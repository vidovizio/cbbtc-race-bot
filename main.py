import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars


SYMBOL = "CBBTC"
BUY_FRACTION_BPS = 10000
MAX_SLIPPAGE_BPS = 150
PULLBACK_BARS = 16
PULLBACK_BPS = 60
RECOVERY_BPS = 15
TAKE_PROFIT_BPS = 90
STOP_LOSS_BPS = 60
MAX_HOLD_BARS = 45
COOLDOWN_BARS = 5

closes = []
lows = []
entry_seq = None
last_exit_seq = -10000
pending = None


def on_batch(state, batch):
    global entry_seq, last_exit_seq, pending

    for fill in batch["fills"]:
        if pending is not None and fill["client_id"] == pending:
            if pending.startswith("sell-") and fill["status"] == "filled":
                last_exit_seq = batch["seq"]
            pending = None

    bar = next((b for b in batch["bars"] if b["symbol"] == SYMBOL), None)
    if bar is None:
        return []

    close = int(bar["c"])
    open_price = int(bar["o"])
    low = int(bar["l"])
    closes.append(close)
    lows.append(low)
    if len(closes) > 32:
        del closes[:-32]
        del lows[:-32]

    holding = state.positions.get(SYMBOL)
    if holding is not None:
        if entry_seq is None:
            entry_seq = batch["seq"]
        if pending is not None:
            return []

        value = state.value(SYMBOL, holding.qty, close)
        age = batch["seq"] - entry_seq
        take_profit = value * 10000 >= holding.cost * (10000 + TAKE_PROFIT_BPS)
        stop_loss = value * 10000 <= holding.cost * (10000 - STOP_LOSS_BPS)
        timed_exit = age >= MAX_HOLD_BARS
        failed_rebound = (
            len(closes) >= 3
            and close < closes[-2]
            and closes[-2] < closes[-3]
            and age >= 3
        )
        if take_profit or stop_loss or timed_exit or failed_rebound:
            order_id = f"sell-{batch['seq']}"
            pending = order_id
            return [{
                "side": "sell",
                "client_id": order_id,
                "symbol": SYMBOL,
                "qty": holding.qty,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }]
        return []

    entry_seq = None
    if pending is not None or state.cash < 1_000_000 or batch["seq"] - last_exit_seq <= COOLDOWN_BARS:
        return []

    if len(closes) < PULLBACK_BARS + 1:
        return []

    recent_high = max(closes[-(PULLBACK_BARS + 1):-1])
    pullback_bps = (recent_high - close) * 10000 // recent_high
    local_low = min(lows[-6:])
    recovery_bps = (close - local_low) * 10000 // local_low
    bullish_reversal = close > open_price and close > max(closes[-3:-1])

    if (
        pullback_bps >= PULLBACK_BPS
        and recovery_bps >= RECOVERY_BPS
        and bullish_reversal
        and batch["seq"] < 1430
    ):
        amount = min(state.cash, state.equity * BUY_FRACTION_BPS // 10000)
        if amount >= 1_000_000:
            order_id = f"buy-{batch['seq']}"
            pending = order_id
            return [{
                "side": "buy",
                "client_id": order_id,
                "symbol": SYMBOL,
                "notional_quote_units": amount,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }]

    return []


makefun_bars.run(on_batch)
