import pytest
from click.testing import CliRunner

from fubon_cli.commands import account, auth, condition, futopt, market, realtime, stock


def _patch_common(monkeypatch, fake_sdk, fake_account):
    for module in [account, market, stock, realtime, futopt, condition]:
        monkeypatch.setattr(module, "get_sdk_and_accounts", lambda: (fake_sdk, [fake_account]))
        if hasattr(module, "get_account"):
            monkeypatch.setattr(module, "get_account", lambda sdk, accounts, idx=0: accounts[0])


@pytest.mark.parametrize(
    "args",
    [
        ["inventory"],
        ["unrealized"],
        ["settlement", "--range", "1d"],
        ["margin-quota", "2330"],
        ["bank-balance"],
        ["maintenance"],
        ["realized"],
        ["realized-summary"],
        ["day-trade-quota"],
    ],
)
def test_account_commands_success(monkeypatch, fake_sdk, fake_account, args):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    runner = CliRunner()
    result = runner.invoke(account.account_group, args)
    assert result.exit_code == 0
    assert '"success": true' in result.output


@pytest.mark.parametrize(
    "args",
    [
        ["quote", "2330", "--odd-lot"],
        ["ticker", "2330"],
        ["candles", "2330", "--timeframe", "5"],
        ["trades", "2330", "--limit", "5", "--offset", "0"],
        ["volumes", "2330"],
        ["snapshot", "TSE"],
        ["movers", "TSE", "--direction", "up", "--change", "percent"],
        ["actives", "TSE", "--trade", "volume"],
        ["history", "2330", "--from", "2024-01-01", "--to", "2024-01-02", "--timeframe", "D", "--adjusted"],
        ["stats", "2330"],
        ["tickers", "--type", "EQUITY", "--exchange", "TWSE"],
        ["bbands", "2330", "--timeframe", "D", "--period", "20", "--std-dev", "2.0"],
        ["kdj", "2330", "--period", "9"],
        ["macd", "2330", "--fast", "12", "--slow", "26", "--signal", "9"],
        ["rsi", "2330", "--period", "14"],
        ["sma", "2330", "--period", "20"],
        ["capital-changes", "--from", "2024-01-01", "--to", "2024-12-31", "--symbol", "2330"],
        ["futopt-quote", "TXFC5"],
        ["futopt-ticker", "TXFC5"],
        ["futopt-tickers", "--type", "future"],
        ["futopt-candles", "TXFC5", "--timeframe", "5"],
        ["futopt-trades", "TXFC5", "--limit", "10", "--offset", "0"],
        ["futopt-volumes", "TXFC5"],
        ["futopt-history", "TXFC5", "--from", "2024-01-01", "--to", "2024-01-02", "--timeframe", "D"],
        ["futopt-stats", "TXFC5"],
    ],
)
def test_market_commands_success(monkeypatch, fake_sdk, fake_account, args):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    runner = CliRunner()
    result = runner.invoke(market.market_group, args)
    assert result.exit_code == 0
    assert '"success": true' in result.output


def test_market_command_error_branch(monkeypatch, fake_sdk, fake_account):
    _patch_common(monkeypatch, fake_sdk, fake_account)

    def boom(**kwargs):
        raise RuntimeError("boom")

    fake_sdk.marketdata.rest_client.stock.intraday.quote = boom
    runner = CliRunner()
    result = runner.invoke(market.market_group, ["quote", "2330"])
    assert result.exit_code == 0
    assert '"success": false' in result.output


