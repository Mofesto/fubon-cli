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
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=en">English</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=de">Deutsch</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=es">Español</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=fr">français</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=ja">日本語</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=ko">한국어</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=pt">Português</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=ru">Русский</a> |
  <a href="https://www.readme-i18n.com/Mofesto/fubon-cli?lang=zh">簡體中文</a>
</div>

富邦證券 Fubon Neo Trading API（v2.2.8）的命令列工具，專為 AI 代理自動化設計。

所有指令皆輸出結構化 JSON 到 stdout，方便 AI 代理、腳本或管線解析與接續處理。

## 環境需求

- Python 3.8 - 3.13
- Fubon Neo SDK wheel 檔（`fubon_neo-2.2.8-cp37-abi3-win_amd64.whl`）
- 具電子憑證的富邦證券帳戶


## 安裝

```bash
# 從 PyPI 安裝（建議）
pip install fubon-cli

# 或從原始碼安裝（開發用）
pip install -e .
```

# Star 歷史

[![Star History Chart](https://api.star-history.com/svg?repos=Mofesto/fubon-cli&type=date&legend=top-left)](https://www.star-history.com/#Mofesto/fubon-cli&type=date&legend=top-left)


## 快速開始

```bash
# 1. 登入（儲存 session 供後續指令使用）
fubon login --id "A123456789" --password "yourpass" --cert-path "/path/to/cert.pfx" --cert-password "certpass"

# 或使用 API Key 登入（需 fubon_neo >= 2.2.7）
fubon login --id "A123456789" --api-key "your_api_key" --cert-path "/path/to/cert.pfx" --cert-password "certpass"

# 2. 取得報價
fubon market quote 2330

# 3. 下買單
fubon stock buy 2330 1000 --price 580

# 4. 查詢委託
fubon stock orders

# 5. 查詢庫存
fubon account inventory
```

## 指令參考

### 認證

```bash
# 登入
fubon login --id <ID> --password <PW> --cert-path <PATH> [--cert-password <PW>]
# API Key 登入（fubon_neo >= 2.2.7）
fubon login --id <ID> --api-key <KEY> --cert-path <PATH>

# 查詢登入狀態
fubon login status

# 登出（清除儲存的認證）
fubon login logout
```

`fubon login status` 的輸出會包含 `login_type` 欄位（`password` 或 `apikey`），用以表示目前的登入方式。

### 股票交易

```bash
# 買進（限價）
fubon stock buy <SYMBOL> <QUANTITY> --price <PRICE>

# 以跌停價買進
fubon stock buy 2881 2000 --price-type limit-down

# 以 IOC（立即成交或取消）買進
fubon stock buy 2330 500 --price 580 --time-in-force IOC

# 賣出
fubon stock sell <SYMBOL> <QUANTITY> --price <PRICE>

# 市價賣出
fubon stock sell 2330 1000 --price-type market

# 當沖委託
fubon stock buy 2330 1000 --price 580 --order-type day-trade

# 零股委託
fubon stock buy 2330 50 --price 580 --market-type intraday-odd

# 查詢委託
fubon stock orders

# 取消委託
fubon stock cancel <ORDER_NO>

# 改價
fubon stock modify-price <ORDER_NO> <NEW_PRICE>

# 改量
fubon stock modify-quantity <ORDER_NO> <NEW_QUANTITY>
```

**委託選項：**

| 參數 | 值 | 預設 |
|--------|--------|---------|
| `--price-type` | `limit`, `market`, `limit-up`, `limit-down`, `reference` | `limit` |
| `--time-in-force` | `ROD`, `IOC`, `FOK` | `ROD` |
| `--order-type` | `stock`, `margin`, `short`, `sbl`, `day-trade` | `stock` |
| `--market-type` | `common`, `odd`, `intraday-odd`, `fixing`, `emg`, `emg-odd` | `common` |

### 帳務查詢

```bash
# 查詢股票庫存（持倉）
fubon account inventory

# 查詢未實現損益
fubon account unrealized

# 查詢當日交割資訊
fubon account settlement

# 查詢昨日交割資訊
fubon account settlement --range 1d

# 查詢個股融資融券額度
fubon account margin-quota 2330
```

### 市場資料

```bash
# 即時報價
fubon market quote 2330

# 個股資訊
fubon market ticker 2330

# 盤中 K 線（預設 5 分鐘）
fubon market candles 2330
fubon market candles 2330 --timeframe 15

# 盤中成交明細
fubon market trades 2330 --limit 50

# 價量分布
fubon market volumes 2330

# 大盤快照
fubon market snapshot TSE

# 漲幅排行
fubon market movers TSE --direction up --change percent

# 跌幅排行
fubon market movers OTC --direction down

# 成交量排行
fubon market actives TSE --trade volume

# 歷史 K 線
fubon market history 2330 --from 2024-01-01 --to 2024-06-30
fubon market history 0050 --timeframe W --adjusted

# 52 週統計
fubon market stats 2330

# 列出所有股票代碼
fubon market tickers --type EQUITY --exchange TWSE
```

### 即時串流

```bash
# 訂閱即時成交（JSONL 串流）
fubon realtime subscribe 2330

# 訂閱聚合資料
fubon realtime subscribe 2330 --channel aggregates

# 監聽委託/成交回報（JSONL 串流）
fubon realtime callbacks
```

## JSON 輸出格式

所有指令皆輸出一致的 JSON 結構：

```json
{
  "success": true,
  "data": { ... }
}
```

錯誤時：

```json
{
  "success": false,
  "error": "Error description"
}
```

串流指令（`realtime subscribe`, `realtime callbacks`）每行輸出一個 JSON 物件（JSONL 格式）。

## AI 助理

**fubon-cli** 內置 AI 助理功能，可以通過自然語言與 CLI 互動，自動生成和執行交易指令。

### 設定 AI

先安裝 OpenAI 支援：

```bash
pip install fubon-cli[ai]
# 或
pip install openai
```

再設定 OpenAI API Key：

```bash
# 方式 1：設定 OpenAI API Key
fubon config set openai-key sk-proj-...

# 方式 2：使用環境變數
export OPENAI_API_KEY=sk-proj-...
export FUBON_AI_KEY=sk-proj-...   # 或這個

# 方式 3：查看目前配置
fubon config show
```

### 一次性查詢（fubon ask）

快速詢問 AI 並取得命令建議：

```bash
# 基本詢問
fubon ask "台積電(2330)的目前報價是多少？"

# 詢問並執行建議的命令（互動確認）
fubon ask "如何以市價買入 2330 一張？" --execute

# 縮寫
fubon ask "幫我查詢帳戶庫存" -x

# 用於 AI 代理（JSON 輸出）
fubon ask "取得 2330 的即時報價" --json-output
```

輸出格式（`--json-output`）：

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

### 互動對話模式（fubon chat）

進入 AI 聊天 REPL，可連續對話並執行命令：

```bash
fubon chat
```

進入後的內建指令：

```
/run      — 執行 AI 最新建議的指令（帶確認）
/clear    — 清除對話記錄，重新開始
exit      — 離開
```

示例：

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
- **指令生成** — 自動從回應中擷取 `fubon` 指令
- **安全確認** — 交易指令（買、賣、取消等）需要明確確認
- **完整 CLI 知識** — AI 瞭解所有 fubon 指令語法和選項
- **多模型支援** — 預設使用 `gpt-4o-mini`，可切換為 `gpt-4o` 等

### 設定 AI 模型

```bash
# 查看目前模型
fubon config show

# 改為 GPT-4O
fubon config set ai-model gpt-4o

# 改為其他模型
fubon config set ai-model gpt-4-turbo
```

## AI 代理整合

此 CLI 針對 AI 代理的交易流程自動化設計：

1. **無狀態執行**：每個指令都是獨立呼叫，登入憑證會儲存在 `~/.fubon-cli-session.json`。
2. **JSON 輸出**：所有回應皆為可機器解析的 JSON。
3. **錯誤代碼**：失敗時返回非 0 狀態碼，錯誤細節在 JSON 中。
4. **串流**：即時資料以 JSONL 持續輸出，便於監控。

代理流程示例：

```bash
# 查詢持倉
positions=$(fubon account inventory)

# 取得報價
quote=$(fubon market quote 2330)

# 依代理邏輯下單
fubon stock buy 2330 1000 --price 580

# 監控成交回報
fubon realtime callbacks
```

## 授權

MIT
