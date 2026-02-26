"""Stock trading commands: buy, sell, modify, cancel, orders."""

import json
import sys

import click

from fubon_cli.core import get_account, get_sdk_and_accounts, obj_to_dict, output


@click.group("stock")
def stock_group():
    """Stock trading operations: buy, sell, modify, cancel orders."""
    pass


@stock_group.command("buy")
@click.argument("symbol")
@click.argument("quantity", type=int)
@click.option(
    "--price", type=str, default=None, help="Limit price. Omit for market/special price types."
)
@click.option(
    "--price-type",
    type=click.Choice(["limit", "market", "limit-up", "limit-down", "reference"]),
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
    type=click.Choice(["stock", "margin", "short", "sbl", "day-trade"]),
    default="stock",
    help="Order type",
)
@click.option(
    "--market-type",
    "mtype",
    type=click.Choice(["common", "odd", "intraday-odd", "fixing", "emg", "emg-odd"]),
    default="common",
    help="Market type",
)
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
    _place_order(
        "Buy", symbol, quantity, price, price_type, tif, otype, mtype, account_index, user_def
    )


@stock_group.command("sell")
@click.argument("symbol")
@click.argument("quantity", type=int)
@click.option(
    "--price", type=str, default=None, help="Limit price. Omit for market/special price types."
)
@click.option(
    "--price-type",
    type=click.Choice(["limit", "market", "limit-up", "limit-down", "reference"]),
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
    type=click.Choice(["stock", "margin", "short", "sbl", "day-trade"]),
    default="stock",
    help="Order type",
)
@click.option(
    "--market-type",
    "mtype",
    type=click.Choice(["common", "odd", "intraday-odd", "fixing", "emg", "emg-odd"]),
    default="common",
    help="Market type",
)
@click.option("--account-index", type=int, default=0, help="Account index (default: 0)")
@click.option("--user-def", default=None, help="User-defined tag (max 10 alphanumeric chars)")
def sell(symbol, quantity, price, price_type, tif, otype, mtype, account_index, user_def):
    """Place a stock SELL order.

    \b
    Examples:
      fubon stock sell 2330 1000 --price 600
      fubon stock sell 2881 2000 --price-type market
    """
    _place_order(
        "Sell", symbol, quantity, price, price_type, tif, otype, mtype, account_index, user_def
    )


