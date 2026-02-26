# fubon-cli

Command-line interface for the Fubon Neo Trading API (v2.2.8), designed for AI agent automation.

All commands output structured JSON to stdout, making it straightforward for AI agents, scripts, or pipelines to parse and act on results.

## Prerequisites

- Python 3.8 - 3.13
- Fubon Neo SDK wheel file (`fubon_neo-2.2.8-cp37-abi3-win_amd64.whl`)
- Fubon securities account with electronic certificate

## Installation

```bash
# Install the Fubon Neo SDK
pip install fubon_neo-2.2.8-cp37-abi3-win_amd64.whl

# Install fubon-cli
pip install -e .
```

## Quick Start

```bash
# 1. Login (saves session for subsequent commands)
fubon login --id "A123456789" --password "yourpass" --cert-path "/path/to/cert.pfx" --cert-password "certpass"

# 2. Get a stock quote
fubon market quote 2330

# 3. Place a buy order
fubon stock buy 2330 1000 --price 580

# 4. Check your orders
fubon stock orders

# 5. Check your inventory
fubon account inventory
```

## Command Reference

### Authentication

```bash
# Login
fubon login --id <ID> --password <PW> --cert-path <PATH> [--cert-password <PW>]

# Check login status
fubon login status

# Logout (clear saved credentials)
fubon login logout
```

### Stock Trading

```bash
# Buy stock (limit order)
fubon stock buy <SYMBOL> <QUANTITY> --price <PRICE>

# Buy at limit-down price
fubon stock buy 2881 2000 --price-type limit-down

# Buy with IOC (Immediate or Cancel)
fubon stock buy 2330 500 --price 580 --time-in-force IOC

# Sell stock
fubon stock sell <SYMBOL> <QUANTITY> --price <PRICE>

# Market order sell
fubon stock sell 2330 1000 --price-type market

# Day trade order
fubon stock buy 2330 1000 --price 580 --order-type day-trade

# Odd-lot order
fubon stock buy 2330 50 --price 580 --market-type intraday-odd

# Query current orders
fubon stock orders

# Cancel an order
fubon stock cancel <ORDER_NO>

# Modify order price
fubon stock modify-price <ORDER_NO> <NEW_PRICE>

# Modify order quantity
fubon stock modify-quantity <ORDER_NO> <NEW_QUANTITY>
```

**Order Options:**

| Option | Values | Default |
|--------|--------|---------|
| `--price-type` | `limit`, `market`, `limit-up`, `limit-down`, `reference` | `limit` |
| `--time-in-force` | `ROD`, `IOC`, `FOK` | `ROD` |
| `--order-type` | `stock`, `margin`, `short`, `sbl`, `day-trade` | `stock` |
| `--market-type` | `common`, `odd`, `intraday-odd`, `fixing`, `emg`, `emg-odd` | `common` |

### Account Queries

```bash
# Query stock inventory (positions)
fubon account inventory

# Query unrealized gains/losses
fubon account unrealized

# Query settlement info (today)
fubon account settlement

# Query settlement for yesterday
fubon account settlement --range 1d

# Query margin/short quota for a stock
fubon account margin-quota 2330
```

### Market Data

```bash
# Realtime quote
fubon market quote 2330

# Stock ticker info
fubon market ticker 2330

# Intraday K-line (5-min default)
fubon market candles 2330
fubon market candles 2330 --timeframe 15

# Intraday trade details
fubon market trades 2330 --limit 50

# Price-volume distribution
fubon market volumes 2330

# Market snapshot
fubon market snapshot TSE

# Top movers (gainers)
fubon market movers TSE --direction up --change percent

# Top movers (losers)
fubon market movers OTC --direction down

# Most active stocks
fubon market actives TSE --trade volume

# Historical K-line
fubon market history 2330 --from 2024-01-01 --to 2024-06-30
fubon market history 0050 --timeframe W --adjusted

# 52-week statistics
fubon market stats 2330

# List all equity tickers
fubon market tickers --type EQUITY --exchange TWSE
```

### Realtime Streaming

```bash
# Subscribe to realtime trade data (streams JSON lines)
fubon realtime subscribe 2330

# Subscribe to aggregated data
fubon realtime subscribe 2330 --channel aggregates

# Listen to order/fill callbacks (streams JSON lines)
fubon realtime callbacks
```

## JSON Output Format

All commands output JSON with a consistent structure:

```json
{
  "success": true,
  "data": { ... }
}
```

On error:

```json
{
  "success": false,
  "error": "Error description"
}
```

Streaming commands (`realtime subscribe`, `realtime callbacks`) output one JSON object per line (JSONL format).

## AI Agent Integration

This CLI is designed for AI agents to automate trading workflows:

1. **Stateless execution**: Each command is a standalone invocation. Login credentials are persisted in `~/.fubon-cli-session.json`.
2. **JSON output**: All responses are machine-parseable JSON.
3. **Error codes**: Non-zero exit codes on failure, with error details in JSON.
4. **Streaming**: Realtime data streams as JSONL for continuous monitoring.

Example agent workflow:

```bash
# Check current positions
positions=$(fubon account inventory)

# Get a quote
quote=$(fubon market quote 2330)

# Place an order based on agent logic
fubon stock buy 2330 1000 --price 580

# Monitor fills
fubon realtime callbacks
```

## License

MIT
