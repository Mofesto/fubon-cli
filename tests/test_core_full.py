import json
import types

import pytest

from fubon_cli import core


def test_session_save_load_clear(tmp_path, monkeypatch):
    session_file = tmp_path / "session.json"
    monkeypatch.setattr(core, "SESSION_FILE", str(session_file))

    core.save_session("A123", "pw", "c.pfx", "cpw")
    loaded = core.load_session()
    assert loaded["personal_id"] == "A123"

    core.clear_session()
    assert core.load_session() is None


def test_get_account_ok_and_out_of_range(capsys):
    accounts = [types.SimpleNamespace(account="1")]
    assert core.get_account(None, accounts, 0).account == "1"

    with pytest.raises(SystemExit):
        core.get_account(None, accounts, 2)
    out = capsys.readouterr().out
    assert "out of range" in out


def test_obj_to_dict_and_parse_repr():
    class Obj:
        def __init__(self):
            self.a = 1
            self._hidden = 2

    assert core.obj_to_dict(None) is None
    assert core.obj_to_dict("x") == "x"
    assert core.obj_to_dict([1, {"a": 2}]) == [1, {"a": 2}]
    assert core.obj_to_dict(Obj()) == {"a": 1}

    parsed = core._parse_sdk_repr(
        'Order { id: 1, ok: True, price: 10.5, nested: Nested { code: "A" }, none_v: None }'
    )
    assert parsed["id"] == 1
    assert parsed["ok"] is True
    assert parsed["price"] == 10.5
    assert parsed["nested"]["code"] == "A"
    assert parsed["none_v"] is None


def test_parse_repr_no_match_and_empty_block():
    assert core._parse_sdk_repr("just-text") == "just-text"
    assert core._parse_sdk_repr("Obj {}") == {}


def test_format_result_and_output(capsys):
    result = types.SimpleNamespace(v=1)
    as_json = core.format_result(result, as_json=True)
    assert '"v": 1' in as_json

    as_text = core.format_result(result, as_json=False)
    assert "{'v': 1}" in as_text

    core.output({"k": 1}, success=True)
    text = capsys.readouterr().out
    payload = json.loads(text)
    assert payload["success"] is True
    assert payload["data"]["k"] == 1


def test_get_sdk_and_accounts_not_logged_in(monkeypatch):
    monkeypatch.setattr(core, "load_session", lambda: None)
    with pytest.raises(SystemExit):
        core.get_sdk_and_accounts()


def test_get_sdk_and_accounts_login_fail(monkeypatch):
    monkeypatch.setattr(
        core,
        "load_session",
        lambda: {
            "personal_id": "A",
            "password": "P",
            "cert_path": "C",
            "cert_password": "",
        },
    )

    class SDK:
        def login(self, *args):
            return types.SimpleNamespace(is_success=False, message="bad")

    monkeypatch.setattr(core, "_import_sdk", lambda: (SDK, object))

    with pytest.raises(SystemExit):
        core.get_sdk_and_accounts()


def test_get_sdk_and_accounts_login_success(monkeypatch):
    monkeypatch.setattr(
        core,
        "load_session",
        lambda: {
            "personal_id": "A",
            "password": "P",
            "cert_path": "C",
            "cert_password": "CP",
        },
    )

    class SDK:
        def login(self, *args):
            assert args == ("A", "P", "C", "CP")
            return types.SimpleNamespace(is_success=True, data=[types.SimpleNamespace(account="1")])

    monkeypatch.setattr(core, "_import_sdk", lambda: (SDK, object))

    sdk, accounts = core.get_sdk_and_accounts()
    assert isinstance(sdk, SDK)
    assert accounts[0].account == "1"


def test_import_sdk_import_error(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("fubon_neo"):
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(SystemExit):
        core._import_sdk()


def test_import_sdk_success(fake_fubon_modules):
    sdk_cls, order_cls = core._import_sdk()
    assert sdk_cls is not None
    assert order_cls is not None
