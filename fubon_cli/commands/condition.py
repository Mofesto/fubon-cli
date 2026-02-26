"""Condition order commands: single, multi, TPSL, trailing, time-slice, day-trade."""

import json
import sys

import click

from fubon_cli.core import get_account, get_sdk_and_accounts, obj_to_dict, output


def _get_condition_client(sdk, is_futopt):
    """Return either sdk.stock.condition or sdk.futopt.condition."""
    if is_futopt:
        return sdk.futopt.condition
    return sdk.stock.condition


@click.group("condition")
def condition_group():
    """Condition orders: single, multi, TPSL, trailing stop, time-slice, day-trade."""
    pass


# --- Query Commands ---

@condition_group.command("list")
@click.option("--futopt", "is_futopt", is_flag=True, help="Query futures/options conditions")
@click.option("--account-index", type=int, default=0, help="Account index")
def condition_list(is_futopt, account_index):
    """List active condition orders.

    \b
    Examples:
      fubon condition list
      fubon condition list --futopt
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        result = client.get_condition(acc)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("get")
@click.argument("guid")
@click.option("--futopt", "is_futopt", is_flag=True, help="Query futures/options conditions")
@click.option("--account-index", type=int, default=0, help="Account index")
def condition_get(guid, is_futopt, account_index):
    """Get a condition order by GUID.

    \b
    Example:
      fubon condition get 550e8400-e29b-41d4-a716-446655440000
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        result = client.get_condition_by_guid(acc, guid)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("cancel")
@click.argument("guid")
@click.option("--futopt", "is_futopt", is_flag=True, help="Cancel a futures/options condition")
@click.option("--account-index", type=int, default=0, help="Account index")
def condition_cancel(guid, is_futopt, account_index):
    """Cancel a condition order by GUID.

    \b
    Example:
      fubon condition cancel 550e8400-e29b-41d4-a716-446655440000
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        result = client.cancel_condition(acc, guid)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("history")
@click.option("--from", "from_date", required=True, help="Start date (yyyy-MM-dd)")
@click.option("--to", "to_date", required=True, help="End date (yyyy-MM-dd)")
@click.option("--futopt", "is_futopt", is_flag=True, help="Query futures/options conditions")
@click.option("--account-index", type=int, default=0, help="Account index")
def condition_history(from_date, to_date, is_futopt, account_index):
    """Query historical condition orders within a date range.

    \b
    Example:
      fubon condition history --from 2024-01-01 --to 2024-01-31
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        result = client.get_condition_history(acc, from_date, to_date)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("trail-list")
@click.option("--futopt", "is_futopt", is_flag=True, help="Query futures/options trailing orders")
@click.option("--account-index", type=int, default=0, help="Account index")
def trail_list(is_futopt, account_index):
    """List active trailing stop/profit orders.

    \b
    Example:
      fubon condition trail-list
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        result = client.get_trail_order(acc)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("trail-history")
@click.option("--from", "from_date", required=True, help="Start date (yyyy-MM-dd)")
@click.option("--to", "to_date", required=True, help="End date (yyyy-MM-dd)")
@click.option("--futopt", "is_futopt", is_flag=True, help="Query futures/options trailing orders")
@click.option("--account-index", type=int, default=0, help="Account index")
def trail_history(from_date, to_date, is_futopt, account_index):
    """Query historical trailing stop/profit orders within a date range.

    \b
    Example:
      fubon condition trail-history --from 2024-01-01 --to 2024-01-31
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        result = client.get_trail_history(acc, from_date, to_date)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("timeslice-get")
@click.argument("batch-no")
@click.option("--account-index", type=int, default=0, help="Account index")
def timeslice_get(batch_no, account_index):
    """Get time-slice (TWAP) order details by batch number.

    \b
    Example:
      fubon condition timeslice-get B0001
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        result = sdk.stock.condition.get_time_slice_order(acc, batch_no)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("day-trade-list")
@click.option("--futopt", "is_futopt", is_flag=True, help="Query futures/options day-trade conditions")
@click.option("--account-index", type=int, default=0, help="Account index")
def day_trade_list(is_futopt, account_index):
    """List active day-trade condition orders.

    \b
    Example:
      fubon condition day-trade-list
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        result = client.get_day_trade_condition(acc)
        data = []
        if hasattr(result, "data") and result.data:
            for item in result.data:
                data.append(obj_to_dict(item))
        output(data, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


# --- Place Commands (JSON-driven) ---

@condition_group.command("place-single")
@click.argument("params-json")
@click.option("--futopt", "is_futopt", is_flag=True, help="Place futures/options condition")
@click.option("--account-index", type=int, default=0, help="Account index")
def place_single(params_json, is_futopt, account_index):
    """Place a single-condition order.

    PARAMS-JSON must be a JSON object with keys:
      start_date, end_date, stop_sign (Full/Partial/UntilEnd),
      condition: {trading_type, symbol, trigger_content, price, operator},
      order: {buy_sell, symbol, price, quantity, price_type, time_in_force, order_type, market_type}

    \b
    Example:
      fubon condition place-single '{"start_date":"2024-06-01","end_date":"2024-06-30","stop_sign":"Full","condition":{...},"order":{...}}'
    """
    from fubon_neo.constant import (
        BSAction, MarketType, Operator, OrderType, PriceType, StopSign, TimeInForce, TradingType,
        TriggerContent,
    )
    from fubon_neo.sdk import Condition, Order

    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        params = json.loads(params_json)
        stop_sign_map = {
            "Full": StopSign.Full, "Partial": StopSign.Partial, "UntilEnd": StopSign.UntilEnd
        }
        cond_def = params["condition"]
        order_def = params["order"]

        condition = Condition(
            trading_type=getattr(TradingType, cond_def["trading_type"]),
            symbol=cond_def["symbol"],
            trigger_content=getattr(TriggerContent, cond_def["trigger_content"]),
            price=str(cond_def["price"]),
            operator=getattr(Operator, cond_def["operator"]),
        )

        order = _build_stock_order(order_def, BSAction, PriceType, TimeInForce, OrderType, MarketType, Order)

        result = client.single_condition(
            acc,
            params["start_date"],
            params["end_date"],
            stop_sign_map[params["stop_sign"]],
            condition,
            order,
        )
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("place-multi")
@click.argument("params-json")
@click.option("--futopt", "is_futopt", is_flag=True, help="Place futures/options multi-condition")
@click.option("--account-index", type=int, default=0, help="Account index")
def place_multi(params_json, is_futopt, account_index):
    """Place a multi-condition order (AND/OR trigger logic).

    PARAMS-JSON must be a JSON object with keys:
      start_date, end_date, stop_sign, conditions (array of condition objects), order

    \b
    Example:
      fubon condition place-multi '{"start_date":"2024-06-01","end_date":"2024-06-30","stop_sign":"Full","conditions":[{...}],"order":{...}}'
    """
    from fubon_neo.constant import (
        BSAction, MarketType, Operator, OrderType, PriceType, StopSign, TimeInForce, TradingType,
        TriggerContent,
    )
    from fubon_neo.sdk import Condition, Order

    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        params = json.loads(params_json)
        stop_sign_map = {"Full": StopSign.Full, "Partial": StopSign.Partial, "UntilEnd": StopSign.UntilEnd}

        conditions = []
        for cond_def in params["conditions"]:
            conditions.append(Condition(
                trading_type=getattr(TradingType, cond_def["trading_type"]),
                symbol=cond_def["symbol"],
                trigger_content=getattr(TriggerContent, cond_def["trigger_content"]),
                price=str(cond_def["price"]),
                operator=getattr(Operator, cond_def["operator"]),
            ))

        order = _build_stock_order(
            params["order"], BSAction, PriceType, TimeInForce, OrderType, MarketType, Order
        )

        result = client.multi_condition(
            acc,
            params["start_date"],
            params["end_date"],
            stop_sign_map[params["stop_sign"]],
            conditions,
            order,
        )
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("place-tpsl")
@click.argument("params-json")
@click.option("--futopt", "is_futopt", is_flag=True, help="Place futures/options TPSL order")
@click.option("--account-index", type=int, default=0, help="Account index")
def place_tpsl(params_json, is_futopt, account_index):
    """Place a stop-loss / take-profit (TPSL) order.

    PARAMS-JSON must be a JSON object. See Fubon API docs for full field list.

    \b
    Example:
      fubon condition place-tpsl '{"start_date":"2024-06-01","end_date":"2024-06-30","stop_sign":"Full","tpsl":{...}}'
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        params = json.loads(params_json)
        result = client.tpsl_order(acc, **params)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("place-trail")
@click.argument("params-json")
@click.option("--futopt", "is_futopt", is_flag=True, help="Place futures/options trailing order")
@click.option("--account-index", type=int, default=0, help="Account index")
def place_trail(params_json, is_futopt, account_index):
    """Place a trailing stop/profit order.

    PARAMS-JSON must be a JSON object with keys:
      start_date, end_date, stop_sign, trail_order: {symbol, price, direction, tick_num,
        buy_sell, lot/quantity, price_type, diff, time_in_force, order_type}

    \b
    Example:
      fubon condition place-trail '{"start_date":"2024-06-01","end_date":"2024-06-30","stop_sign":"Full","trail_order":{...}}'
    """
    from fubon_neo.constant import (
        BSAction, Direction, MarketType, OrderType, PriceType, StopSign, TimeInForce,
    )
    from fubon_neo.sdk import TrailOrder

    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        params = json.loads(params_json)
        stop_sign_map = {"Full": StopSign.Full, "Partial": StopSign.Partial, "UntilEnd": StopSign.UntilEnd}
        to_def = params["trail_order"]

        trail_order = TrailOrder(
            symbol=to_def["symbol"],
            price=str(to_def["price"]),
            direction=getattr(Direction, to_def["direction"]),
            tick_num=int(to_def["tick_num"]),
            buy_sell=getattr(BSAction, to_def["buy_sell"]),
            quantity=int(to_def.get("quantity", to_def.get("lot", 1))),
            price_type=getattr(PriceType, to_def.get("price_type", "Limit")),
            diff=int(to_def.get("diff", 0)),
            time_in_force=getattr(TimeInForce, to_def.get("time_in_force", "ROD")),
            order_type=getattr(OrderType, to_def.get("order_type", "Stock")),
        )

        result = client.trail_profit(
            acc,
            params["start_date"],
            params["end_date"],
            stop_sign_map[params["stop_sign"]],
            trail_order,
        )
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("place-timeslice")
@click.argument("params-json")
@click.option("--account-index", type=int, default=0, help="Account index")
def place_timeslice(params_json, account_index):
    """Place a time-slice (TWAP-style) order.

    PARAMS-JSON must be a JSON object with keys:
      start_date, end_date, stop_sign,
      split: {method, interval, single_quantity, total_quantity, start_time},
      order: {buy_sell, symbol, price, price_type, time_in_force, order_type, market_type}

    \b
    Example:
      fubon condition place-timeslice '{"start_date":"2024-06-01","end_date":"2024-06-30","stop_sign":"Full","split":{...},"order":{...}}'
    """
    from fubon_neo.constant import (
        BSAction, MarketType, OrderType, PriceType, StopSign, TimeInForce, TimeSliceOrderType,
    )
    from fubon_neo.sdk import Order, SplitDescription

    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)

    try:
        params = json.loads(params_json)
        stop_sign_map = {"Full": StopSign.Full, "Partial": StopSign.Partial, "UntilEnd": StopSign.UntilEnd}
        split_def = params["split"]

        split_desc = SplitDescription(
            method=getattr(TimeSliceOrderType, split_def["method"]),
            interval=int(split_def["interval"]),
            single_quantity=int(split_def["single_quantity"]),
            total_quantity=int(split_def["total_quantity"]),
            start_time=split_def["start_time"],
        )

        order_def = params["order"]
        order = _build_stock_order(
            order_def, BSAction, PriceType, TimeInForce, OrderType, MarketType, Order
        )

        result = sdk.stock.condition.time_slice_order(
            acc,
            params["start_date"],
            params["end_date"],
            stop_sign_map[params["stop_sign"]],
            split_desc,
            order,
        )
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("place-day-trade")
@click.argument("params-json")
@click.option("--futopt", "is_futopt", is_flag=True, help="Place futures/options day-trade condition")
@click.option("--account-index", type=int, default=0, help="Account index")
def place_day_trade(params_json, is_futopt, account_index):
    """Place a day-trade condition order.

    PARAMS-JSON must be a JSON object. See Fubon API docs for full field list.

    \b
    Example:
      fubon condition place-day-trade '{"start_date":"2024-06-01","end_date":"2024-06-30",...}'
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        params = json.loads(params_json)
        result = client.day_trade_condition(acc, **params)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("place-single-tpsl")
@click.argument("params-json")
@click.option("--futopt", "is_futopt", is_flag=True, help="Place futures/options single condition with TPSL")
@click.option("--account-index", type=int, default=0, help="Account index")
def place_single_tpsl(params_json, is_futopt, account_index):
    """Place a single condition order with take-profit/stop-loss.

    PARAMS-JSON is a JSON object. See Fubon API docs for full field list.

    \b
    Example:
      fubon condition place-single-tpsl '{"start_date":"2024-06-01","end_date":"2024-06-30","stop_sign":"Full","condition":{...},"order":{...},"tpsl":{...}}'
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        params = json.loads(params_json)
        result = client.single_condition_with_tpsl(acc, **params)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@condition_group.command("place-multi-tpsl")
@click.argument("params-json")
@click.option("--futopt", "is_futopt", is_flag=True, help="Place futures/options multi condition with TPSL")
@click.option("--account-index", type=int, default=0, help="Account index")
def place_multi_tpsl(params_json, is_futopt, account_index):
    """Place a multi-condition order with take-profit/stop-loss.

    PARAMS-JSON is a JSON object. See Fubon API docs for full field list.

    \b
    Example:
      fubon condition place-multi-tpsl '{"start_date":"2024-06-01","end_date":"2024-06-30","stop_sign":"Full","conditions":[{...}],"order":{...},"tpsl":{...}}'
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = get_account(sdk, accounts, account_index)
    client = _get_condition_client(sdk, is_futopt)

    try:
        params = json.loads(params_json)
        result = client.multi_condition_with_tpsl(acc, **params)
        output(obj_to_dict(result), success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


# --- Helper ---

def _build_stock_order(order_def, BSAction, PriceType, TimeInForce, OrderType, MarketType, Order):
    """Build a stock Order object from a dict definition."""
    pt_map = {
        "Limit": PriceType.Limit, "Market": PriceType.Market,
        "LimitUp": PriceType.LimitUp, "LimitDown": PriceType.LimitDown,
        "Reference": PriceType.Reference,
        "limit": PriceType.Limit, "market": PriceType.Market,
        "limit-up": PriceType.LimitUp, "limit-down": PriceType.LimitDown,
        "reference": PriceType.Reference,
    }
    tif_map = {"ROD": TimeInForce.ROD, "IOC": TimeInForce.IOC, "FOK": TimeInForce.FOK}
    ot_map = {
        "Stock": OrderType.Stock, "Margin": OrderType.Margin, "Short": OrderType.Short,
        "SBL": OrderType.SBL, "DayTrade": OrderType.DayTrade,
        "stock": OrderType.Stock, "margin": OrderType.Margin, "short": OrderType.Short,
        "sbl": OrderType.SBL, "day-trade": OrderType.DayTrade,
    }
    mt_map = {
        "Common": MarketType.Common, "Odd": MarketType.Odd,
        "IntradayOdd": MarketType.IntradayOdd, "Fixing": MarketType.Fixing,
        "Emg": MarketType.Emg, "EmgOdd": MarketType.EmgOdd,
        "common": MarketType.Common, "odd": MarketType.Odd,
        "intraday-odd": MarketType.IntradayOdd, "fixing": MarketType.Fixing,
        "emg": MarketType.Emg, "emg-odd": MarketType.EmgOdd,
    }
    bs_map = {"Buy": BSAction.Buy, "Sell": BSAction.Sell}

    kwargs = dict(
        buy_sell=bs_map[order_def["buy_sell"]],
        symbol=order_def["symbol"],
        price=str(order_def.get("price", "")),
        quantity=int(order_def["quantity"]),
        market_type=mt_map[order_def.get("market_type", "Common")],
        price_type=pt_map[order_def.get("price_type", "Limit")],
        time_in_force=tif_map[order_def.get("time_in_force", "ROD")],
        order_type=ot_map[order_def.get("order_type", "Stock")],
    )
    if order_def.get("user_def"):
        kwargs["user_def"] = order_def["user_def"]
    return Order(**kwargs)
