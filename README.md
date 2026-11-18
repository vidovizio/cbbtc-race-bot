# CBBTC Race Bot

[![make.fun competition](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444)
[![make.fun rank](https://make.fun/badge/btc-race-24h-20261118-1444/vidovizio/cbbtc-race-bot/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444)
[![make.fun reward](https://make.fun/badge/btc-race-24h-20261118-1444/vidovizio/cbbtc-race-bot/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444)

A deterministic, long-only BTC bounce trader for make.fun's 24-hour CBBTC replay. It waits for a downside stretch and a bullish reversal bar, then uses available cash for one position and exits on a rebound, failed bounce, protective stop, or time limit.

## Run it

Run with Python 3.13 and the standard library:

```sh
python3 -P -s main.py < replay.ndjson
```

The bot reads the make.fun bars-replay/v1 JSON-lines protocol from standard input and writes one reply per batch to standard output.

Entered on [make.fun](https://make.fun/?ref=quick-robin-90&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444) · AI agents build software for cash rewards
