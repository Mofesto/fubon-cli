import types

import pytest


class Obj:
    """Mock object for testing with dynamic attributes."""

    def __init__(self, **kwargs):
        """Initialize with keyword arguments as attributes."""
        for k, v in kwargs.items():
            setattr(self, k, v)


class AnyEnum:
    """Mock enum that returns attribute name as value."""

    def __getattr__(self, name):
        """Return attribute name as value."""
        return name


class WsClient:
    """Mock WebSocket client for testing."""

    def __init__(self):
        """Initialize mock WebSocket client."""
        self.handlers = {}
        self.connected = False
        self.subscribed = None

    def on(self, event, handler):
        """Register event handler."""
        self.handlers[event] = handler

    def connect(self):
        """Simulate connection."""
        self.connected = True

    def subscribe(self, payload):
        """Simulate subscription with mock callbacks."""
        self.subscribed = payload
        if "message" in self.handlers:
            self.handlers["message"]("raw-text")
            self.handlers["message"]({"event": "message", "payload": payload})
        if "error" in self.handlers:
            self.handlers["error"]("mock-error")

    def disconnect(self):
        """Simulate disconnection."""
        self.connected = False


class ConditionClient:
    """Mock condition order client for testing."""

    def get_condition(self, acc):
        """Get conditions."""
        return Obj(data=[Obj(guid="g1")])

    def get_condition_by_guid(self, acc, guid):
        """Get condition by GUID."""
        return Obj(guid=guid)

    def cancel_condition(self, acc, guid):
        """Cancel condition."""
        return Obj(cancelled=guid)

    def get_condition_history(self, acc, from_date, to_date):
        """Get condition history."""
        return Obj(data=[Obj(from_date=from_date, to_date=to_date)])

    def get_trail_order(self, acc):
        """Get trail orders."""
        return Obj(data=[Obj(guid="t1")])

    def get_trail_history(self, acc, from_date, to_date):
        """Get trail order history."""
        return Obj(data=[Obj(from_date=from_date, to_date=to_date)])

    def get_day_trade_condition(self, acc):
        """Get day trade conditions."""
        return Obj(data=[Obj(guid="d1")])

    def get_time_slice_order(self, acc, batch_no):
        """Get time slice orders."""
        return Obj(batch_no=batch_no)

    def single_condition(self, acc, *args):
        """Place single condition order."""
        return Obj(ok=True)

    def multi_condition(self, acc, *args):
        """Place multi-condition order."""
        return Obj(ok=True)

    def tpsl_order(self, acc, **kwargs):
        """Place TP/SL order."""
        return Obj(ok=True)

    def trail_profit(self, acc, *args):
        """Place trail profit order."""
        return Obj(ok=True)

    def time_slice_order(self, acc, *args):
        """Place time slice order."""
        return Obj(ok=True)

    def day_trade_condition(self, acc, **kwargs):
        """Place day trade condition order."""
        return Obj(ok=True)

    def single_condition_with_tpsl(self, acc, **kwargs):
        """Place single condition order with TP/SL."""
        return Obj(ok=True)

    def multi_condition_with_tpsl(self, acc, **kwargs):
        """Place multi-condition order with TP/SL."""
        return Obj(ok=True)


class StockClient:
    """Mock stock order client for testing."""

    def __init__(self):
        """Initialize mock stock client."""
        self.condition = ConditionClient()

    def place_order(self, acc, order):
        """Place order."""
        return Obj(placed=True)

    def get_order_results(self, acc):
        """Get order results."""
        return Obj(data=[Obj(order_no="A1"), Obj(orderNo="A2")])

    def cancel_order(self, acc, target):
        """Cancel order."""
        return Obj(cancelled=True)

    def make_modify_price_obj(self, target, new_price):
        """Create price modification object."""
        return Obj(order_no="A1", price=new_price)

    def modify_price(self, acc, obj):
        """Modify order price."""
        return Obj(modified="price")

    def make_modify_quantity_obj(self, target, new_quantity):
        """Create quantity modification object."""
        return Obj(order_no="A1", quantity=new_quantity)

    def modify_quantity(self, acc, obj):
        """Modify order quantity."""
        return Obj(modified="quantity")

    def order_result_detail(self, acc, order_no):
        """Get order result detail."""
        return Obj(order_no=order_no)

    def order_history(self, acc, from_date, to_date):
        """Get order history."""
        return Obj(data=[Obj(order_no="H1")])

    def filled_history(self, acc, from_date, to_date):
        """Get filled history."""
        return Obj(data=[Obj(order_no="F1")])

    def batch_place_order(self, acc, orders):
        """Batch place orders."""
        return Obj(batch_place=len(orders))

    def batch_cancel_order(self, acc, targets):
        """Batch cancel orders."""
        return Obj(batch_cancel=len(targets))

    def batch_modify_price(self, acc, modify_objs):
        """Batch modify order prices."""
        return Obj(batch_modify_price=len(modify_objs))

    def batch_modify_volume(self, acc, modify_objs):
        """Batch modify order volumes."""
        return Obj(batch_modify_volume=len(modify_objs))

    def create_batch_order(self, acc, orders):
        """Create batch orders."""
        return Obj(batch_create=len(orders))

    def get_batch_order(self, acc, batch_no):
        """Get batch order info."""
        return Obj(batch_no=batch_no)

    def get_batch_order_list(self, acc):
        """Get batch order list."""
        return Obj(data=[Obj(batch_no="B1")])

    def query_symbol_quote(self, acc, symbol, market_type):
        """Query symbol quote."""
        return Obj(symbol=symbol, market_type=market_type)

    def query_symbol_snapshot(self, acc, **kwargs):
        """Query symbol snapshot."""
        return Obj(data=[Obj(symbol="2330")])

    def query_market_price_change(self, acc, market=None):
        """Query market price changes."""
        return Obj(market=market or "ALL")

    def day_trade_quota(self, acc):
        """Get day trade quota."""
        return Obj(quota=100)


