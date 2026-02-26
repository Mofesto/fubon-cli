"""AI assistant and config commands for fubon-cli.

Provides:
  fubon ask "<question>"  — One-shot AI Q&A with command suggestions
  fubon chat              — Interactive AI chat REPL with command execution
  fubon config set/show   — Manage API key and model settings
"""

import json
import os
import re
import subprocess
import sys

import click

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".fubon-cli-config.json")

# Commands that mutate account state — always require explicit confirmation
_TRADING_KEYWORDS = {
    "stock buy",
    "stock sell",
    "stock modify",
    "stock cancel",
    "futopt buy",
    "futopt sell",
    "futopt modify",
    "futopt cancel",
    "condition cancel",
}

FUBON_COMMANDS_REFERENCE = """\
## 認證 (Authentication)
fubon login --id <ID> --password <PW> --cert-path <PATH> [--cert-password <PW>]
fubon login logout
fubon login status

## 股票交易 (Stock Trading)
fubon stock buy <SYMBOL> <QUANTITY> --price <PRICE>
    options: --price-type [limit|market|limit-up|limit-down|reference]
             --time-in-force [ROD|IOC|FOK]
             --order-type [stock|margin|short|sbl|day-trade]
             --market-type [common|odd|intraday-odd|fixing|emg]
             --account-index <N>
fubon stock sell <SYMBOL> <QUANTITY> --price <PRICE>  (same options as buy)
fubon stock modify <ORDER_ID> [--price <PRICE>] [--quantity <QTY>]
fubon stock cancel <ORDER_ID> [--account-index <N>]
fubon stock orders [--filled] [--account-index <N>]

## 帳務查詢 (Account)
fubon account inventory   [--account-index <N>]
fubon account unrealized  [--account-index <N>]
fubon account settlement  [--account-index <N>]
fubon account balance     [--account-index <N>]

## 市場資料 (Market Data)
fubon market quote <SYMBOL> [--odd-lot]
fubon market ticker <SYMBOL> [--odd-lot]
fubon market candles <SYMBOL> [--from YYYY-MM-DD] [--to YYYY-MM-DD]
    [--timeframe 1d|1h|30m|15m|5m|1m]
fubon market snapshot <SYMBOL>
fubon market movers  [--direction up|down] [--market TSE|OTC] [--limit 20]
fubon market actives [--market TSE|OTC] [--limit 20]

## 即時訂閱 (Realtime WebSocket)
fubon realtime subscribe <SYMBOL> [--channel trades|aggregates|candles]

## 期貨/選擇權 (Futures / Options)
fubon futopt buy <SYMBOL> <LOT> --price <PRICE>
    options: --price-type [limit|market|market-range]
             --time-in-force [ROD|IOC|FOK]
fubon futopt sell <SYMBOL> <LOT> --price <PRICE>  (same options)
fubon futopt modify <ORDER_ID> [--price <PRICE>] [--quantity <QTY>]
fubon futopt cancel <ORDER_ID>
fubon futopt orders      [--filled]
fubon futopt inventories

## 條件單 (Condition Orders)
fubon condition list     [--futopt] [--account-index <N>]
fubon condition single   [many options — see fubon condition single --help]
fubon condition multi    [many options]
fubon condition tpsl     [many options]
fubon condition trailing [many options]
fubon condition timeslice [many options]
fubon condition daytrade [many options]
fubon condition modify   <ORDER_ID> [options]
fubon condition cancel   <ORDER_ID> [--futopt]

## AI & 設定
fubon ask "<question>"    — 詢問 AI (one-shot)
fubon chat                — 互動對話模式
fubon config set <key> <value>
fubon config show
"""

SYSTEM_PROMPT = (
    "你是富邦 CLI 助理（Fubon CLI Assistant），一個專為 fubon-cli 交易命令列工具設計的 AI 助手。"
    "你幫助用戶查詢台灣股市資料、管理富邦證券帳戶，並提供投資分析建議。\n\n"
    "可用的 fubon CLI 指令列表：\n"
    + FUBON_COMMANDS_REFERENCE
    + "\n\n"
    "回答原則：\n"
    "1. 使用繁體中文回答\n"
    "2. 提供精確的 fubon 指令，並放在 ```bash 程式碼區塊中\n"
    "3. 交易指令（buy/sell）務必提醒風險與確認\n"
    "4. 如需多個步驟，依序編號說明\n"
    "5. 簡潔直接，不要囉嗦\n"
    "6. 所有 fubon 指令輸出 JSON，可用 | python -m json.tool 美化\n"
)


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------


