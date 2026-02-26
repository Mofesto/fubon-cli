"""Main CLI entry point for fubon-cli."""

import click

from fubon_cli import __version__
from fubon_cli.commands.account import account_group
from fubon_cli.commands.auth import auth_group
from fubon_cli.commands.market import market_group
from fubon_cli.commands.realtime import realtime_group
from fubon_cli.commands.stock import stock_group


@click.group()
@click.version_option(version=__version__, prog_name="fubon-cli")
def cli():
    """Fubon Neo Trading CLI - AI agent friendly command-line interface.

    All commands output JSON for easy parsing by AI agents.
    Login first with: fubon login --id <ID> --password <PW> --cert-path <PATH>
    """
    pass


cli.add_command(auth_group)
cli.add_command(stock_group)
cli.add_command(account_group)
cli.add_command(market_group)
cli.add_command(realtime_group)


if __name__ == "__main__":
    cli()
