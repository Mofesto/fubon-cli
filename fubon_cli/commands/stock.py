"""Stock trading commands: buy, sell, modify, cancel, orders."""

import json
import sys

import click

from fubon_cli.core import get_sdk_and_accounts, get_account, obj_to_dict, output


@click.group("stock")
def stock_group():
    """Stock trading operations: buy, sell, modify, cancel orders."""
    pass


@stock_group.command("buy")
@click.argument("symbol")
@click.argument("quantity", type=int)
@click.option("--price", type=str, default=None, help="Limit price. Omit for market/special price types.")
@click.option("--price-type", type=click.Choice(["limit", "market", "limit-up", "limit-down", "reference"]),
              default="limit", help="Price type")
@click.option("--time-in-force", "tif", type=click.Choice(["ROD", "IOC", "FOK"]),
              default="ROD", help="Time in force")
@click.option("--order-type", "otype", type=click.Choice(["stock", "margin", "short", "sbl", "day-trade"]),
              default="stock", help="Order type")
@click.option("--market-type", "mtype",
              type=click.Choice(["common", "odd", "intraday-odd", "fixing", "emg", "emg-odd"]),
              default="common", help="Market type")
@click.option("--account-index", type=int, default=0, help="Account index (default: 0)")
@click.option("--user-def", default=None, help="User-defined tag (max 10 alphanumeric chars)")
def buy(symbol, quantity, price, price_type, tif, otype, mtype, account_index, user_def):
    """Place a stock BUY order.

    \b
    Examples:
      fubon stock buy 2330 1000 --price 580
      fubon stock buy 2881 2000 --price-type limit-down
      fubon stock buy 2330 500 --price 580 --time-in-force IOC
    """
    _place_order("Buy", symbol, quantity, price, price_type, tif, otype, mtype, account_index, user_def)


@stock_group.command("sell")
@click.argument("symbol")
@click.argument("quantity", type=int)
@click.option("--price", type=str, default=None, help="Limit price. Omit for market/special price types.")
@click.option("--price-type", type=click.Choice(["limit", "market", "limit-up", "limit-down", "reference"]),
              default="limit", help="Price type")
@click.option("--time-in-force", "tif", type=click.Choice(["ROD", "IOC", "FOK"]),
              default="ROD", help="Time in force")
@click.option("--order-type", "otype", type=click.Choice(["stock", "margin", "short", "sbl", "day-trade"]),
              default="stock", help="Order type")
@click.option("--market-type", "mtype",
              type=click.Choice(["common", "odd", "intraday-odd", "fixing", "emg", "emg-odd"]),
              default="common", help="Market type")
@click.option("--account-index", type=int, default=0, help="Account index (default: 0)")
@click.option("--user-def", default=None, help="User-defined tag (max 10 alphanumeric chars)")
def sell(symbol, quantity, price, price_type, tif, otype, mtype, account_index, user_def):
    """Place a stock SELL order.

    \b
    Examples:
      fubon stock sell 2330 1000 --price 600
      fubon stock sell 2881 2000 --price-type market
    """
    _place_order("Sell", symbol, quantity, price, price_type, tif, otype, mtype, account_index, user_def)


def _place_order(action, symbol, quantity, price, price_type, tif, otype, mtype, account_index, user_def):
    """Internal: build and place a stock order."""
    from fubon_neo.sdk import Order
    from fubon_neo.constant import BSAction, TimeInForce, OrderType, PriceType, MarketType

    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    bs_map = {"Buy": BSAction.Buy, "Sell": BSAction.Sell}
    pt_map = {
        "limit": PriceType.Limit, "market": PriceType.Market,
        "limit-up": PriceType.LimitUp, "limit-down": PriceType.LimitDown,
        "reference": PriceType.Reference,
    }
    tif_map = {"ROD": TimeInForce.ROD, "IOC": TimeInForce.IOC, "FOK": TimeInForce.FOK}
    ot_map = {
        "stock": OrderType.Stock, "margin": OrderType.Margin,
        "short": OrderType.Short, "sbl": OrderType.SBL,
        "day-trade": OrderType.DayTrade,
    }
    mt_map = {
        "common": MarketType.Common, "odd": MarketType.Odd,
        "intraday-odd": MarketType.IntradayOdd, "fixing": MarketType.Fixing,
        "emg": MarketType.Emg, "emg-odd": MarketType.EmgOdd,
    }

    if price_type == "limit" and price is None:
        output(None, success=False, error="--price is required for limit orders")
        sys.exit(1)

    order_kwargs = dict(
        buy_sell=bs_map[action],
        symbol=symbol,
        price=price,
        quantity=quantity,
        market_type=mt_map[mtype],
        price_type=pt_map[price_type],
        time_in_force=tif_map[tif],
        order_type=ot_map[otype],
    )
    if user_def:
        order_kwargs["user_def"] = user_def

    order = Order(**order_kwargs)

    try:
        result = sdk.stock.place_order(acc, order)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("orders")
@click.option("--account-index", type=int, default=0, help="Account index")
def orders(account_index):
    """Query current order results.

    \b
    Example:
      fubon stock orders
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.stock.get_order_results(acc)
        data = []
        if hasattr(result, "data") and result.data:
            for r in result.data:
                data.append(obj_to_dict(r))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("cancel")
@click.argument("order-no")
@click.option("--account-index", type=int, default=0, help="Account index")
def cancel(order_no, account_index):
    """Cancel an existing order by order number.

    \b
    Example:
      fubon stock cancel A1234
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        order_results = sdk.stock.get_order_results(acc)
        target = None
        if hasattr(order_results, "data") and order_results.data:
            for r in order_results.data:
                r_dict = obj_to_dict(r)
                # Match by order_no field
                rno = r_dict.get("order_no") or r_dict.get("orderNo") or ""
                if rno == order_no:
                    target = r
                    break

        if target is None:
            output(None, success=False, error=f"Order {order_no} not found in current order results")
            sys.exit(1)

        result = sdk.stock.cancel_order(acc, target)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("modify-price")
@click.argument("order-no")
@click.argument("new-price")
@click.option("--account-index", type=int, default=0, help="Account index")
def modify_price(order_no, new_price, account_index):
    """Modify the price of an existing order.

    \b
    Example:
      fubon stock modify-price A1234 580.0
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        order_results = sdk.stock.get_order_results(acc)
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

        modify_obj = sdk.stock.make_modify_price_obj(target, new_price)
        result = sdk.stock.modify_price(acc, modify_obj)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("modify-quantity")
@click.argument("order-no")
@click.argument("new-quantity", type=int)
@click.option("--account-index", type=int, default=0, help="Account index")
def modify_quantity(order_no, new_quantity, account_index):
    """Modify the quantity of an existing order.

    \b
    Example:
      fubon stock modify-quantity A1234 500
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        order_results = sdk.stock.get_order_results(acc)
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

        modify_obj = sdk.stock.make_modify_quantity_obj(target, new_quantity)
        result = sdk.stock.modify_quantity(acc, modify_obj)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))
