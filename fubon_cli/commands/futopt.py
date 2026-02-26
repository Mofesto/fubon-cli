"""Futures/Options trading commands: buy, sell, modify, cancel, orders, inventories."""

import sys

import click

from fubon_cli.core import get_account, get_sdk_and_accounts, obj_to_dict, output


@click.group("futopt")
def futopt_group():
    """Futures/options trading: buy, sell, modify, cancel orders, inventories."""
    pass


@futopt_group.command("buy")
@click.argument("symbol")
@click.argument("lot", type=int)
@click.option("--price", type=str, default=None, help="Limit price. Omit for market orders.")
@click.option(
    "--price-type",
    type=click.Choice(["limit", "market", "market-range"]),
    default="limit",
    help="Price type",
)
@click.option(
    "--time-in-force",
    "tif",
    type=click.Choice(["ROD", "IOC", "FOK"]),
    default="ROD",
    help="Time in force",
)
@click.option(
    "--order-type",
    "otype",
    type=click.Choice(["new", "cover", "auto"]),
    default="new",
    help="Order type: new position, cover (close), or auto",
)
@click.option(
    "--market-type",
    "mtype",
    type=click.Choice(["future", "future-night", "option", "option-night"]),
    default="future",
    help="Market type",
)
@click.option("--account-index", type=int, default=0, help="Account index (default: 0)")
def futopt_buy(symbol, lot, price, price_type, tif, otype, mtype, account_index):
    """Place a futures/options BUY order.

    \b
    Examples:
      fubon futopt buy TXFC5 1 --price 18000
      fubon futopt buy TXFC5 1 --price-type market
    """
    _place_futopt_order("Buy", symbol, lot, price, price_type, tif, otype, mtype, account_index)


@futopt_group.command("sell")
@click.argument("symbol")
@click.argument("lot", type=int)
@click.option("--price", type=str, default=None, help="Limit price. Omit for market orders.")
@click.option(
    "--price-type",
    type=click.Choice(["limit", "market", "market-range"]),
    default="limit",
    help="Price type",
)
@click.option(
    "--time-in-force",
    "tif",
    type=click.Choice(["ROD", "IOC", "FOK"]),
    default="ROD",
    help="Time in force",
)
@click.option(
    "--order-type",
    "otype",
    type=click.Choice(["new", "cover", "auto"]),
    default="new",
    help="Order type: new position, cover (close), or auto",
)
@click.option(
    "--market-type",
    "mtype",
    type=click.Choice(["future", "future-night", "option", "option-night"]),
    default="future",
    help="Market type",
)
@click.option("--account-index", type=int, default=0, help="Account index (default: 0)")
def futopt_sell(symbol, lot, price, price_type, tif, otype, mtype, account_index):
    """Place a futures/options SELL order.

    \b
    Examples:
      fubon futopt sell TXFC5 1 --price 18000
      fubon futopt sell TXFC5 1 --price-type market
    """
    _place_futopt_order("Sell", symbol, lot, price, price_type, tif, otype, mtype, account_index)


def _place_futopt_order(action, symbol, lot, price, price_type, tif, otype, mtype, account_index):
    """Internal: build and place a futures/options order."""
    from fubon_neo.constant import BSAction, FutOptMarketType, FutOptOrderType, FutOptPriceType, TimeInForce
    from fubon_neo.sdk import FutOptOrder

    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    bs_map = {"Buy": BSAction.Buy, "Sell": BSAction.Sell}
    pt_map = {
        "limit": FutOptPriceType.Limit,
        "market": FutOptPriceType.Market,
        "market-range": FutOptPriceType.MarketRange,
    }
    tif_map = {"ROD": TimeInForce.ROD, "IOC": TimeInForce.IOC, "FOK": TimeInForce.FOK}
    ot_map = {
        "new": FutOptOrderType.New,
        "cover": FutOptOrderType.Cover,
        "auto": FutOptOrderType.Auto,
    }
    mt_map = {
        "future": FutOptMarketType.Future,
        "future-night": FutOptMarketType.FutureNight,
        "option": FutOptMarketType.Option,
        "option-night": FutOptMarketType.OptionNight,
    }

    if price_type == "limit" and price is None:
        output(None, success=False, error="--price is required for limit orders")
        sys.exit(1)

    order_kwargs = dict(
        buy_sell=bs_map[action],
        symbol=symbol,
        price=price,
        lot=lot,
        market_type=mt_map[mtype],
        price_type=pt_map[price_type],
        time_in_force=tif_map[tif],
        order_type=ot_map[otype],
    )

    order = FutOptOrder(**order_kwargs)

    try:
        result = sdk.futopt.place_order(acc, order)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@futopt_group.command("orders")
