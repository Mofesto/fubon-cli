"""Market data commands: quote, ticker, candles, snapshot, movers, actives."""

import json
import sys

import click

from fubon_cli.core import get_sdk_and_accounts, output


def _get_rest_stock(sdk):
    """Initialize realtime and return the REST stock client."""
    sdk.init_realtime()
    return sdk.marketdata.rest_client.stock


@click.group("market")
def market_group():
    """Market data queries: quotes, candles, snapshots, movers."""
    pass


@market_group.command("quote")
@click.argument("symbol")
@click.option("--odd-lot", is_flag=True, help="Query odd-lot quote")
def quote(symbol, odd_lot):
    """Get realtime quote for a stock.

    \b
    Examples:
      fubon market quote 2330
      fubon market quote 2330 --odd-lot
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {"symbol": symbol}
        if odd_lot:
            kwargs["type"] = "oddlot"
        result = rest.intraday.quote(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("ticker")
@click.argument("symbol")
@click.option("--odd-lot", is_flag=True, help="Query odd-lot ticker info")
def ticker(symbol, odd_lot):
    """Get ticker information for a stock.

    \b
    Example:
      fubon market ticker 2330
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {"symbol": symbol}
        if odd_lot:
            kwargs["type"] = "oddlot"
        result = rest.intraday.ticker(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("candles")
@click.argument("symbol")
@click.option(
    "--timeframe",
    type=click.Choice(["1", "5", "10", "15", "30", "60"]),
    default="5",
    help="K-line timeframe in minutes",
)
@click.option("--odd-lot", is_flag=True, help="Query odd-lot candles")
def candles(symbol, timeframe, odd_lot):
    """Get intraday candlestick (K-line) data.

    \b
    Examples:
      fubon market candles 2330
      fubon market candles 2330 --timeframe 15
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {"symbol": symbol, "timeframe": timeframe}
        if odd_lot:
            kwargs["type"] = "oddlot"
        result = rest.intraday.candles(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("trades")
@click.argument("symbol")
@click.option("--limit", type=int, default=None, help="Max number of trades")
@click.option("--offset", type=int, default=None, help="Offset for pagination")
def trades(symbol, limit, offset):
    """Get intraday trade details for a stock.

    \b
    Example:
      fubon market trades 2330 --limit 50
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {"symbol": symbol}
        if limit is not None:
            kwargs["limit"] = limit
        if offset is not None:
            kwargs["offset"] = offset
        result = rest.intraday.trades(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("volumes")
@click.argument("symbol")
def volumes(symbol):
    """Get price-volume distribution for a stock.

    \b
    Example:
      fubon market volumes 2330
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        result = rest.intraday.volumes(symbol=symbol)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("snapshot")
@click.argument("market", type=click.Choice(["TSE", "OTC", "ESB", "TIB", "PSB"]))
def snapshot(market):
    """Get market snapshot for a given market segment.

    \b
    Example:
      fubon market snapshot TSE
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        result = rest.snapshot.quotes(market=market)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("movers")
@click.argument("market", type=click.Choice(["TSE", "OTC", "ESB", "TIB", "PSB"]))
@click.option(
    "--direction", type=click.Choice(["up", "down"]), default="up", help="Price direction"
)
@click.option(
    "--change", type=click.Choice(["percent", "value"]), default="percent", help="Change type"
)
def movers(market, direction, change):
    """Get top movers (gainers/losers) for a market.

    \b
    Examples:
      fubon market movers TSE --direction up --change percent
      fubon market movers OTC --direction down
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        result = rest.snapshot.movers(market=market, direction=direction, change=change)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("actives")
@click.argument("market", type=click.Choice(["TSE", "OTC", "ESB", "TIB", "PSB"]))
@click.option(
    "--trade",
    type=click.Choice(["volume", "value"]),
    default="volume",
    help="Rank by volume or value",
)
def actives(market, trade):
    """Get most active stocks by volume or value.

    \b
    Example:
      fubon market actives TSE --trade value
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        result = rest.snapshot.actives(market=market, trade=trade)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("history")
@click.argument("symbol")
@click.option("--from", "from_date", default=None, help="Start date (yyyy-MM-dd)")
@click.option("--to", "to_date", default=None, help="End date (yyyy-MM-dd)")
@click.option(
    "--timeframe",
    type=click.Choice(["1", "5", "10", "15", "30", "60", "D", "W", "M"]),
    default="D",
    help="K-line timeframe",
)
@click.option("--adjusted", is_flag=True, help="Use adjusted prices")
def history(symbol, from_date, to_date, timeframe, adjusted):
    """Get historical candlestick data.

    \b
    Examples:
      fubon market history 2330 --from 2024-01-01 --to 2024-06-30
      fubon market history 0050 --timeframe W --adjusted
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {"symbol": symbol, "timeframe": timeframe}
        if from_date:
            kwargs["from"] = from_date
        if to_date:
            kwargs["to"] = to_date
        if adjusted:
            kwargs["adjusted"] = "true"
        result = rest.historical.candles(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("stats")
@click.argument("symbol")
def stats(symbol):
    """Get 52-week statistics for a stock.

    \b
    Example:
      fubon market stats 2330
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        result = rest.historical.stats(symbol=symbol)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("tickers")
@click.option(
    "--type",
    "ticker_type",
    type=click.Choice(["EQUITY", "INDEX", "WARRANT", "ODDLOT"]),
    default="EQUITY",
    help="Ticker type",
)
@click.option(
    "--exchange", type=click.Choice(["TWSE", "TPEx"]), default=None, help="Exchange filter"
)
def tickers(ticker_type, exchange):
    """List available tickers by type and exchange.

    \b
    Examples:
      fubon market tickers --type EQUITY --exchange TWSE
      fubon market tickers --type INDEX
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {"type": ticker_type}
        if exchange:
            kwargs["exchange"] = exchange
        result = rest.intraday.tickers(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


# --- Technical Indicators ---

@market_group.command("bbands")
@click.argument("symbol")
@click.option("--timeframe", type=click.Choice(["1", "5", "10", "15", "30", "60", "D", "W", "M"]), default="D", help="Timeframe")
@click.option("--period", type=int, default=None, help="Period (e.g. 20)")
@click.option("--std-dev", type=float, default=None, help="Standard deviation multiplier")
def bbands(symbol, timeframe, period, std_dev):
    """Get Bollinger Bands technical indicator.

    \b
    Example:
      fubon market bbands 2330 --timeframe D --period 20
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {"symbol": symbol, "timeframe": timeframe}
        if period is not None:
            kwargs["period"] = period
        if std_dev is not None:
            kwargs["stdDev"] = std_dev
        result = rest.technical.bbands(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("kdj")
@click.argument("symbol")
@click.option("--timeframe", type=click.Choice(["1", "5", "10", "15", "30", "60", "D", "W", "M"]), default="D", help="Timeframe")
@click.option("--period", type=int, default=None, help="Period")
def kdj(symbol, timeframe, period):
    """Get KDJ stochastic technical indicator.

    \b
    Example:
      fubon market kdj 2330
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {"symbol": symbol, "timeframe": timeframe}
        if period is not None:
            kwargs["period"] = period
        result = rest.technical.kdj(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("macd")
@click.argument("symbol")
@click.option("--timeframe", type=click.Choice(["1", "5", "10", "15", "30", "60", "D", "W", "M"]), default="D", help="Timeframe")
@click.option("--fast", type=int, default=None, help="Fast period")
@click.option("--slow", type=int, default=None, help="Slow period")
@click.option("--signal", type=int, default=None, help="Signal period")
def macd(symbol, timeframe, fast, slow, signal):
    """Get MACD technical indicator.

    \b
    Example:
      fubon market macd 2330 --fast 12 --slow 26 --signal 9
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {"symbol": symbol, "timeframe": timeframe}
        if fast is not None:
            kwargs["fastPeriod"] = fast
        if slow is not None:
            kwargs["slowPeriod"] = slow
        if signal is not None:
            kwargs["signalPeriod"] = signal
        result = rest.technical.macd(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("rsi")
@click.argument("symbol")
@click.option("--timeframe", type=click.Choice(["1", "5", "10", "15", "30", "60", "D", "W", "M"]), default="D", help="Timeframe")
@click.option("--period", type=int, default=None, help="Period (e.g. 14)")
def rsi(symbol, timeframe, period):
    """Get RSI (Relative Strength Index) technical indicator.

    \b
    Example:
      fubon market rsi 2330 --period 14
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {"symbol": symbol, "timeframe": timeframe}
        if period is not None:
            kwargs["period"] = period
        result = rest.technical.rsi(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("sma")
@click.argument("symbol")
@click.option("--timeframe", type=click.Choice(["1", "5", "10", "15", "30", "60", "D", "W", "M"]), default="D", help="Timeframe")
@click.option("--period", type=int, default=None, help="Period (e.g. 20)")
def sma(symbol, timeframe, period):
    """Get SMA (Simple Moving Average) technical indicator.

    \b
    Example:
      fubon market sma 2330 --period 20
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {"symbol": symbol, "timeframe": timeframe}
        if period is not None:
            kwargs["period"] = period
        result = rest.technical.sma(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


# --- Corporate Actions ---

@market_group.command("capital-changes")
@click.option("--from", "from_date", default=None, help="Start date (yyyy-MM-dd)")
@click.option("--to", "to_date", default=None, help="End date (yyyy-MM-dd)")
@click.option("--symbol", default=None, help="Filter by stock symbol")
def capital_changes(from_date, to_date, symbol):
    """Query capital change events (ETF splits, par value changes, capital reductions).

    \b
    Examples:
      fubon market capital-changes
      fubon market capital-changes --from 2024-01-01 --to 2024-12-31 --symbol 2330
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_stock(sdk)

    try:
        kwargs = {}
        if from_date:
            kwargs["from"] = from_date
        if to_date:
            kwargs["to"] = to_date
        if symbol:
            kwargs["symbol"] = symbol
        result = rest.corporate_actions.capital_changes(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


# --- Futures/Options Market Data ---

def _get_rest_futopt(sdk):
    """Initialize realtime and return the REST futopt client."""
    sdk.init_realtime()
    return sdk.marketdata.rest_client.futopt


@market_group.command("futopt-quote")
@click.argument("symbol")
def futopt_quote(symbol):
    """Get realtime quote for a futures/options contract.

    \b
    Example:
      fubon market futopt-quote TXFC5
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_futopt(sdk)

    try:
        result = rest.intraday.quote(symbol=symbol)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("futopt-ticker")
@click.argument("symbol")
def futopt_ticker(symbol):
    """Get ticker information for a futures/options contract.

    \b
    Example:
      fubon market futopt-ticker TXFC5
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_futopt(sdk)

    try:
        result = rest.intraday.ticker(symbol=symbol)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("futopt-tickers")
@click.option("--type", "ticker_type", default=None, help="Contract type filter")
def futopt_tickers(ticker_type):
    """List available futures/options contracts.

    \b
    Example:
      fubon market futopt-tickers
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_futopt(sdk)

    try:
        kwargs = {}
        if ticker_type:
            kwargs["type"] = ticker_type
        result = rest.intraday.tickers(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("futopt-candles")
@click.argument("symbol")
@click.option(
    "--timeframe",
    type=click.Choice(["1", "5", "10", "15", "30", "60"]),
    default="5",
    help="K-line timeframe in minutes",
)
def futopt_candles(symbol, timeframe):
    """Get intraday candlestick data for a futures/options contract.

    \b
    Example:
      fubon market futopt-candles TXFC5 --timeframe 5
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_futopt(sdk)

    try:
        result = rest.intraday.candles(symbol=symbol, timeframe=timeframe)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("futopt-trades")
@click.argument("symbol")
@click.option("--limit", type=int, default=None, help="Max number of trades")
@click.option("--offset", type=int, default=None, help="Offset for pagination")
def futopt_trades(symbol, limit, offset):
    """Get intraday trade ticks for a futures/options contract.

    \b
    Example:
      fubon market futopt-trades TXFC5 --limit 50
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_futopt(sdk)

    try:
        kwargs = {"symbol": symbol}
        if limit is not None:
            kwargs["limit"] = limit
        if offset is not None:
            kwargs["offset"] = offset
        result = rest.intraday.trades(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("futopt-volumes")
@click.argument("symbol")
def futopt_volumes(symbol):
    """Get price-volume distribution for a futures/options contract.

    \b
    Example:
      fubon market futopt-volumes TXFC5
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_futopt(sdk)

    try:
        result = rest.intraday.volumes(symbol=symbol)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("futopt-history")
@click.argument("symbol")
@click.option("--from", "from_date", default=None, help="Start date (yyyy-MM-dd)")
@click.option("--to", "to_date", default=None, help="End date (yyyy-MM-dd)")
@click.option(
    "--timeframe",
    type=click.Choice(["1", "5", "10", "15", "30", "60", "D", "W", "M"]),
    default="D",
    help="K-line timeframe",
)
def futopt_history(symbol, from_date, to_date, timeframe):
    """Get historical candlestick data for a futures/options contract.

    \b
    Example:
      fubon market futopt-history TXFC5 --from 2024-01-01 --to 2024-06-30
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_futopt(sdk)

    try:
        kwargs = {"symbol": symbol, "timeframe": timeframe}
        if from_date:
            kwargs["from"] = from_date
        if to_date:
            kwargs["to"] = to_date
        result = rest.historical.candles(**kwargs)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))


@market_group.command("futopt-stats")
@click.argument("symbol")
def futopt_stats(symbol):
    """Get statistics for a futures/options contract.

    \b
    Example:
      fubon market futopt-stats TXFC5
    """
    sdk, _ = get_sdk_and_accounts()
    rest = _get_rest_futopt(sdk)

    try:
        result = rest.historical.stats(symbol=symbol)
        output(result, success=True)
    except Exception as e:
        output(None, success=False, error=str(e))