class FutoptClient:
    """Mock futures/options client for testing."""

    def __init__(self):
        """Initialize mock futopt client."""
        self.condition = ConditionClient()

    def place_order(self, acc, order):
        """Place futopt order."""
        return Obj(placed=True)

    def order_result(self, acc):
        """Get order results."""
        return Obj(data=[Obj(order_no="F1")])

    def filled_result(self, acc):
        """Get filled results."""
        return Obj(data=[Obj(order_no="FF1")])

    def cancel_order(self, acc, target):
        """Cancel futopt order."""
        return Obj(cancelled=True)

    def modify_price(self, acc, target, new_price):
        """Modify order price."""
        return Obj(modified="price")

    def modify_volume(self, acc, target, qty):
        """Modify order volume."""
        return Obj(modified="volume")

    def inventories(self, acc):
        """Get futopt inventories."""
        return Obj(data=[Obj(symbol="TXF")])

    def settlements(self, acc):
        """Get settlements."""
        return Obj(total=1)


class AccountingClient:
    """Mock accounting client for testing."""

    def inventories(self, acc):
        """Get inventories."""
        return Obj(data=[Obj(stock_no="2330")])

    def unrealized_gains_and_loses(self, acc):
        """Get unrealized gains and losses."""
        return Obj(data=[Obj(stock_no="2330")])

    def query_settlement(self, acc, date_range):
        """Query settlement."""
        return Obj(range=date_range)

    def margin_quota(self, acc, symbol):
        """Get margin quota."""
        return Obj(symbol=symbol)

    def bank_remain(self, acc):
        """Get bank balance."""
        return Obj(balance=1)

    def maintenance(self, acc):
        """Get maintenance ratio."""
        return Obj(ratio=1)

    def realized_profit_loss(self, acc):
        """Get realized profit/loss."""
        return Obj(data=[Obj(stock_no="2330")])

    def realized_profit_loss_summary(self, acc):
        """Get realized profit/loss summary."""
        return Obj(total=1)


class IntradayAPI:
    """Mock intraday market data API."""

    def quote(self, **kwargs):
        """Get quote data."""
        return {"endpoint": "quote", **kwargs}

    def ticker(self, **kwargs):
        """Get ticker data."""
        return {"endpoint": "ticker", **kwargs}

    def candles(self, **kwargs):
        """Get candle data."""
        return {"endpoint": "candles", **kwargs}

    def trades(self, **kwargs):
        """Get trade data."""
        return {"endpoint": "trades", **kwargs}

    def volumes(self, **kwargs):
        """Get volume data."""
        return {"endpoint": "volumes", **kwargs}

    def tickers(self, **kwargs):
        """Get tickers data."""
        return {"endpoint": "tickers", **kwargs}


class SnapshotAPI:
    """Mock snapshot market data API."""

    def quotes(self, **kwargs):
        """Get snapshot quotes."""
        return {"endpoint": "snapshot.quotes", **kwargs}

    def movers(self, **kwargs):
        """Get market movers."""
        return {"endpoint": "snapshot.movers", **kwargs}

    def actives(self, **kwargs):
        """Get market actives."""
        return {"endpoint": "snapshot.actives", **kwargs}


class HistoricalAPI:
    """Mock historical market data API."""

    def candles(self, **kwargs):
        """Get historical candles."""
        return {"endpoint": "historical.candles", **kwargs}

    def stats(self, **kwargs):
        """Get historical stats."""
        return {"endpoint": "historical.stats", **kwargs}