@pytest.mark.parametrize(
    "args",
    [
        ["buy", "2330", "1", "--price", "10"],
        ["sell", "2330", "1", "--price", "10"],
        ["orders"],
        ["cancel", "A1"],
        ["modify-price", "A1", "10"],
        ["modify-quantity", "A1", "2"],
        ["order-detail", "A1"],
        ["order-history", "--from", "2024-01-01", "--to", "2024-01-31"],
        ["filled-history", "--from", "2024-01-01", "--to", "2024-01-31"],
        ["batch-place", '[{"symbol":"2330","buy_sell":"Buy","price":"10","quantity":1,"price_type":"limit","time_in_force":"ROD","order_type":"stock","market_type":"common"}]'],
        ["batch-cancel", "A1"],
        ["batch-modify-price", '[{"order_no":"A1","price":"11"}]'],
        ["batch-modify-quantity", '[{"order_no":"A1","quantity":2}]'],
        ["batch-create", '[{"symbol":"2330","buy_sell":"Buy","price":"10","quantity":1,"price_type":"limit","time_in_force":"ROD","order_type":"stock","market_type":"common"}]'],
        ["batch-get", "B1"],
        ["batch-list"],
        ["symbol-quote", "2330", "--market-type", "common"],
        ["symbol-snapshot", "--market-type", "common", "--stock-types", "stock,margin"],
        ["price-change", "--market", "TSE"],
        ["price-change"],
    ],
)
def test_stock_commands_success(monkeypatch, fake_sdk, fake_account, fake_fubon_modules, args):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    runner = CliRunner()
    result = runner.invoke(stock.stock_group, args)
    assert result.exit_code == 0
    assert '"success": true' in result.output


def test_stock_missing_price_and_not_found(monkeypatch, fake_sdk, fake_account, fake_fubon_modules):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    runner = CliRunner()

    missing_price = runner.invoke(stock.stock_group, ["buy", "2330", "1"])
    assert missing_price.exit_code != 0
    assert "--price is required" in missing_price.output

    not_found = runner.invoke(stock.stock_group, ["cancel", "ZZZ"])
    assert not_found.exit_code != 0


def test_stock_error_branch(monkeypatch, fake_sdk, fake_account, fake_fubon_modules):
    _patch_common(monkeypatch, fake_sdk, fake_account)

    def boom(acc):
        raise RuntimeError("boom")

    fake_sdk.stock.get_order_results = boom
    runner = CliRunner()
    result = runner.invoke(stock.stock_group, ["orders"])
    assert result.exit_code == 0
    assert '"success": false' in result.output


@pytest.mark.parametrize(
    "args",
    [
        ["buy", "TXFC5", "1", "--price", "10"],
        ["sell", "TXFC5", "1", "--price", "10"],
        ["orders"],
        ["filled"],
        ["cancel", "F1"],
        ["modify-price", "F1", "10"],
        ["modify-quantity", "F1", "2"],
        ["inventories"],
        ["settlements"],
    ],
)
def test_futopt_commands_success(monkeypatch, fake_sdk, fake_account, fake_fubon_modules, args):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    runner = CliRunner()
    result = runner.invoke(futopt.futopt_group, args)
    assert result.exit_code == 0
    assert '"success": true' in result.output


def test_futopt_missing_price_and_not_found(monkeypatch, fake_sdk, fake_account, fake_fubon_modules):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    runner = CliRunner()

    missing_price = runner.invoke(futopt.futopt_group, ["buy", "TXFC5", "1"])
    assert missing_price.exit_code != 0

    not_found = runner.invoke(futopt.futopt_group, ["cancel", "ZZZ"])
    assert not_found.exit_code != 0


@pytest.mark.parametrize(
    "args",
    [
        ["list"],
        ["get", "GUID-1"],
        ["cancel", "GUID-1"],
        ["history", "--from", "2024-01-01", "--to", "2024-01-31"],
        ["trail-list"],
        ["trail-history", "--from", "2024-01-01", "--to", "2024-01-31"],
        ["timeslice-get", "B1"],
        ["day-trade-list"],
        ["place-single", '{"start_date":"2024-01-01","end_date":"2024-01-31","stop_sign":"Full","condition":{"trading_type":"Stock","symbol":"2330","trigger_content":"LastPrice","price":"10","operator":"Greater"},"order":{"buy_sell":"Buy","symbol":"2330","price":"10","quantity":1,"price_type":"limit","time_in_force":"ROD","order_type":"stock","market_type":"common"}}'],
        ["place-multi", '{"start_date":"2024-01-01","end_date":"2024-01-31","stop_sign":"Full","conditions":[{"trading_type":"Stock","symbol":"2330","trigger_content":"LastPrice","price":"10","operator":"Greater"}],"order":{"buy_sell":"Buy","symbol":"2330","price":"10","quantity":1,"price_type":"limit","time_in_force":"ROD","order_type":"stock","market_type":"common"}}'],
        ["place-tpsl", '{"symbol":"2330"}'],
        ["place-trail", '{"start_date":"2024-01-01","end_date":"2024-01-31","stop_sign":"Full","trail_order":{"symbol":"2330","price":"10","direction":"Up","tick_num":2,"buy_sell":"Buy","quantity":1,"price_type":"Limit","diff":1,"time_in_force":"ROD","order_type":"Stock"}}'],
        ["place-timeslice", '{"start_date":"2024-01-01","end_date":"2024-01-31","stop_sign":"Full","split":{"method":"EqualQty","interval":60,"single_quantity":1,"total_quantity":2,"start_time":"09:00:00"},"order":{"buy_sell":"Buy","symbol":"2330","price":"10","quantity":1,"price_type":"limit","time_in_force":"ROD","order_type":"stock","market_type":"common"}}'],
        ["place-day-trade", '{"symbol":"2330"}'],
        ["place-single-tpsl", '{"symbol":"2330"}'],
        ["place-multi-tpsl", '{"symbol":"2330"}'],
        ["list", "--futopt"],
    ],
)
def test_condition_commands_success(monkeypatch, fake_sdk, fake_account, fake_fubon_modules, args):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    runner = CliRunner()
    result = runner.invoke(condition.condition_group, args)
    assert result.exit_code == 0
    assert '"success": true' in result.output