@click.option("--account-index", type=int, default=0, help="Account index")
def futopt_orders(account_index):
    """Query current futures/options open orders.

    \b
    Example:
      fubon futopt orders
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.futopt.order_result(acc)
        data = []
        if hasattr(result, "data") and result.data:
            for r in result.data:
                data.append(obj_to_dict(r))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@futopt_group.command("filled")
@click.option("--account-index", type=int, default=0, help="Account index")
def futopt_filled(account_index):
    """Query filled futures/options orders for today.

    \b
    Example:
      fubon futopt filled
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.futopt.filled_result(acc)
        data = []
        if hasattr(result, "data") and result.data:
            for r in result.data:
                data.append(obj_to_dict(r))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@futopt_group.command("cancel")
@click.argument("order-no")
@click.option("--account-index", type=int, default=0, help="Account index")
def futopt_cancel(order_no, account_index):
    """Cancel an existing futures/options order by order number.

    \b
    Example:
      fubon futopt cancel F1234
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        order_results = sdk.futopt.order_result(acc)
        target = None
        if hasattr(order_results, "data") and order_results.data:
            for r in order_results.data:
                r_dict = obj_to_dict(r)
                rno = r_dict.get("order_no") or r_dict.get("orderNo") or ""
                if rno == order_no:
                    target = r
                    break

        if target is None:
            output(
                None, success=False,
                error=f"Order {order_no} not found in current order results"
            )
            sys.exit(1)

        result = sdk.futopt.cancel_order(acc, target)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@futopt_group.command("modify-price")
@click.argument("order-no")
@click.argument("new-price")
@click.option("--account-index", type=int, default=0, help="Account index")
def futopt_modify_price(order_no, new_price, account_index):
    """Modify the price of an existing futures/options order.

    \b
    Example:
      fubon futopt modify-price F1234 18100
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        order_results = sdk.futopt.order_result(acc)
        target = None
        if hasattr(order_results, "data") and order_results.data:
            for r in order_results.data:
                r_dict = obj_to_dict(r)
                rno = r_dict.get("order_no") or r_dict.get("orderNo") or ""
                if rno == order_no:
                    target = r
                    break

        if target is None:
            output(None, success=False, error=f"Order {order_no} not found")
            sys.exit(1)

        result = sdk.futopt.modify_price(acc, target, new_price)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@futopt_group.command("modify-quantity")
@click.argument("order-no")
@click.argument("new-quantity", type=int)
@click.option("--account-index", type=int, default=0, help="Account index")
def futopt_modify_quantity(order_no, new_quantity, account_index):
    """Modify the quantity (lots) of an existing futures/options order.

    \b
    Example:
      fubon futopt modify-quantity F1234 2
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        order_results = sdk.futopt.order_result(acc)
        target = None
        if hasattr(order_results, "data") and order_results.data:
            for r in order_results.data:
                r_dict = obj_to_dict(r)
                rno = r_dict.get("order_no") or r_dict.get("orderNo") or ""
                if rno == order_no:
                    target = r
                    break

        if target is None:
            output(None, success=False, error=f"Order {order_no} not found")
            sys.exit(1)

        result = sdk.futopt.modify_volume(acc, target, new_quantity)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@futopt_group.command("inventories")
@click.option("--account-index", type=int, default=0, help="Account index")
def futopt_inventories(account_index):
    """Query futures/options position inventory.

    \b
    Example:
      fubon futopt inventories
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.futopt.inventories(acc)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@futopt_group.command("settlements")
@click.option("--account-index", type=int, default=0, help="Account index")
def futopt_settlements(account_index):
    """Query futures/options settlement data.

    \b
    Example:
      fubon futopt settlements
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.futopt.settlements(acc)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))
