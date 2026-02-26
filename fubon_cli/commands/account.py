"""Account query commands: inventory, balance, settlement, unrealized P&L."""

import click

from fubon_cli.core import get_account, get_sdk_and_accounts, obj_to_dict, output


@click.group("account")
def account_group():
    """Account queries: inventory, unrealized P&L, settlement."""
    pass


@account_group.command("inventory")
@click.option("--account-index", type=int, default=0, help="Account index")
def inventory(account_index):
    r"""Query stock inventory (positions).

    \b
    Example:
      fubon account inventory
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.accounting.inventories(acc)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@account_group.command("unrealized")
@click.option("--account-index", type=int, default=0, help="Account index")
def unrealized(account_index):
    r"""Query unrealized gains and losses.

    \b
    Example:
      fubon account unrealized
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.accounting.unrealized_gains_and_loses(acc)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@account_group.command("settlement")
@click.option(
    "--range",
    "date_range",
    type=click.Choice(["0d", "1d", "2d", "3d"]),
    default="0d",
    help="Query range: 0d=today, 1d=yesterday, etc.",
)
@click.option("--account-index", type=int, default=0, help="Account index")
def settlement(date_range, account_index):
    r"""Query settlement information.

    \b
    Examples:
      fubon account settlement
      fubon account settlement --range 1d
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.accounting.query_settlement(acc, date_range)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@account_group.command("margin-quota")
@click.argument("symbol")
@click.option("--account-index", type=int, default=0, help="Account index")
def margin_quota(symbol, account_index):
    r"""Query margin/short selling quota for a stock.

    \b
    Example:
      fubon account margin-quota 2330
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.accounting.margin_quota(acc, symbol)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@account_group.command("bank-balance")
@click.option("--account-index", type=int, default=0, help="Account index")
def bank_balance(account_index):
    r"""Query bank account balance (TWD).

    \b
    Example:
      fubon account bank-balance
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.accounting.bank_remain(acc)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@account_group.command("maintenance")
@click.option("--account-index", type=int, default=0, help="Account index")
def maintenance(account_index):
    r"""Query margin maintenance ratio.

    \b
    Example:
      fubon account maintenance
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.accounting.maintenance(acc)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@account_group.command("realized")
@click.option("--account-index", type=int, default=0, help="Account index")
def realized(account_index):
    r"""Query realized profit and loss detail.

    \b
    Example:
      fubon account realized
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.accounting.realized_profit_loss(acc)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@account_group.command("realized-summary")
@click.option("--account-index", type=int, default=0, help="Account index")
def realized_summary(account_index):
    r"""Query realized profit and loss summary.

    \b
    Example:
      fubon account realized-summary
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.accounting.realized_profit_loss_summary(acc)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@account_group.command("day-trade-quota")
@click.option("--account-index", type=int, default=0, help="Account index")
def day_trade_quota(account_index):
    r"""Query day trade and short sell quota.

    \b
    Example:
      fubon account day-trade-quota
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.stock.day_trade_quota(acc)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))
