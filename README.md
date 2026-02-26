# fubon-cli

<div align="center" style="line-height: 1;">
  <a href="https://pypi.org/project/fubon-cli/" target="_blank"><img alt="PyPI version" src="https://img.shields.io/pypi/v/fubon-cli.svg"/></a>
  <a href="https://codecov.io/gh/Mofesto/fubon-cli" target="_blank"><img alt="codecov" src="https://codecov.io/gh/Mofesto/fubon-cli/branch/main/graph/badge.svg"/></a>
</div>

<p align="center">
  <img src="assets/image.png" style="width: 60%; height: auto;">
</p>

<div align="center">
  <!-- Keep these links. Translations will automatically update with the README. -->
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=de">Deutsch</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=es">Español</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=fr">français</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=ja">日本語</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=ko">한국어</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=pt">Português</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=ru">Русский</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=zh">中文</a>
</div>

Command-line interface for the Fubon Neo Trading API (v2.2.8), designed for AI agent automation.

All commands output structured JSON to stdout, making it straightforward for AI agents, scripts, or pipelines to parse and act on results.

## Prerequisites

- Python 3.8 - 3.13
- Fubon Neo SDK wheel file (`fubon_neo-2.2.8-cp37-abi3-win_amd64.whl`)
- Fubon securities account with electronic certificate


## Installation

```bash
# Install from PyPI (recommended)
pip install fubon-cli

# Or, install from source (for development)
pip install -e .
```

# Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Mofesto/fubon-cli&type=date&legend=top-left)](https://www.star-history.com/#Mofesto/fubon-cli&type=date&legend=top-left)


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

## AI Assistant

**fubon-cli** 內置 AI 助理功能，可以通過自然語言與 CLI 互動，自動生成和執行交易指令。

### Setup (設定 AI)

首先安裝 OpenAI 支持：

```bash
pip install fubon-cli[ai]
# 或
pip install openai
```

然後設定 OpenAI API Key：

```bash
# 方式 1：設定 OpenAI API 密鑰
fubon config set openai-key sk-proj-...

# 方式 2：使用環境變數
export OPENAI_API_KEY=sk-proj-...
export FUBON_AI_KEY=sk-proj-...   # 或這個

# 方式 3：查看目前配置
fubon config show
```

### 一次性查詢 (fubon ask)

快速詢問 AI 並取得命令建議：

```bash
# 基本詢問
fubon ask "台積電(2330)的目前報價是多少？"

# 詢問並執行建議的命令（互動確認）
fubon ask "如何以市價買入 2330 一張？" --execute

# 縮寫
fubon ask "幫我查詢帳戶庫存" -x

# 用於 AI 代理人（JSON 輸出）
fubon ask "取得 2330 的即時報價" --json-output
```

輸出格式（--json-output）：

```json
{
  "success": true,
  "question": "台積電(2330)的目前報價是多少？",
  "answer": "根據 Fubon Neo SDK...",
  "suggested_commands": [
    "fubon market quote 2330"
  ]
}
```

### 互動對話模式 (fubon chat)

進入 AI 聊天 REPL，可連續對話和執行命令：

```bash
fubon chat
```

進入後的內建指令：

```
/run      — 執行 AI 最新建議的指令（帶確認）
/clear    — 清除對話記錄，重新開始
exit      — 離開
```

例子：

```
你 ❯ 台積電現在的股價多少？
富邦助理 ❯ 為了幫您查詢台積電(2330)的目前股價...
[AI 回覆 + 建議指令]

💡 有 1 個建議指令，輸入 /run 執行
你 ❯ /run
  1. ✦ fubon market quote 2330
  執行 [fubon market quote 2330]? (y|n): y
  ▶ fubon market quote 2330
  {
    "success": true,
    "data": {
      "symbol": "2330",
      "price": 995.0,
      ...
    }
  }

你 ❯ 幫我買 5 張零股
富邦助理 ❯ 為了買進 2330 的零股...
  ⚠ [交易] fubon stock buy 2330 50 --price 990
  執行交易指令？此操作會影響帳戶！
  [fubon stock buy 2330 50 --price 990]
  請輸入 yes 確認
```

### AI 助理特性

- **繁體中文對話** — 自動回應繁體中文
- **命令生成** — 自動從回應中提取 `fubon` 命令
- **安全確認** — 交易命令（買、賣、取消等）需要顯式確認
- **完整 CLI 知識** — AI 瞭解所有 fubon 指令語法和選項
- **多模型支持** — 預設使用 `gpt-4o-mini`，可切換為 `gpt-4o` 等

### 配置 AI 模型

```bash
# 查看目前模型
fubon config show

# 更改為 GPT-4O
fubon config set ai-model gpt-4o

# 更改為其他模型
fubon config set ai-model gpt-4-turbo
```

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
