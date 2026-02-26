import builtins
import importlib
import json
import sys
import types

from click.testing import CliRunner

from fubon_cli import core
from fubon_cli.commands import auth, condition, futopt, market, realtime, stock


def _patch_common(monkeypatch, fake_sdk, fake_account):
    for module in [market, stock, futopt, condition, realtime]:
        monkeypatch.setattr(module, "get_sdk_and_accounts", lambda: (fake_sdk, [fake_account]))
        if hasattr(module, "get_account"):
            monkeypatch.setattr(module, "get_account", lambda sdk, accounts, idx=0: accounts[0])


def test_package_version_fallback_importerror(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "fubon_cli._version":
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    sys.modules.pop("fubon_cli", None)
    mod = importlib.import_module("fubon_cli")
    assert mod.__version__ == "0.1.0"



def test_auth_login_failed_branch(monkeypatch, fake_fubon_modules):
    _constant, sdk_mod = fake_fubon_modules

    class BadSDK:
        def login(self, *args):
            return types.SimpleNamespace(is_success=False, message="bad", data=[])

    monkeypatch.setattr(sdk_mod, "FubonSDK", BadSDK)

    runner = CliRunner()
    result = runner.invoke(
        auth.auth_group,
        ["--id", "A123", "--password", "pw", "--cert-path", "c.pfx"],
    )
    assert result.exit_code != 0
    assert "Login failed" in result.output



def test_market_odd_lot_branches(monkeypatch, fake_sdk, fake_account):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    runner = CliRunner()

    r1 = runner.invoke(market.market_group, ["ticker", "2330", "--odd-lot"])
    assert r1.exit_code == 0
    assert '"type": "oddlot"' in r1.output

    r2 = runner.invoke(market.market_group, ["candles", "2330", "--odd-lot"])
    assert r2.exit_code == 0
    assert '"type": "oddlot"' in r2.output



def test_futopt_not_found_branches(monkeypatch, fake_sdk, fake_account):
    _patch_common(monkeypatch, fake_sdk, fake_account)

    fake_sdk.futopt.order_result = lambda acc: types.SimpleNamespace(data=[])
    runner = CliRunner()

    r1 = runner.invoke(futopt.futopt_group, ["modify-price", "X", "10"])
    assert r1.exit_code != 0

    r2 = runner.invoke(futopt.futopt_group, ["modify-quantity", "X", "2"])
    assert r2.exit_code != 0



def test_stock_user_def_and_not_found_branches(monkeypatch, fake_sdk, fake_account, fake_fubon_modules):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    runner = CliRunner()

    r_buy = runner.invoke(
        stock.stock_group,
        ["buy", "2330", "1", "--price", "10", "--user-def", "TAG1"],
    )
    assert r_buy.exit_code == 0

    r_batch_place = runner.invoke(
        stock.stock_group,
        [
            "batch-place",
            '[{"symbol":"2330","buy_sell":"Buy","price":"10","quantity":1,"user_def":"X"}]',
        ],
    )
    assert r_batch_place.exit_code == 0

    r_batch_create = runner.invoke(
        stock.stock_group,
        [
            "batch-create",
            '[{"symbol":"2330","buy_sell":"Buy","price":"10","quantity":1,"user_def":"X"}]',
        ],
    )
    assert r_batch_create.exit_code == 0

    # not found branches
    r_mod_price = runner.invoke(stock.stock_group, ["modify-price", "NOPE", "10"])
    assert r_mod_price.exit_code != 0

    r_mod_qty = runner.invoke(stock.stock_group, ["modify-quantity", "NOPE", "2"])
    assert r_mod_qty.exit_code != 0

    r_batch_cancel = runner.invoke(stock.stock_group, ["batch-cancel", "NOPE"])
    assert r_batch_cancel.exit_code != 0

    r_batch_mod_price = runner.invoke(
        stock.stock_group,
        ["batch-modify-price", '[{"order_no":"NOPE","price":"11"}]'],
    )
    assert r_batch_mod_price.exit_code != 0

    r_batch_mod_qty = runner.invoke(
        stock.stock_group,
        ["batch-modify-quantity", '[{"order_no":"NOPE","quantity":2}]'],
    )
    assert r_batch_mod_qty.exit_code != 0



def test_condition_build_stock_order_user_def(fake_fubon_modules):
    constant, sdk_mod = fake_fubon_modules
    order = condition._build_stock_order(
        {
            "buy_sell": "Buy",
            "symbol": "2330",
            "price": "10",
            "quantity": 1,
            "price_type": "limit",
            "time_in_force": "ROD",
            "order_type": "stock",
            "market_type": "common",
            "user_def": "TAG",
        },
        constant.BSAction,
        constant.PriceType,
        constant.TimeInForce,
        constant.OrderType,
        constant.MarketType,
        sdk_mod.Order,
    )
    assert "user_def" in order.kwargs



def test_realtime_signal_handlers_and_callbacks(monkeypatch, fake_sdk, fake_account):
    _patch_common(monkeypatch, fake_sdk, fake_account)
    runner = CliRunner()

    def trigger_handler(_sig, handler):
        # Execute handler immediately to cover disconnect + sys.exit paths.
        handler(2, None)

    monkeypatch.setattr(realtime.signal, "signal", trigger_handler)

    result1 = runner.invoke(realtime.realtime_group, ["subscribe", "2330"])
    assert result1.exit_code == 0

    result2 = runner.invoke(realtime.realtime_group, ["subscribe-futopt", "TXFC5"])
    assert result2.exit_code == 0

    monkeypatch.setattr(realtime.signal, "signal", lambda *args, **kwargs: None)
    monkeypatch.setattr(realtime.time, "sleep", lambda _x: (_ for _ in ()).throw(KeyboardInterrupt()))
    result3 = runner.invoke(realtime.realtime_group, ["callbacks"])
    assert result3.exit_code == 0

    # Cover callbacks handle_signal branch (line with sys.exit(0)).
    monkeypatch.setattr(realtime.signal, "signal", trigger_handler)
    result4 = runner.invoke(realtime.realtime_group, ["callbacks"])
    assert result4.exit_code == 0



def test_core_parse_remaining_branches():
    # include token without colon to hit continue branch and raw enum-like value branch
    parsed = core._parse_sdk_repr("Obj { a: 1, invalid, mode: SomeEnum.Value }")
    assert parsed["a"] == 1
    assert parsed["mode"] == "SomeEnum.Value"

    parsed_bool = core._parse_sdk_repr("Obj { ok: False }")
    assert parsed_bool["ok"] is False

    class TextOnly:
        def __str__(self):
            return "plain-text"

    assert core.obj_to_dict(TextOnly()) == "plain-text"