def _place_order(
    action, symbol, quantity, price, price_type, tif, otype, mtype, account_index, user_def
):
    """Internal: build and place a stock order."""
    from fubon_neo.constant import BSAction, MarketType, OrderType, PriceType, TimeInForce
    from fubon_neo.sdk import Order

    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    bs_map = {"Buy": BSAction.Buy, "Sell": BSAction.Sell}
    pt_map = {
        "limit": PriceType.Limit,
        "market": PriceType.Market,
        "limit-up": PriceType.LimitUp,
        "limit-down": PriceType.LimitDown,
        "reference": PriceType.Reference,
    }
    tif_map = {"ROD": TimeInForce.ROD, "IOC": TimeInForce.IOC, "FOK": TimeInForce.FOK}
    ot_map = {
        "stock": OrderType.Stock,
        "margin": OrderType.Margin,
        "short": OrderType.Short,
        "sbl": OrderType.SBL,
        "day-trade": OrderType.DayTrade,
    }
    mt_map = {
        "common": MarketType.Common,
        "odd": MarketType.Odd,
        "intraday-odd": MarketType.IntradayOdd,
        "fixing": MarketType.Fixing,
        "emg": MarketType.Emg,
        "emg-odd": MarketType.EmgOdd,
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
            output(
                None, success=False, error=f"Order {order_no} not found in current order results"
            )
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


@stock_group.command("order-detail")
@click.argument("order-no")
@click.option("--account-index", type=int, default=0, help="Account index")
def order_detail(order_no, account_index):
    """Get detailed history for a specific order.

    \b
    Example:
      fubon stock order-detail A1234
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.stock.order_result_detail(acc, order_no)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("order-history")
@click.option("--from", "from_date", required=True, help="Start date (yyyy-MM-dd)")
@click.option("--to", "to_date", required=True, help="End date (yyyy-MM-dd, max 30-day range)")
@click.option("--account-index", type=int, default=0, help="Account index")
def order_history(from_date, to_date, account_index):
    """Query historical orders within a date range (max 30 days).

    \b
    Example:
      fubon stock order-history --from 2024-01-01 --to 2024-01-31
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.stock.order_history(acc, from_date, to_date)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("filled-history")
@click.option("--from", "from_date", required=True, help="Start date (yyyy-MM-dd)")
@click.option("--to", "to_date", required=True, help="End date (yyyy-MM-dd, max 30-day range)")
@click.option("--account-index", type=int, default=0, help="Account index")
def filled_history(from_date, to_date, account_index):
    """Query historical filled (executed) orders within a date range (max 30 days).

    \b
    Example:
      fubon stock filled-history --from 2024-01-01 --to 2024-01-31
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.stock.filled_history(acc, from_date, to_date)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("batch-place")
@click.argument("orders-json")
@click.option("--account-index", type=int, default=0, help="Account index")
def batch_place(orders_json, account_index):
    """Place multiple orders in a single batch. ORDERS-JSON is a JSON array of order objects.

    \b
    Each order object fields: symbol, buy_sell (Buy/Sell), price, quantity,
      price_type (limit/market/limit-up/limit-down/reference),
      time_in_force (ROD/IOC/FOK), order_type (stock/margin/short/sbl/day-trade),
      market_type (common/odd/intraday-odd/fixing/emg/emg-odd)

    Example:
      fubon stock batch-place '[{"symbol":"2330","buy_sell":"Buy","price":"580","quantity":1000,"price_type":"limit","time_in_force":"ROD","order_type":"stock","market_type":"common"}]'
    """
    from fubon_neo.constant import BSAction, MarketType, OrderType, PriceType, TimeInForce
    from fubon_neo.sdk import Order

    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    pt_map = {
        "limit": PriceType.Limit, "market": PriceType.Market,
        "limit-up": PriceType.LimitUp, "limit-down": PriceType.LimitDown,
        "reference": PriceType.Reference,
    }
    tif_map = {"ROD": TimeInForce.ROD, "IOC": TimeInForce.IOC, "FOK": TimeInForce.FOK}
    ot_map = {
        "stock": OrderType.Stock, "margin": OrderType.Margin, "short": OrderType.Short,
        "sbl": OrderType.SBL, "day-trade": OrderType.DayTrade,
    }
    mt_map = {
        "common": MarketType.Common, "odd": MarketType.Odd,
        "intraday-odd": MarketType.IntradayOdd, "fixing": MarketType.Fixing,
        "emg": MarketType.Emg, "emg-odd": MarketType.EmgOdd,
    }
    bs_map = {"Buy": BSAction.Buy, "Sell": BSAction.Sell}

    try:
        order_defs = json.loads(orders_json)
        orders = []
        for od in order_defs:
            kwargs = dict(
                buy_sell=bs_map[od["buy_sell"]],
                symbol=od["symbol"],
                price=str(od.get("price", "")),
                quantity=int(od["quantity"]),
                market_type=mt_map[od.get("market_type", "common")],
                price_type=pt_map[od.get("price_type", "limit")],
                time_in_force=tif_map[od.get("time_in_force", "ROD")],
                order_type=ot_map[od.get("order_type", "stock")],
            )
            if od.get("user_def"):
                kwargs["user_def"] = od["user_def"]
            orders.append(Order(**kwargs))

        result = sdk.stock.batch_place_order(acc, orders)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("batch-cancel")
@click.argument("order-nos", nargs=-1, required=True)
@click.option("--account-index", type=int, default=0, help="Account index")
def batch_cancel(order_nos, account_index):
    """Cancel multiple orders by order numbers.

    \b
    Example:
      fubon stock batch-cancel A1234 A1235 A1236
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        order_results = sdk.stock.get_order_results(acc)
        targets = []
        if hasattr(order_results, "data") and order_results.data:
            for r in order_results.data:
                r_dict = obj_to_dict(r)
                rno = r_dict.get("order_no") or r_dict.get("orderNo") or ""
                if rno in order_nos:
                    targets.append(r)

        not_found = set(order_nos) - {
            (obj_to_dict(t).get("order_no") or obj_to_dict(t).get("orderNo") or "")
            for t in targets
        }
        if not_found:
            output(None, success=False, error=f"Orders not found: {', '.join(not_found)}")
            sys.exit(1)

        result = sdk.stock.batch_cancel_order(acc, targets)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("batch-modify-price")
@click.argument("updates-json")
@click.option("--account-index", type=int, default=0, help="Account index")
def batch_modify_price(updates_json, account_index):
    """Modify prices for multiple orders. UPDATES-JSON is a JSON array of {order_no, price}.

    \b
    Example:
      fubon stock batch-modify-price '[{"order_no":"A1234","price":"575"},{"order_no":"A1235","price":"582"}]'
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        updates = json.loads(updates_json)
        order_results = sdk.stock.get_order_results(acc)

        order_map = {}
        if hasattr(order_results, "data") and order_results.data:
            for r in order_results.data:
                r_dict = obj_to_dict(r)
                rno = r_dict.get("order_no") or r_dict.get("orderNo") or ""
                order_map[rno] = r

        modify_objs = []
        for upd in updates:
            order_no = upd["order_no"]
            if order_no not in order_map:
                output(None, success=False, error=f"Order {order_no} not found")
                sys.exit(1)
            modify_objs.append(sdk.stock.make_modify_price_obj(order_map[order_no], str(upd["price"])))

        result = sdk.stock.batch_modify_price(acc, modify_objs)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("batch-modify-quantity")
@click.argument("updates-json")
@click.option("--account-index", type=int, default=0, help="Account index")
def batch_modify_quantity(updates_json, account_index):
    """Modify quantities for multiple orders. UPDATES-JSON is a JSON array of {order_no, quantity}.

    \b
    Example:
      fubon stock batch-modify-quantity '[{"order_no":"A1234","quantity":500}]'
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        updates = json.loads(updates_json)
        order_results = sdk.stock.get_order_results(acc)

        order_map = {}
        if hasattr(order_results, "data") and order_results.data:
            for r in order_results.data:
                r_dict = obj_to_dict(r)
                rno = r_dict.get("order_no") or r_dict.get("orderNo") or ""
                order_map[rno] = r

        modify_objs = []
        for upd in updates:
            order_no = upd["order_no"]
            if order_no not in order_map:
                output(None, success=False, error=f"Order {order_no} not found")
                sys.exit(1)
            modify_objs.append(sdk.stock.make_modify_quantity_obj(order_map[order_no], int(upd["quantity"])))

        result = sdk.stock.batch_modify_volume(acc, modify_objs)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("batch-create")
@click.argument("orders-json")
@click.option("--account-index", type=int, default=0, help="Account index")
def batch_create(orders_json, account_index):
    """Create a named batch order. ORDERS-JSON is a JSON array of order objects (same format as batch-place).

    \b
    Example:
      fubon stock batch-create '[{"symbol":"2330","buy_sell":"Buy","price":"580","quantity":1000,"price_type":"limit","time_in_force":"ROD","order_type":"stock","market_type":"common"}]'
    """
    from fubon_neo.constant import BSAction, MarketType, OrderType, PriceType, TimeInForce
    from fubon_neo.sdk import Order

    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    pt_map = {
        "limit": PriceType.Limit, "market": PriceType.Market,
        "limit-up": PriceType.LimitUp, "limit-down": PriceType.LimitDown,
        "reference": PriceType.Reference,
    }
    tif_map = {"ROD": TimeInForce.ROD, "IOC": TimeInForce.IOC, "FOK": TimeInForce.FOK}
    ot_map = {
        "stock": OrderType.Stock, "margin": OrderType.Margin, "short": OrderType.Short,
        "sbl": OrderType.SBL, "day-trade": OrderType.DayTrade,
    }
    mt_map = {
        "common": MarketType.Common, "odd": MarketType.Odd,
        "intraday-odd": MarketType.IntradayOdd, "fixing": MarketType.Fixing,
        "emg": MarketType.Emg, "emg-odd": MarketType.EmgOdd,
    }
    bs_map = {"Buy": BSAction.Buy, "Sell": BSAction.Sell}

    try:
        order_defs = json.loads(orders_json)
        orders = []
        for od in order_defs:
            kwargs = dict(
                buy_sell=bs_map[od["buy_sell"]],
                symbol=od["symbol"],
                price=str(od.get("price", "")),
                quantity=int(od["quantity"]),
                market_type=mt_map[od.get("market_type", "common")],
                price_type=pt_map[od.get("price_type", "limit")],
                time_in_force=tif_map[od.get("time_in_force", "ROD")],
                order_type=ot_map[od.get("order_type", "stock")],
            )
            if od.get("user_def"):
                kwargs["user_def"] = od["user_def"]
            orders.append(Order(**kwargs))

        result = sdk.stock.create_batch_order(acc, orders)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("batch-get")
@click.argument("batch-no")
@click.option("--account-index", type=int, default=0, help="Account index")
def batch_get(batch_no, account_index):
    """Get details of a named batch order by batch number.

    \b
    Example:
      fubon stock batch-get B0001
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.stock.get_batch_order(acc, batch_no)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("batch-list")
@click.option("--account-index", type=int, default=0, help="Account index")
def batch_list(account_index):
    """List all batch orders for today.

    \b
    Example:
      fubon stock batch-list
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.stock.get_batch_order_list(acc)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("symbol-quote")
@click.argument("symbol")
@click.option(
    "--market-type",
    "mtype",
    type=click.Choice(["common", "odd", "intraday-odd", "fixing", "emg", "emg-odd"]),
    default="common",
    help="Market type",
)
@click.option("--account-index", type=int, default=0, help="Account index")
def symbol_quote(symbol, mtype, account_index):
    """Query real-time stock quote including tradability flags.

    \b
    Example:
      fubon stock symbol-quote 2330
    """
    from fubon_neo.constant import MarketType

    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    mt_map = {
        "common": MarketType.Common, "odd": MarketType.Odd,
        "intraday-odd": MarketType.IntradayOdd, "fixing": MarketType.Fixing,
        "emg": MarketType.Emg, "emg-odd": MarketType.EmgOdd,
    }

    try:
        result = sdk.stock.query_symbol_quote(acc, symbol, mt_map[mtype])
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("symbol-snapshot")
@click.option(
    "--market-type",
    "mtype",
    type=click.Choice(["common", "odd", "intraday-odd", "fixing", "emg", "emg-odd"]),
    default="common",
    help="Market type",
)
@click.option(
    "--stock-types",
    default=None,
    help="Comma-separated stock types filter (e.g. stock,margin,short)",
)
@click.option("--account-index", type=int, default=0, help="Account index")
def symbol_snapshot(mtype, stock_types, account_index):
    """Query full quote snapshot for all holdings.

    \b
    Example:
      fubon stock symbol-snapshot
      fubon stock symbol-snapshot --market-type common --stock-types stock,margin
    """
    from fubon_neo.constant import MarketType

    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    mt_map = {
        "common": MarketType.Common, "odd": MarketType.Odd,
        "intraday-odd": MarketType.IntradayOdd, "fixing": MarketType.Fixing,
        "emg": MarketType.Emg, "emg-odd": MarketType.EmgOdd,
    }

    try:
        kwargs = {"market_type": mt_map[mtype]}
        if stock_types:
            kwargs["stock_types"] = stock_types.split(",")
        result = sdk.stock.query_symbol_snapshot(acc, **kwargs)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@stock_group.command("price-change")
@click.option(
    "--market",
    type=click.Choice(["TSE", "OTC", "ESB", "TIB", "PSB"]),
    default=None,
    help="Market to query. Omit to query all holdings.",
)
@click.option("--account-index", type=int, default=0, help="Account index")
def price_change(market, account_index):
    """Query up/down limit price change report.

    \b
    Examples:
      fubon stock price-change
      fubon stock price-change --market TSE
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        if market:
            result = sdk.stock.query_market_price_change(acc, market)
        else:
            result = sdk.stock.query_market_price_change(acc)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))