def load_config() -> dict:
    """Load ~/.fubon-cli-config.json, return empty dict on error."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(data: dict) -> None:
    """Write config to disk; restrict permissions on Unix."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    if os.name != "nt":
        os.chmod(CONFIG_FILE, 0o600)


def _get_api_key() -> "str | None":
    config = load_config()
    return (
        config.get("openai_api_key")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("FUBON_AI_KEY")
    )


def _get_model() -> str:
    return load_config().get("ai_model", "gpt-4o-mini")


def _has_openai() -> bool:
    try:
        import openai  # noqa: F401

        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# AI helpers
# ---------------------------------------------------------------------------


def _call_ai(messages: list) -> str:
    """Call OpenAI API and return assistant message content."""
    from openai import OpenAI

    client = OpenAI(api_key=_get_api_key())
    response = client.chat.completions.create(
        model=_get_model(),
        messages=messages,
        max_tokens=2048,
        temperature=0.3,
    )
    return response.choices[0].message.content


def _extract_fubon_commands(text: str) -> list:
    """Return list of 'fubon ...' commands found in AI response text."""
    commands = []
    # Commands inside fenced code blocks
    code_blocks = re.findall(
        r"```(?:bash|sh|shell|cmd|powershell|zsh)?\n(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    for block in code_blocks:
        for line in block.strip().splitlines():
            line = line.strip().lstrip("$ ")
            if line.startswith("fubon ") and line not in commands:
                commands.append(line)
    # Inline backtick commands
    for cmd in re.findall(r"`(fubon [^`\n]+)`", text):
        cmd = cmd.strip()
        if cmd not in commands:
            commands.append(cmd)
    return commands


def _is_trading_command(cmd: str) -> bool:
    """Return True if cmd is a state-mutating trading command."""
    return any(kw in cmd for kw in _TRADING_KEYWORDS)


def _run_fubon_command(cmd: str) -> str:
    """Execute a fubon shell command and return pretty-printed output."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    raw = (result.stdout or result.stderr or "").strip()
    try:
        return json.dumps(json.loads(raw), indent=2, ensure_ascii=False)
    except Exception:
        return raw


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

_DIVIDER = click.style("  " + "─" * 52, fg="bright_black")


def _print_ai_response(text: str) -> None:
    """Render AI markdown-ish response to terminal with basic colour."""
    click.echo()
    in_code = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
            click.echo(_DIVIDER)
        elif in_code:
            click.echo(click.style("    " + line, fg="green"))
        elif re.match(r"^#{1,3} ", line):
            click.echo(click.style("  " + line, fg="cyan", bold=True))
        else:
            click.echo("  " + line)
    click.echo()


def _offer_to_execute(commands: list) -> None:
    """Interactively ask user to confirm and run each extracted command."""
    if not commands:
        return

    click.echo(click.style("\n  💡 AI 建議的指令：", fg="yellow", bold=True))
    for i, cmd in enumerate(commands, 1):
        tag = (
            click.style(" ⚠  [交易]", fg="red")
            if _is_trading_command(cmd)
            else click.style(" ✦", fg="cyan")
        )
        click.echo(f"  {i}.{tag} {click.style(cmd, fg='green')}")
    click.echo()

    for cmd in commands:
        if _is_trading_command(cmd):
            prompt_text = click.style(
                f"  執行交易指令？此操作會影響帳戶！\n  [{cmd}]\n  請輸入 yes 確認",
                fg="red",
            )
            answer = click.prompt(prompt_text, default="no")
            confirmed = answer.strip().lower() == "yes"
        else:
            prompt_text = click.style(f"  執行 [{cmd}]?", fg="yellow")
            answer = click.prompt(prompt_text, default="n")
            confirmed = answer.strip().lower() in ("y", "yes")

        if confirmed:
            click.echo(click.style(f"  ▶ {cmd}", fg="cyan"))
            output = _run_fubon_command(cmd)
            click.echo(click.style(output, fg="white"))
        else:
            click.echo(click.style("  （跳過）", fg="bright_black"))
        click.echo()


def _print_chat_banner() -> None:
    """Print the chat mode welcome banner."""
    border = click.style("  " + "━" * 54, fg="cyan")
    click.echo()
    click.echo(border)
    click.echo(
        "  "
        + click.style("🤖  富邦 AI 助理", fg="white", bold=True)
        + click.style("  ─  互動對話模式", fg="cyan")
    )
    click.echo(border)
    click.echo()
    click.echo("  可詢問任何 fubon CLI 問題，AI 可建議並協助執行指令。")
    click.echo()
    click.echo(click.style("  內建指令：", fg="bright_black"))
    click.echo(
        "    " + click.style("/run   ", fg="green") + "— 執行 AI 最新建議的指令"
    )
    click.echo(
        "    " + click.style("/clear ", fg="green") + "— 清除對話記錄，重新開始"
    )
    click.echo(
        "    " + click.style("exit   ", fg="green") + "— 離開對話"
    )
    click.echo()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@click.command("ask")
@click.argument("question")
@click.option(
    "--execute", "-x", is_flag=True, help="互動方式確認並執行 AI 建議的指令"
)
@click.option(
    "--json-output",
    "json_out",
    is_flag=True,
    help="以 JSON 輸出（AI 代理人模式）",
)
def ask_cmd(question: str, execute: bool, json_out: bool) -> None:
    """向 AI 詢問 fubon CLI 相關問題，取得指令建議。

    \b
    範例：
      fubon ask "台積電現在的報價是多少？"
      fubon ask "如何以市價買入2330一張？" --execute
      fubon ask "幫我查詢帳戶庫存" -x
    """
    if not _has_openai():
        msg = "openai 套件未安裝。請執行：pip install openai  （或 pip install fubon-cli[ai]）"
        if json_out:
            click.echo(json.dumps({"success": False, "error": msg}))
        else:
            click.echo(click.style("❌ " + msg, fg="red"))
        sys.exit(1)

    if not _get_api_key():
        msg = (
            "未設定 AI API Key。\n"
            "請執行：fubon config set openai-key <YOUR_OPENAI_API_KEY>\n"
            "或設定環境變數：OPENAI_API_KEY=<YOUR_KEY>"
        )
        if json_out:
            click.echo(json.dumps({"success": False, "error": msg}))
        else:
            click.echo(click.style("❌ " + msg, fg="red"))
        sys.exit(1)

    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        if not json_out:
            click.echo(click.style("  ⋯ 正在思考...", fg="bright_black"))

        answer = _call_ai(messages)

        if json_out:
            click.echo(
                json.dumps(
                    {
                        "success": True,
                        "question": question,
                        "answer": answer,
                        "suggested_commands": _extract_fubon_commands(answer),
                    },
                    ensure_ascii=False,
                )
            )
            return

        _print_ai_response(answer)

        if execute:
            _offer_to_execute(_extract_fubon_commands(answer))

    except Exception as e:
        if json_out:
            click.echo(json.dumps({"success": False, "error": str(e)}))
        else:
            click.echo(click.style(f"❌ AI 錯誤：{e}", fg="red"))
        sys.exit(1)


@click.command("chat")
def chat_cmd() -> None:
    """開啟 AI 互動對話模式，可即時詢問並執行 fubon 指令。

    \b
    內建指令：
      /run    執行 AI 最新建議的指令（帶確認）
      /clear  清除對話記錄
      exit    離開
    """
    if not _has_openai():
        click.echo(click.style("❌ openai 套件未安裝。請執行：pip install openai", fg="red"))
        sys.exit(1)

    if not _get_api_key():
        click.echo(click.style("❌ 未設定 AI API Key。", fg="red"))
        click.echo("請執行：" + click.style(" fubon config set openai-key <YOUR_KEY>", fg="green"))
        sys.exit(1)

    _print_chat_banner()

    messages: list = [{"role": "system", "content": SYSTEM_PROMPT}]
    last_commands: list = []

    while True:
        try:
            user_input = click.prompt(
                click.style("你", fg="cyan", bold=True),
                prompt_suffix=click.style(" ❯ ", fg="bright_black"),
            )
        except (click.Abort, EOFError, KeyboardInterrupt):
            click.echo(click.style("\n  再見！", fg="cyan"))
            break

        user_input = user_input.strip()
        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q", "bye", "掰掰"):
            click.echo(click.style("  再見！", fg="cyan"))
            break

        if user_input.lower() == "/clear":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            last_commands = []
            click.echo(click.style("  ✓ 對話記錄已清除", fg="green"))
            continue

        if user_input.lower() == "/run":
            if last_commands:
                _offer_to_execute(last_commands)
            else:
                click.echo(click.style("  （目前沒有可執行的指令）", fg="bright_black"))
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            click.echo(click.style("  ⋯", fg="bright_black"), nl=False)
            answer = _call_ai(messages)
            click.echo("\r   \r", nl=False)  # clear the spinner

            messages.append({"role": "assistant", "content": answer})

            click.echo(
                "\n  "
                + click.style("富邦助理", fg="yellow", bold=True)
                + click.style(" ❯ ", fg="bright_black")
            )
            _print_ai_response(answer)

            last_commands = _extract_fubon_commands(answer)
            if last_commands:
                count = len(last_commands)
                click.echo(
                    click.style(
                        f"  💡 有 {count} 個建議指令，輸入 /run 執行",
                        fg="yellow",
                    )
                )
            click.echo()

        except KeyboardInterrupt:
            click.echo(click.style("  （已中斷）", fg="bright_black"))
            if messages and messages[-1]["role"] == "user":
                messages.pop()
        except Exception as e:
            click.echo(click.style(f"\n  ❌ 錯誤：{e}", fg="red"))
            if messages and messages[-1]["role"] == "user":
                messages.pop()


# ---------------------------------------------------------------------------
# Config command group
# ---------------------------------------------------------------------------

_KEY_MAP = {
    "openai-key": "openai_api_key",
    "ai-key": "openai_api_key",
    "ai-model": "ai_model",
    "model": "ai_model",
}


@click.group("config")
def config_group() -> None:
    """設定 fubon-cli 配置（AI Key、模型等）。"""
    pass


@config_group.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """設定配置項目。

    \b
    可設定項目：
      openai-key   OpenAI API Key
      ai-model     AI 模型（預設：gpt-4o-mini）

    \b
    範例：
      fubon config set openai-key sk-proj-...
      fubon config set ai-model gpt-4o
    """
    internal_key = _KEY_MAP.get(key.lower())
    if not internal_key:
        click.echo(click.style(f"❌ 未知的配置項目：{key}", fg="red"))
        click.echo("可設定：" + ", ".join(_KEY_MAP))
        sys.exit(1)

    cfg = load_config()
    cfg[internal_key] = value
    save_config(cfg)

    # Mask keys for display
    display = f"{value[:8]}..." if "key" in internal_key else value
    click.echo(click.style(f"  ✓ {key} = {display}", fg="green"))


@config_group.command("show")
def config_show() -> None:
    """顯示目前的所有配置。"""
    cfg = load_config()
    if not cfg:
        click.echo(click.style("  （無配置，使用環境變數或預設值）", fg="bright_black"))
        return

    click.echo()
    click.echo(click.style("  fubon-cli 配置：", fg="cyan", bold=True))
    for k, v in cfg.items():
        display = f"{str(v)[:8]}..." if "key" in k.lower() else str(v)
        click.echo(f"    {click.style(k, fg='green')}: {display}")
    click.echo()


@config_group.command("get")
@click.argument("key")
def config_get(key: str) -> None:
    """取得特定配置項目的值。"""
    cfg = load_config()
    internal_key = _KEY_MAP.get(key.lower(), key.lower().replace("-", "_"))
    value = cfg.get(internal_key)
    if value is None:
        click.echo(click.style(f"  {key}: （未設定）", fg="bright_black"))
    elif "key" in internal_key.lower():
        click.echo(f"  {key}: {str(value)[:8]}...")
    else:
        click.echo(f"  {key}: {value}")
