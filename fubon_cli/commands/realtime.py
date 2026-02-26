"""Realtime (WebSocket) subscription commands."""

import json
import signal
import sys
import time

import click

from fubon_cli.core import get_sdk_and_accounts, output


@click.group("realtime")
def realtime_group():
    """Realtime market data subscriptions via WebSocket."""
    pass


@realtime_group.command("subscribe")
@click.argument("symbol")
@click.option(
    "--channel",
    type=click.Choice(["trades", "aggregates", "candles"]),
    default="trades",
    help="Data channel to subscribe",
)
def subscribe(symbol, channel):
    """Subscribe to realtime data for a stock. Streams JSON lines to stdout.

    \b
    Press Ctrl+C to stop.

    Examples:
      fubon realtime subscribe 2330
      fubon realtime subscribe 2330 --channel aggregates
    """
    sdk, _ = get_sdk_and_accounts()
    sdk.init_realtime()

    ws_stock = sdk.marketdata.websocket_client.stock

    def on_message(message):
        if isinstance(message, str):
            print(message, flush=True)
        else:
            print(json.dumps(message, ensure_ascii=False, default=str), flush=True)

    def on_error(error):
        err_msg = json.dumps({"event": "error", "message": str(error)}, ensure_ascii=False)
        print(err_msg, flush=True)

    ws_stock.on("message", on_message)
    ws_stock.on("error", on_error)

    ws_stock.connect()
    ws_stock.subscribe({"channel": channel, "symbol": symbol})

    # Keep running until Ctrl+C
    def handle_signal(signum, frame):
        ws_stock.disconnect()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ws_stock.disconnect()


@realtime_group.command("callbacks")
@click.option("--account-index", type=int, default=0, help="Account index")
def callbacks(account_index):
    """Listen to order/fill/event callbacks. Streams JSON lines to stdout.

    \b
    Press Ctrl+C to stop.

    Example:
      fubon realtime callbacks
    """
    sdk, accounts = get_sdk_and_accounts()
    acc = accounts[account_index] if account_index < len(accounts) else accounts[0]

    def on_order(code, content):
        msg = {"event": "order", "code": code, "data": str(content)}
        print(json.dumps(msg, ensure_ascii=False), flush=True)

    def on_order_changed(code, content):
        msg = {"event": "order_changed", "code": code, "data": str(content)}
        print(json.dumps(msg, ensure_ascii=False), flush=True)

    def on_filled(code, content):
        msg = {"event": "filled", "code": code, "data": str(content)}
        print(json.dumps(msg, ensure_ascii=False), flush=True)

    def on_event(code, content):
        msg = {"event": "system_event", "code": code, "data": str(content)}
        print(json.dumps(msg, ensure_ascii=False), flush=True)

    sdk.set_on_order(on_order)
    sdk.set_on_order_changed(on_order_changed)
    sdk.set_on_filled(on_filled)
    sdk.set_on_event(on_event)

    print(
        json.dumps(
            {"event": "listening", "message": "Waiting for callbacks... Press Ctrl+C to stop."}
        ),
        flush=True,
    )

    def handle_signal(signum, frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
