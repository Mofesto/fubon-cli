"""Tests for authentication commands and core session management."""

import json
import sys
import types

import pytest
from click.testing import CliRunner

import fubon_cli.core as core
from fubon_cli.commands.auth import auth_group


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _Obj:
    """Minimal mock object."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def _make_sdk_module(login_success=True, apikey_success=True, raise_import=False):
    """Build a minimal fake fubon_neo.sdk module."""
    sdk_mod = types.ModuleType("fubon_neo.sdk")

    class _FubonSDK:
        def login(self, *args):
            if not login_success:
                return _Obj(is_success=False, message="bad password")
            return _Obj(
                is_success=True,
                data=[_Obj(name="Tester", account="617842", branch_no="20203", account_type="stock")],
            )

        def apikey_login(self, *args):
            if not apikey_success:
                return _Obj(is_success=False, message="bad api key")
            return _Obj(
                is_success=True,
                data=[_Obj(name="Tester", account="617842", branch_no="20203", account_type="stock")],
            )

    sdk_mod.FubonSDK = _FubonSDK
    return sdk_mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def session_file(tmp_path, monkeypatch):
    """Redirect session file to a temp path."""
    path = str(tmp_path / "session.json")
    monkeypatch.setattr(core, "SESSION_FILE", path)
    return path


@pytest.fixture
def patch_sdk(monkeypatch):
    """Inject working fake SDK into sys.modules."""
    sdk_mod = _make_sdk_module()
    root = types.ModuleType("fubon_neo")
    constant = types.ModuleType("fubon_neo.constant")
    monkeypatch.setitem(sys.modules, "fubon_neo", root)
    monkeypatch.setitem(sys.modules, "fubon_neo.constant", constant)
    monkeypatch.setitem(sys.modules, "fubon_neo.sdk", sdk_mod)
    return sdk_mod


# ---------------------------------------------------------------------------
# Password login (auth_group)
# ---------------------------------------------------------------------------

class TestPasswordLogin:
    """Tests for password-based login."""

    def test_password_login_success(self, monkeypatch, session_file, patch_sdk):
        runner = CliRunner()
        result = runner.invoke(
            auth_group,
            ["--id", "A123456789", "--password", "pw", "--cert-path", "/cert.p12"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "accounts" in data["data"]

    def test_password_login_with_cert_password(self, monkeypatch, session_file, patch_sdk):
        runner = CliRunner()
        result = runner.invoke(
            auth_group,
            [
                "--id", "A123456789",
                "--password", "pw",
                "--cert-path", "/cert.p12",
                "--cert-password", "certpw",
            ],
        )
        assert result.exit_code == 0
        assert json.loads(result.output)["success"] is True

    def test_password_login_saves_session(self, monkeypatch, session_file, patch_sdk):
        runner = CliRunner()
        runner.invoke(
            auth_group,
            ["--id", "A123456789", "--password", "pw", "--cert-path", "/cert.p12"],
        )
        with open(session_file) as f:
            saved = json.load(f)
        assert saved["login_type"] == "password"
        assert saved["personal_id"] == "A123456789"
        assert saved["password"] == "pw"
        assert saved["api_key"] is None

    def test_password_login_sdk_failure(self, monkeypatch, session_file):
        sdk_mod = _make_sdk_module(login_success=False)
        root = types.ModuleType("fubon_neo")
        constant = types.ModuleType("fubon_neo.constant")
        monkeypatch.setitem(sys.modules, "fubon_neo", root)
        monkeypatch.setitem(sys.modules, "fubon_neo.constant", constant)
        monkeypatch.setitem(sys.modules, "fubon_neo.sdk", sdk_mod)

        runner = CliRunner()
        result = runner.invoke(
            auth_group,
            ["--id", "A123456789", "--password", "bad", "--cert-path", "/cert.p12"],
        )
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["success"] is False
        assert "Login failed" in data["error"]

    def test_missing_id(self, session_file, patch_sdk):
        runner = CliRunner()
        result = runner.invoke(
            auth_group, ["--password", "pw", "--cert-path", "/cert.p12"]
        )
        assert result.exit_code == 1
        assert json.loads(result.output)["success"] is False

    def test_missing_cert_path(self, session_file, patch_sdk):
        runner = CliRunner()
        result = runner.invoke(
            auth_group, ["--id", "A123456789", "--password", "pw"]
        )
        assert result.exit_code == 1
        assert json.loads(result.output)["success"] is False

    def test_missing_both_password_and_apikey(self, session_file, patch_sdk):
        runner = CliRunner()
        result = runner.invoke(
            auth_group, ["--id", "A123456789", "--cert-path", "/cert.p12"]
        )
        assert result.exit_code == 1
        assert json.loads(result.output)["success"] is False

    def test_sdk_not_installed(self, monkeypatch, session_file):
        monkeypatch.setitem(sys.modules, "fubon_neo", None)
        monkeypatch.setitem(sys.modules, "fubon_neo.sdk", None)
        monkeypatch.setitem(sys.modules, "fubon_neo.constant", None)

        runner = CliRunner()
        result = runner.invoke(
            auth_group,
            ["--id", "A123456789", "--password", "pw", "--cert-path", "/cert.p12"],
        )
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["success"] is False
        assert "not installed" in data["error"]


# ---------------------------------------------------------------------------
# API Key login (auth_group)
# ---------------------------------------------------------------------------

class TestApiKeyLogin:
    """Tests for API Key-based login (v2.2.7+)."""

    def test_apikey_login_success(self, monkeypatch, session_file, patch_sdk):
        runner = CliRunner()
        result = runner.invoke(
            auth_group,
            ["--id", "A123456789", "--api-key", "MY_KEY_123", "--cert-path", "/cert.p12"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert "accounts" in data["data"]

    def test_apikey_login_with_cert_password(self, monkeypatch, session_file, patch_sdk):
        runner = CliRunner()
        result = runner.invoke(
            auth_group,
            [
                "--id", "A123456789",
                "--api-key", "MY_KEY",
                "--cert-path", "/cert.p12",
                "--cert-password", "certpw",
            ],
        )
        assert result.exit_code == 0
        assert json.loads(result.output)["success"] is True

    def test_apikey_login_saves_session(self, monkeypatch, session_file, patch_sdk):
        runner = CliRunner()
        runner.invoke(
            auth_group,
            ["--id", "A123456789", "--api-key", "MY_KEY_123", "--cert-path", "/cert.p12"],
        )
        with open(session_file) as f:
            saved = json.load(f)
        assert saved["login_type"] == "apikey"
        assert saved["personal_id"] == "A123456789"
        assert saved["api_key"] == "MY_KEY_123"
        assert saved["password"] is None

    def test_apikey_login_sdk_failure(self, monkeypatch, session_file):
        sdk_mod = _make_sdk_module(apikey_success=False)
        root = types.ModuleType("fubon_neo")
        constant = types.ModuleType("fubon_neo.constant")
        monkeypatch.setitem(sys.modules, "fubon_neo", root)
        monkeypatch.setitem(sys.modules, "fubon_neo.constant", constant)
        monkeypatch.setitem(sys.modules, "fubon_neo.sdk", sdk_mod)

        runner = CliRunner()
        result = runner.invoke(
            auth_group,
            ["--id", "A123456789", "--api-key", "BAD_KEY", "--cert-path", "/cert.p12"],
        )
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["success"] is False
        assert "API Key login failed" in data["error"]

    def test_both_password_and_apikey_rejected(self, session_file, patch_sdk):
        runner = CliRunner()
        result = runner.invoke(
            auth_group,
            [
                "--id", "A123456789",
                "--password", "pw",
                "--api-key", "MY_KEY",
                "--cert-path", "/cert.p12",
            ],
        )
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["success"] is False
        assert "Cannot use" in data["error"]


# ---------------------------------------------------------------------------
# Logout and Status
# ---------------------------------------------------------------------------

class TestLogoutAndStatus:
    """Tests for logout and status subcommands."""

    def test_logout(self, session_file):
        # Write a dummy session first
        with open(session_file, "w") as f:
            json.dump({"personal_id": "X"}, f)

        runner = CliRunner()
        result = runner.invoke(auth_group, ["logout"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True

        import os
        assert not os.path.exists(session_file)

    def test_status_not_logged_in(self, session_file):
        runner = CliRunner()
        result = runner.invoke(auth_group, ["status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["data"]["logged_in"] is False

    def test_status_password_session(self, session_file):
        with open(session_file, "w") as f:
            json.dump({
                "login_type": "password",
                "personal_id": "A123456789",
                "cert_path": "/cert.p12",
            }, f)

        runner = CliRunner()
        result = runner.invoke(auth_group, ["status"])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["logged_in"] is True
        assert data["login_type"] == "password"
        assert data["personal_id"] == "A12***"
        assert data["cert_path"] == "/cert.p12"

    def test_status_apikey_session(self, session_file):
        with open(session_file, "w") as f:
            json.dump({
                "login_type": "apikey",
                "personal_id": "B987654321",
                "cert_path": "/cert2.p12",
            }, f)

        runner = CliRunner()
        result = runner.invoke(auth_group, ["status"])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["logged_in"] is True
        assert data["login_type"] == "apikey"

    def test_status_legacy_session_defaults_to_password(self, session_file):
        """Sessions without login_type (created before this feature) default to 'password'."""
        with open(session_file, "w") as f:
            json.dump({
                "personal_id": "C111222333",
                "cert_path": "/old.p12",
            }, f)

        runner = CliRunner()
        result = runner.invoke(auth_group, ["status"])
        assert result.exit_code == 0
        data = json.loads(result.output)["data"]
        assert data["login_type"] == "password"


# ---------------------------------------------------------------------------
# core.save_session / core.load_session
# ---------------------------------------------------------------------------

class TestCoreSession:
    """Tests for core session persistence functions."""

    def test_save_load_password_session(self, session_file):
        core.save_session("ID", "pw", "/cert.p12", "certpw")
        loaded = core.load_session()
        assert loaded["login_type"] == "password"
        assert loaded["personal_id"] == "ID"
        assert loaded["password"] == "pw"
        assert loaded["api_key"] is None

    def test_save_load_apikey_session(self, session_file):
        core.save_session("ID", None, "/cert.p12", "certpw", login_type="apikey", api_key="KEY123")
        loaded = core.load_session()
        assert loaded["login_type"] == "apikey"
        assert loaded["api_key"] == "KEY123"
        assert loaded["password"] is None

    def test_load_session_no_file(self, session_file):
        assert core.load_session() is None

    def test_clear_session(self, session_file):
        core.save_session("ID", "pw", "/cert.p12", "")
        core.clear_session()
        assert core.load_session() is None


# ---------------------------------------------------------------------------
# core.get_sdk_and_accounts
# ---------------------------------------------------------------------------

class TestGetSdkAndAccounts:
    """Tests for core.get_sdk_and_accounts with both login types."""

    def _fake_import_sdk(self, sdk_instance):
        class _FakeSDK:
            def __new__(cls):
                return sdk_instance

        return _FakeSDK, None

    def test_no_session_exits(self, monkeypatch, session_file, capsys):
        monkeypatch.setattr(core, "load_session", lambda: None)
        with pytest.raises(SystemExit) as exc:
            core.get_sdk_and_accounts()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Not logged in" in captured.out

    def test_password_session_calls_login(self, monkeypatch, session_file):
        session = {
            "login_type": "password",
            "personal_id": "ID",
            "password": "pw",
            "cert_path": "/cert.p12",
            "cert_password": "cp",
            "api_key": None,
        }
        monkeypatch.setattr(core, "load_session", lambda: session)

        called = {}

        class _FakeSDK:
            def login(self, *args):
                called["method"] = "login"
                called["args"] = args
                return _Obj(
                    is_success=True,
                    data=[_Obj(account="617842")],
                )

            def apikey_login(self, *args):
                called["method"] = "apikey_login"
                return _Obj(is_success=True, data=[])

        monkeypatch.setattr(core, "_import_sdk", lambda: (_FakeSDK, None))
        sdk, accounts = core.get_sdk_and_accounts()
        assert called["method"] == "login"
        assert called["args"] == ("ID", "pw", "/cert.p12", "cp")

    def test_apikey_session_calls_apikey_login(self, monkeypatch, session_file):
        session = {
            "login_type": "apikey",
            "personal_id": "ID",
            "password": None,
            "cert_path": "/cert.p12",
            "cert_password": "cp",
            "api_key": "KEY123",
        }
        monkeypatch.setattr(core, "load_session", lambda: session)

        called = {}

        class _FakeSDK:
            def login(self, *args):
                called["method"] = "login"
                return _Obj(is_success=True, data=[])

            def apikey_login(self, *args):
                called["method"] = "apikey_login"
                called["args"] = args
                return _Obj(
                    is_success=True,
                    data=[_Obj(account="617842")],
                )

        monkeypatch.setattr(core, "_import_sdk", lambda: (_FakeSDK, None))
        sdk, accounts = core.get_sdk_and_accounts()
        assert called["method"] == "apikey_login"
        assert called["args"] == ("ID", "KEY123", "/cert.p12", "cp")

    def test_login_failure_exits(self, monkeypatch, session_file, capsys):
        session = {
            "login_type": "password",
            "personal_id": "ID",
            "password": "bad",
            "cert_path": "/cert.p12",
            "cert_password": "",
        }
        monkeypatch.setattr(core, "load_session", lambda: session)

        class _FakeSDK:
            def login(self, *args):
                return _Obj(is_success=False, message="invalid credentials")

        monkeypatch.setattr(core, "_import_sdk", lambda: (_FakeSDK, None))
        with pytest.raises(SystemExit) as exc:
            core.get_sdk_and_accounts()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Login failed" in captured.out

    def test_apikey_login_failure_exits(self, monkeypatch, session_file, capsys):
        session = {
            "login_type": "apikey",
            "personal_id": "ID",
            "password": None,
            "cert_path": "/cert.p12",
            "cert_password": "",
            "api_key": "BAD_KEY",
        }
        monkeypatch.setattr(core, "load_session", lambda: session)

        class _FakeSDK:
            def apikey_login(self, *args):
                return _Obj(is_success=False, message="key rejected")

        monkeypatch.setattr(core, "_import_sdk", lambda: (_FakeSDK, None))
        with pytest.raises(SystemExit) as exc:
            core.get_sdk_and_accounts()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "Login failed" in captured.out

    def test_legacy_session_without_login_type(self, monkeypatch, session_file):
        """Sessions without login_type default to password login."""
        session = {
            "personal_id": "ID",
            "password": "pw",
            "cert_path": "/cert.p12",
            "cert_password": "",
        }
        monkeypatch.setattr(core, "load_session", lambda: session)

        called = {}

        class _FakeSDK:
            def login(self, *args):
                called["method"] = "login"
                return _Obj(is_success=True, data=[_Obj(account="617842")])

            def apikey_login(self, *args):
                called["method"] = "apikey_login"
                return _Obj(is_success=True, data=[])

        monkeypatch.setattr(core, "_import_sdk", lambda: (_FakeSDK, None))
        core.get_sdk_and_accounts()
        assert called["method"] == "login"