def test_condition_error_branch(monkeypatch, fake_sdk, fake_account):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    fake_sdk.stock.condition.get_condition = lambda acc: (_ for _ in ()).throw(RuntimeError("boom"))
    runner = CliRunner()
    result = runner.invoke(condition.condition_group, ["list"])
    assert result.exit_code == 0
    assert '"success": false' in result.output


def test_realtime_commands(monkeypatch, fake_sdk, fake_account):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    monkeypatch.setattr(realtime.signal, "signal", lambda *args, **kwargs: None)

    def stop_once(_):
        raise KeyboardInterrupt

    monkeypatch.setattr(realtime.time, "sleep", stop_once)
    runner = CliRunner()

    result_stock = runner.invoke(realtime.realtime_group, ["subscribe", "2330", "--channel", "trades"])
    assert result_stock.exit_code == 0
    assert '"event": "error"' in result_stock.output

    result_futopt = runner.invoke(
        realtime.realtime_group, ["subscribe-futopt", "TXFC5", "--channel", "trades"]
    )
    assert result_futopt.exit_code == 0

    result_callbacks = runner.invoke(realtime.realtime_group, ["callbacks", "--account-index", "10"])
    assert result_callbacks.exit_code == 0
    assert '"event": "listening"' in result_callbacks.output


def test_auth_login_status_logout(monkeypatch, fake_fubon_modules):
    runner = CliRunner()

    missing = runner.invoke(auth.auth_group, [])
    assert missing.exit_code != 0

    saved = {}
    monkeypatch.setattr(auth, "save_session", lambda pid, pw, cp, cpass: saved.update(pid=pid))
    login_ok = runner.invoke(
        auth.auth_group,
        ["--id", "A123", "--password", "pw", "--cert-path", "c.pfx", "--cert-password", "cpw"],
    )
    assert login_ok.exit_code == 0
    assert '"success": true' in login_ok.output
    assert saved["pid"] == "A123"

    monkeypatch.setattr(auth, "load_session", lambda: None)
    status_no = runner.invoke(auth.auth_group, ["status"])
    assert '"logged_in": false' in status_no.output

    monkeypatch.setattr(
        auth,
        "load_session",
        lambda: {"personal_id": "A123456789", "cert_path": "c.pfx"},
    )
    status_yes = runner.invoke(auth.auth_group, ["status"])
    assert '"logged_in": true' in status_yes.output

    cleared = {}
    monkeypatch.setattr(auth, "clear_session", lambda: cleared.update(ok=True))
    logout_ok = runner.invoke(auth.auth_group, ["logout"])
    assert logout_ok.exit_code == 0
    assert cleared["ok"] is True


def test_auth_import_error(monkeypatch):
    import builtins

    runner = CliRunner()
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "fubon_neo.sdk":
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = runner.invoke(
        auth.auth_group,
        ["--id", "A123", "--password", "pw", "--cert-path", "c.pfx"],
    )
    assert result.exit_code != 0
    assert '"success": false' in result.output