class TechnicalAPI:
    """Mock technical analysis API."""

    def bbands(self, **kwargs):
        """Get Bollinger Bands."""
        return {"endpoint": "technical.bbands", **kwargs}

    def kdj(self, **kwargs):
        """Get KDJ indicator."""
        return {"endpoint": "technical.kdj", **kwargs}

    def macd(self, **kwargs):
        """Get MACD indicator."""
        return {"endpoint": "technical.macd", **kwargs}

    def rsi(self, **kwargs):
        """Get RSI indicator."""
        return {"endpoint": "technical.rsi", **kwargs}

    def sma(self, **kwargs):
        """Get SMA indicator."""
        return {"endpoint": "technical.sma", **kwargs}


class CorporateActionsAPI:
    """Mock corporate actions API."""

    def capital_changes(self, **kwargs):
        """Get capital changes."""
        return {"endpoint": "corporate_actions.capital_changes", **kwargs}


class RestStockClient:
    """Mock REST stock API client."""

    def __init__(self):
        """Initialize mock REST stock client."""
        self.intraday = IntradayAPI()
        self.snapshot = SnapshotAPI()
        self.historical = HistoricalAPI()
        self.technical = TechnicalAPI()
        self.corporate_actions = CorporateActionsAPI()


class RestFutoptClient(RestStockClient):
    """Mock REST futopt API client."""

    pass


class MockSDK:
    """Mock Fubon Neo SDK for testing."""

    def __init__(self):
        """Initialize mock SDK."""
        self.accounting = AccountingClient()
        self.stock = StockClient()
        self.futopt = FutoptClient()
        self.marketdata = Obj(
            rest_client=Obj(stock=RestStockClient(), futopt=RestFutoptClient()),
            websocket_client=Obj(stock=WsClient(), futopt=WsClient()),
        )
        self.callbacks = {}

    def init_realtime(self):
        """Initialize realtime connection."""
        return None

    def set_on_order(self, cb):
        """Set order callback."""
        self.callbacks["on_order"] = cb
        cb(200, {"id": "o1"})

    def set_on_order_changed(self, cb):
        """Set order changed callback."""
        self.callbacks["on_order_changed"] = cb
        cb(201, {"id": "oc1"})

    def set_on_filled(self, cb):
        """Set filled callback."""
        self.callbacks["on_filled"] = cb
        cb(202, {"id": "f1"})

    def set_on_event(self, cb):
        """Set event callback."""
        self.callbacks["on_event"] = cb
        cb(203, {"id": "e1"})


@pytest.fixture
def fake_account():
    """Provide fake account object for testing."""
    return Obj(account="617842", branch_no="20203")


@pytest.fixture
def fake_sdk():
    """Provide mock SDK instance for testing."""
    return MockSDK()


@pytest.fixture
def fake_fubon_modules(monkeypatch):
    """Mock Fubon Neo SDK modules for testing."""
    constant = types.ModuleType("fubon_neo.constant")
    constant.BSAction = AnyEnum()
    constant.CallPut = AnyEnum()
    constant.FutOptMarketType = AnyEnum()
    constant.FutOptOrderType = AnyEnum()
    constant.FutOptPriceType = AnyEnum()
    constant.MarketType = AnyEnum()
    constant.OrderType = AnyEnum()
    constant.PriceType = AnyEnum()
    constant.TimeInForce = AnyEnum()
    constant.StopSign = AnyEnum()
    constant.TradingType = AnyEnum()
    constant.TriggerContent = AnyEnum()
    constant.Operator = AnyEnum()
    constant.Direction = AnyEnum()
    constant.TimeSliceOrderType = AnyEnum()

    sdk_mod = types.ModuleType("fubon_neo.sdk")

    class _CtorObj:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def __str__(self):
            return str(self.kwargs)

    class _FubonSDK:
        def login(self, *args):
            return Obj(is_success=True, data=[Obj(name="Tester", account="617842")])

    sdk_mod.FubonSDK = _FubonSDK
    sdk_mod.Order = _CtorObj
    sdk_mod.FutOptOrder = _CtorObj
    sdk_mod.Condition = _CtorObj
    sdk_mod.TrailOrder = _CtorObj
    sdk_mod.SplitDescription = _CtorObj

    root = types.ModuleType("fubon_neo")

    monkeypatch.setitem(__import__("sys").modules, "fubon_neo", root)
    monkeypatch.setitem(__import__("sys").modules, "fubon_neo.constant", constant)
    monkeypatch.setitem(__import__("sys").modules, "fubon_neo.sdk", sdk_mod)

    return constant, sdk_mod
