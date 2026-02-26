"""Main CLI entry point for fubon-cli."""

import click

from fubon_cli import __version__
from fubon_cli.commands.account import account_group
from fubon_cli.commands.ai import ask_cmd, chat_cmd, config_group
from fubon_cli.commands.auth import auth_group
from fubon_cli.commands.condition import condition_group
from fubon_cli.commands.futopt import futopt_group
from fubon_cli.commands.market import market_group
from fubon_cli.commands.realtime import realtime_group
from fubon_cli.commands.stock import stock_group


def _print_welcome() -> None:
    """Print the fubon-cli welcome / overview screen."""
    border = click.style("  " + "━" * 56, fg="cyan")
    click.echo()
    click.echo(border)
    click.echo(
        "  "
        + click.style("🏦  fubon-cli  ", fg="white", bold=True)
        + click.style(f"v{__version__}", fg="yellow")
        + click.style("  富邦證券命令列工具", fg="white")
    )
    click.echo(border)
    click.echo()
    click.echo(
        click.style("  AI 原生設計", fg="bright_black")
        + click.style(" · ", fg="bright_black")
        + click.style("輸出 JSON", fg="bright_black")
        + click.style(" · ", fg="bright_black")
        + click.style("適合 AI 代理人自動化", fg="bright_black")
    )
    click.echo()

    click.echo(click.style("  指令分類：", fg="white", bold=True))
    trading_cmds = [
        ("login",     "登入 / 登出 / 查詢工作階段"),
        ("stock",     "股票下單（買入 · 賣出 · 改單 · 取消 · 查詢）"),
        ("account",   "帳務查詢（庫存 · 未實現損益 · 交割 · 餘額）"),
        ("market",    "市場資料（報價 · K線 · 快照 · 強弱排行）"),
        ("realtime",  "即時訂閱（WebSocket 串流報價）"),
        ("futopt",    "期貨 / 選擇權（下單 · 庫存 · 委託查詢）"),
        ("condition", "條件單（停利停損 · 追蹤 · 時間分割）"),
    ]
    ai_cmds = [
        ("ask",    "🤖 AI 問答 — 詢問指令建議（one-shot）"),
        ("chat",   "🤖 AI 對話 — 互動式助理，可直接執行指令"),
        ("config", "⚙️  設定 AI API Key、模型等配置"),
    ]
    for name, desc in trading_cmds:
        click.echo(
            "    "
            + click.style(name.ljust(12), fg="green")
            + click.style(desc, fg="white")
        )
    click.echo()
    for name, desc in ai_cmds:
        click.echo(
            "    "
            + click.style(name.ljust(12), fg="yellow")
            + click.style(desc, fg="white")
        )
    click.echo()

    click.echo(click.style("  快速開始：", fg="white", bold=True))
    examples = [
        "fubon login --id A123456789 --password <PW> --cert-path cert.p12",
        "fubon market quote 2330",
        'fubon ask "台積電現在的價格是多少？"',
        "fubon chat                          # 開啟互動 AI 對話",
    ]
    for ex in examples:
        click.echo("    " + click.style(ex, fg="bright_black"))
    click.echo()
    click.echo(
        click.style("  提示：", fg="bright_black")
        + " 使用 "
        + click.style("fubon <指令> --help", fg="cyan")
        + " 查看各指令的詳細說明"
    )
    click.echo()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="fubon-cli")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Fubon Neo Trading CLI - AI agent friendly command-line interface.

    All commands output JSON for easy parsing by AI agents.
    Login first with: fubon login --id <ID> --password <PW> --cert-path <PATH>
    """
    if ctx.invoked_subcommand is None:
        _print_welcome()


cli.add_command(auth_group)
cli.add_command(stock_group)
cli.add_command(account_group)
cli.add_command(market_group)
cli.add_command(realtime_group)
cli.add_command(futopt_group)
cli.add_command(condition_group)
cli.add_command(ask_cmd)
cli.add_command(chat_cmd)
cli.add_command(config_group)


if __name__ == "__main__":
    cli()
