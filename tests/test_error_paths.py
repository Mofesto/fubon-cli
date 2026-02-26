from click.testing import CliRunner

from fubon_cli.commands import account, condition, futopt, market, stock


class RaiseAny:
    """Mock class that raises exceptions."""

    def __getattr__(self, _name):
        """Return self for chaining."""
        return self

    def __call__(self, *args, **kwargs):
        """Raise RuntimeError when called."""
        raise RuntimeError("boom")


def _patch_common(monkeypatch, fake_sdk, fake_account):
    for module in [account, market, stock, futopt, condition]:
        monkeypatch.setattr(module, "get_sdk_and_accounts", lambda: (fake_sdk, [fake_account]))
        if hasattr(module, "get_account"):
            monkeypatch.setattr(module, "get_account", lambda sdk, accounts, idx=0: accounts[0])


def test_account_error_paths(monkeypatch, fake_sdk, fake_account):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    fake_sdk.accounting = RaiseAny()
    fake_sdk.stock = RaiseAny()
    runner = CliRunner()

    commands = [
        ["inventory"],
        ["unrealized"],
        ["settlement"],
        ["margin-quota", "2330"],
        ["bank-balance"],
        ["maintenance"],
        ["realized"],
        ["realized-summary"],
        ["day-trade-quota"],
    ]

    for cmd in commands:
        result = runner.invoke(account.account_group, cmd)
        assert result.exit_code == 0
        assert '"success": false' in result.output


def test_market_error_paths(monkeypatch, fake_sdk, fake_account):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    fake_sdk.marketdata.rest_client.stock = RaiseAny()
    fake_sdk.marketdata.rest_client.futopt = RaiseAny()
    runner = CliRunner()

    commands = [
        ["quote", "2330"],
        ["ticker", "2330"],
        ["candles", "2330"],
        ["trades", "2330"],
        ["volumes", "2330"],
        ["snapshot", "TSE"],
        ["movers", "TSE"],
        ["actives", "TSE"],
        ["history", "2330"],
        ["stats", "2330"],
        ["tickers"],
        ["bbands", "2330"],
        ["kdj", "2330"],
        ["macd", "2330"],
        ["rsi", "2330"],
        ["sma", "2330"],
        ["capital-changes"],
        ["futopt-quote", "TXFC5"],
        ["futopt-ticker", "TXFC5"],
        ["futopt-tickers"],
        ["futopt-candles", "TXFC5"],
        ["futopt-trades", "TXFC5"],
        ["futopt-volumes", "TXFC5"],
        ["futopt-history", "TXFC5"],
        ["futopt-stats", "TXFC5"],
    ]

    for cmd in commands:
        result = runner.invoke(market.market_group, cmd)
        assert result.exit_code == 0
        assert '"success": false' in result.output


def test_stock_error_paths(monkeypatch, fake_sdk, fake_account, fake_fubon_modules):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    fake_sdk.stock = RaiseAny()
    runner = CliRunner()

    commands = [
        ["buy", "2330", "1", "--price", "10"],
        ["sell", "2330", "1", "--price", "10"],
        ["orders"],
        ["cancel", "A1"],
        ["modify-price", "A1", "10"],
        ["modify-quantity", "A1", "2"],
        ["order-detail", "A1"],
        ["order-history", "--from", "2024-01-01", "--to", "2024-01-31"],
        ["filled-history", "--from", "2024-01-01", "--to", "2024-01-31"],
        ["batch-place", '[{"symbol":"2330","buy_sell":"Buy","price":"10","quantity":1}]'],
        ["batch-cancel", "A1"],
        ["batch-modify-price", '[{"order_no":"A1","price":"11"}]'],
        ["batch-modify-quantity", '[{"order_no":"A1","quantity":2}]'],
        ["batch-create", '[{"symbol":"2330","buy_sell":"Buy","price":"10","quantity":1}]'],
        ["batch-get", "B1"],
        ["batch-list"],
        ["symbol-quote", "2330"],
        ["symbol-snapshot"],
        ["price-change"],
    ]

    for cmd in commands:
        result = runner.invoke(stock.stock_group, cmd)
        assert result.exit_code == 0
        assert '"success": false' in result.output


def test_futopt_error_paths(monkeypatch, fake_sdk, fake_account, fake_fubon_modules):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    fake_sdk.futopt = RaiseAny()
    runner = CliRunner()

    commands = [
        ["buy", "TXFC5", "1", "--price", "10"],
        ["sell", "TXFC5", "1", "--price", "10"],
        ["orders"],
        ["filled"],
        ["cancel", "F1"],
        ["modify-price", "F1", "10"],
        ["modify-quantity", "F1", "2"],
        ["inventories"],
        ["settlements"],
    ]

    for cmd in commands:
        result = runner.invoke(futopt.futopt_group, cmd)
        assert result.exit_code == 0
        assert '"success": false' in result.output


def test_condition_error_paths(monkeypatch, fake_sdk, fake_account, fake_fubon_modules):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    fake_sdk.stock.condition = RaiseAny()
    fake_sdk.futopt.condition = RaiseAny()
    runner = CliRunner()

    commands = [
        ["list"],
        ["get", "GUID-1"],
        ["cancel", "GUID-1"],
        ["history", "--from", "2024-01-01", "--to", "2024-01-31"],
        ["trail-list"],
        ["trail-history", "--from", "2024-01-01", "--to", "2024-01-31"],
        ["timeslice-get", "B1"],
        ["day-trade-list"],
        ["place-single", '{"start_date":"2024-01-01","end_date":"2024-01-31","stop_sign":"Full","condition":{"trading_type":"Stock","symbol":"2330","trigger_content":"LastPrice","price":"10","operator":"Greater"},"order":{"buy_sell":"Buy","symbol":"2330","price":"10","quantity":1}}'],
        ["place-multi", '{"start_date":"2024-01-01","end_date":"2024-01-31","stop_sign":"Full","conditions":[{"trading_type":"Stock","symbol":"2330","trigger_content":"LastPrice","price":"10","operator":"Greater"}],"order":{"buy_sell":"Buy","symbol":"2330","price":"10","quantity":1}}'],
        ["place-tpsl", '{"symbol":"2330"}'],
        ["place-trail", '{"start_date":"2024-01-01","end_date":"2024-01-31","stop_sign":"Full","trail_order":{"symbol":"2330","price":"10","direction":"Up","tick_num":2,"buy_sell":"Buy","quantity":1}}'],
        ["place-timeslice", '{"start_date":"2024-01-01","end_date":"2024-01-31","stop_sign":"Full","split":{"method":"EqualQty","interval":60,"single_quantity":1,"total_quantity":2,"start_time":"09:00:00"},"order":{"buy_sell":"Buy","symbol":"2330","price":"10","quantity":1}}'],
        ["place-day-trade", '{"symbol":"2330"}'],
        ["place-single-tpsl", '{"symbol":"2330"}'],
        ["place-multi-tpsl", '{"symbol":"2330"}'],
    ]

    for cmd in commands:
        result = runner.invoke(condition.condition_group, cmd)
        assert result.exit_code == 0
        assert '"success": false' in result.output
