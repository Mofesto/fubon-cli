"""Comprehensive tests for fubon_cli/commands/ai.py.

Covers: load_config, save_config, _get_api_key, _get_model, _has_openai,
_call_ai, _extract_fubon_commands, _is_trading_command, _run_fubon_command,
_print_ai_response, _print_chat_banner, _offer_to_execute, ask_cmd,
chat_cmd, config set/show/get.
"""

import builtins
import json
import os
import subprocess
import sys
import types

import click
import pytest
from click.testing import CliRunner

from fubon_cli.commands import ai
from fubon_cli.commands.ai import (
    _extract_fubon_commands,
    _is_trading_command,
    _run_fubon_command,
    ask_cmd,
    chat_cmd,
    config_group,
    load_config,
    save_config,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture()
def tmp_config(tmp_path, monkeypatch):
    """Point ai.CONFIG_FILE to a temp path and return the Path object."""
    cfg_path = tmp_path / "config.json"
    monkeypatch.setattr(ai, "CONFIG_FILE", str(cfg_path))
    return cfg_path


# ─── load_config ──────────────────────────────────────────────────────────────


def test_load_config_missing_file(tmp_config):
    assert load_config() == {}


def test_load_config_valid_json(tmp_config):
    data = {"openai_api_key": "sk-test", "ai_model": "gpt-4o"}
    tmp_config.write_text(json.dumps(data), encoding="utf-8")
    assert load_config() == data


def test_load_config_invalid_json(tmp_config):
    tmp_config.write_text("not json!!", encoding="utf-8")
    assert load_config() == {}


# ─── save_config ──────────────────────────────────────────────────────────────


def test_save_config_nt(tmp_config, monkeypatch):
    """On Windows (nt) chmod is not called."""
    monkeypatch.setattr(os, "name", "nt")
    called = []
    monkeypatch.setattr(os, "chmod", lambda *a: called.append(a))
    save_config({"ai_model": "gpt-4"})
    assert tmp_config.exists()
    assert called == []


def test_save_config_posix(tmp_config, monkeypatch):
    """On POSIX chmod(0o600) is called."""
    monkeypatch.setattr(os, "name", "posix")
    called = []
    monkeypatch.setattr(os, "chmod", lambda p, m: called.append(m))
    save_config({"ai_model": "gpt-4"})
    assert called == [0o600]


def test_save_config_data_persisted(tmp_config, monkeypatch):
    monkeypatch.setattr(os, "name", "nt")
    save_config({"key": "val"})
    assert json.loads(tmp_config.read_text(encoding="utf-8")) == {"key": "val"}


# ─── _get_api_key ─────────────────────────────────────────────────────────────


def test_get_api_key_from_config(tmp_config, monkeypatch):
    tmp_config.write_text(json.dumps({"openai_api_key": "sk-cfg"}), encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("FUBON_AI_KEY", raising=False)
    assert ai._get_api_key() == "sk-cfg"


def test_get_api_key_from_openai_env(tmp_config, monkeypatch):
    tmp_config.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env-openai")
    monkeypatch.delenv("FUBON_AI_KEY", raising=False)
    assert ai._get_api_key() == "sk-env-openai"


def test_get_api_key_from_fubon_env(tmp_config, monkeypatch):
    tmp_config.write_text("{}", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("FUBON_AI_KEY", "sk-fubon")
    assert ai._get_api_key() == "sk-fubon"


def test_get_api_key_none(tmp_config, monkeypatch):
    tmp_config.write_text("{}", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("FUBON_AI_KEY", raising=False)
    assert ai._get_api_key() is None


# ─── _get_model ───────────────────────────────────────────────────────────────


def test_get_model_from_config(tmp_config):
    tmp_config.write_text(json.dumps({"ai_model": "gpt-4o"}), encoding="utf-8")
    assert ai._get_model() == "gpt-4o"


def test_get_model_default(tmp_config):
    tmp_config.write_text("{}", encoding="utf-8")
    assert ai._get_model() == "gpt-4o-mini"


# ─── _has_openai ──────────────────────────────────────────────────────────────


def test_has_openai_true(monkeypatch):
    fake_openai = types.ModuleType("openai")
    monkeypatch.setitem(sys.modules, "openai", fake_openai)
    assert ai._has_openai() is True


def test_has_openai_false(monkeypatch):
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "openai":
            raise ImportError("no openai")
        return real_import(name, *args, **kwargs)

    sys.modules.pop("openai", None)
    monkeypatch.setattr(builtins, "__import__", _fake_import)
    assert ai._has_openai() is False


# ─── _extract_fubon_commands ──────────────────────────────────────────────────


def test_extract_fenced_bash_block():
    text = "```bash\nfubon market quote 2330\nfubon stock buy 2330 1 --price 10\n```"
    cmds = _extract_fubon_commands(text)
    assert "fubon market quote 2330" in cmds
    assert "fubon stock buy 2330 1 --price 10" in cmds


def test_extract_fenced_sh_with_dollar_prefix():
    text = "```sh\n$ fubon account inventory\n```"
    cmds = _extract_fubon_commands(text)
    assert "fubon account inventory" in cmds


def test_extract_inline_backtick():
    text = "執行 `fubon account balance` 查詢"
    cmds = _extract_fubon_commands(text)
    assert "fubon account balance" in cmds


def test_extract_no_commands():
    cmds = _extract_fubon_commands("沒有任何指令在這裡")
    assert cmds == []


def test_extract_dedup():
    text = (
        "```bash\nfubon market quote 2330\nfubon market quote 2330\n```\n"
        "`fubon market quote 2330`"
    )
    cmds = _extract_fubon_commands(text)
    assert cmds.count("fubon market quote 2330") == 1


def test_extract_fenced_no_language():
    text = "```\nfubon account unrealized\n```"
    cmds = _extract_fubon_commands(text)
    assert "fubon account unrealized" in cmds


# ─── _is_trading_command ─────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "cmd",
    [
        "fubon stock buy 2330 1 --price 10",
        "fubon stock sell 2330 1 --price 10",
        "fubon stock modify ORD1 --price 11",
        "fubon stock cancel ORD1",
        "fubon futopt buy TX 1 --price 100",
        "fubon futopt sell TX 1 --price 100",
        "fubon futopt modify ORD2 --price 101",
        "fubon futopt cancel ORD2",
        "fubon condition cancel abc123",
    ],
)
def test_is_trading_command_true(cmd):
    assert _is_trading_command(cmd) is True


@pytest.mark.parametrize(
    "cmd",
    [
        "fubon market quote 2330",
        "fubon account inventory",
        "fubon stock orders",
        "fubon futopt orders",
        "fubon futopt inventories",
    ],
)
def test_is_trading_command_false(cmd):
    assert _is_trading_command(cmd) is False


# ─── _run_fubon_command ───────────────────────────────────────────────────────


def test_run_fubon_command_json_output(monkeypatch):
    payload = {"success": True, "data": {"price": 100}}
    mock_proc = types.SimpleNamespace(stdout=json.dumps(payload), stderr="")
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: mock_proc)
    out = _run_fubon_command("fubon market quote 2330")
    assert json.loads(out) == payload


def test_run_fubon_command_non_json(monkeypatch):
    mock_proc = types.SimpleNamespace(stdout="plain text", stderr="")
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: mock_proc)
    assert _run_fubon_command("fubon x") == "plain text"


def test_run_fubon_command_stderr_fallback(monkeypatch):
    mock_proc = types.SimpleNamespace(stdout="", stderr="some error")
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: mock_proc)
    assert _run_fubon_command("fubon x") == "some error"


# ─── _print_ai_response ───────────────────────────────────────────────────────


def test_print_ai_response_renders(tmp_config):
    runner = CliRunner()

    @click.command()
    def _cmd():
        ai._print_ai_response(
            "## 標題\n"
            "一般文字\n"
            "```bash\n"
            "fubon market quote 2330\n"
            "```\n"
            "後續文字"
        )

    result = runner.invoke(_cmd)
    assert result.exit_code == 0
    assert "fubon market quote 2330" in result.output
    assert "標題" in result.output


def test_print_ai_response_empty_string():
    runner = CliRunner()

    @click.command()
    def _cmd():
        ai._print_ai_response("")

    result = runner.invoke(_cmd)
    assert result.exit_code == 0


# ─── _print_chat_banner ───────────────────────────────────────────────────────


def test_print_chat_banner_output():
    runner = CliRunner()

    @click.command()
    def _cmd():
        ai._print_chat_banner()

    result = runner.invoke(_cmd)
    assert result.exit_code == 0
    assert "/run" in result.output
    assert "/clear" in result.output
    assert "exit" in result.output


# ─── _offer_to_execute ────────────────────────────────────────────────────────


def test_offer_to_execute_empty_list():
    runner = CliRunner()

    @click.command()
    def _cmd():
        ai._offer_to_execute([])

    result = runner.invoke(_cmd)
    assert result.exit_code == 0
    assert result.output == ""


def test_offer_to_execute_non_trading_confirmed(monkeypatch):
    executed = []
    monkeypatch.setattr(ai, "_run_fubon_command", lambda c: executed.append(c) or "ok output")
    runner = CliRunner()

    @click.command()
    def _cmd():
        ai._offer_to_execute(["fubon market quote 2330"])

    result = runner.invoke(_cmd, input="y\n")
    assert result.exit_code == 0
    assert "ok output" in result.output
    assert executed == ["fubon market quote 2330"]


def test_offer_to_execute_non_trading_declined(monkeypatch):
    executed = []
    monkeypatch.setattr(ai, "_run_fubon_command", lambda c: executed.append(c) or "")
    runner = CliRunner()

    @click.command()
    def _cmd():
        ai._offer_to_execute(["fubon market quote 2330"])

    result = runner.invoke(_cmd, input="n\n")
    assert result.exit_code == 0
    assert "跳過" in result.output
    assert executed == []


def test_offer_to_execute_trading_confirmed(monkeypatch):
    executed = []
    monkeypatch.setattr(ai, "_run_fubon_command", lambda c: executed.append(c) or "trade done")
    runner = CliRunner()

    @click.command()
    def _cmd():
        ai._offer_to_execute(["fubon stock buy 2330 1 --price 10"])

    result = runner.invoke(_cmd, input="yes\n")
    assert result.exit_code == 0
    assert "trade done" in result.output
    assert len(executed) == 1


def test_offer_to_execute_trading_declined(monkeypatch):
    executed = []
    monkeypatch.setattr(ai, "_run_fubon_command", lambda c: executed.append(c) or "")
    runner = CliRunner()

    @click.command()
    def _cmd():
        ai._offer_to_execute(["fubon stock buy 2330 1 --price 10"])

    result = runner.invoke(_cmd, input="no\n")
    assert result.exit_code == 0
    assert "跳過" in result.output
    assert executed == []


# ─── ask_cmd ─────────────────────────────────────────────────────────────────


def test_ask_no_openai_text_output(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: False)
    runner = CliRunner()
    result = runner.invoke(ask_cmd, ["什麼是台積電？"])
    assert result.exit_code == 1
    assert "openai" in result.output.lower()


def test_ask_no_openai_json_output(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: False)
    runner = CliRunner()
    result = runner.invoke(ask_cmd, ["什麼是台積電？", "--json-output"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["success"] is False


def test_ask_no_api_key_text_output(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: None)
    runner = CliRunner()
    result = runner.invoke(ask_cmd, ["what?"])
    assert result.exit_code == 1
    assert "key" in result.output.lower() or "Key" in result.output


def test_ask_no_api_key_json_output(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: None)
    runner = CliRunner()
    result = runner.invoke(ask_cmd, ["what?", "--json-output"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["success"] is False


def test_ask_success_json_output(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")
    monkeypatch.setattr(
        ai, "_call_ai", lambda msgs: "```bash\nfubon market quote 2330\n```"
    )
    runner = CliRunner()
    result = runner.invoke(ask_cmd, ["查詢台積電報價", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["success"] is True
    assert data["question"] == "查詢台積電報價"
    assert "fubon market quote 2330" in data["suggested_commands"]


def test_ask_success_text_output(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")
    monkeypatch.setattr(
        ai, "_call_ai", lambda msgs: "## 答案\n一般回應\n`fubon account inventory`"
    )
    runner = CliRunner()
    result = runner.invoke(ask_cmd, ["查詢庫存"])
    assert result.exit_code == 0
    assert "答案" in result.output


def test_ask_execute_flag_runs_command(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")
    monkeypatch.setattr(
        ai, "_call_ai", lambda msgs: "```bash\nfubon account inventory\n```"
    )
    executed = []
    monkeypatch.setattr(ai, "_run_fubon_command", lambda c: executed.append(c) or "result")
    runner = CliRunner()
    result = runner.invoke(ask_cmd, ["查詢庫存", "--execute"], input="y\n")
    assert result.exit_code == 0
    assert executed == ["fubon account inventory"]


def test_ask_exception_text_output(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")

    def _raise(msgs):
        raise RuntimeError("API error")

    monkeypatch.setattr(ai, "_call_ai", _raise)
    runner = CliRunner()
    result = runner.invoke(ask_cmd, ["問題?"])
    assert result.exit_code == 1
    assert "API error" in result.output


def test_ask_exception_json_output(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")

    def _raise(msgs):
        raise RuntimeError("network failure")

    monkeypatch.setattr(ai, "_call_ai", _raise)
    runner = CliRunner()
    result = runner.invoke(ask_cmd, ["問題?", "--json-output"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["success"] is False
    assert "network failure" in data["error"]


# ─── chat_cmd ─────────────────────────────────────────────────────────────────


def test_chat_no_openai(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: False)
    runner = CliRunner()
    result = runner.invoke(chat_cmd, [])
    assert result.exit_code == 1


def test_chat_no_api_key(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: None)
    runner = CliRunner()
    result = runner.invoke(chat_cmd, [])
    assert result.exit_code == 1


def test_chat_exit_command(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")
    runner = CliRunner()
    result = runner.invoke(chat_cmd, [], input="exit\n")
    assert result.exit_code == 0
    assert "再見" in result.output


def test_chat_eof_exits_gracefully(tmp_config, monkeypatch):
    """EOFError/Abort on click.prompt exits gracefully with 再見 message."""
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")

    call_count = [0]

    def _fake_prompt(*args, **kwargs):
        call_count[0] += 1
        raise EOFError()

    monkeypatch.setattr(click, "prompt", _fake_prompt)
    runner = CliRunner()
    result = runner.invoke(chat_cmd, [])
    assert result.exit_code == 0
    assert "再見" in result.output


def test_chat_clear_command(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")
    runner = CliRunner()
    result = runner.invoke(chat_cmd, [], input="/clear\nexit\n")
    assert result.exit_code == 0
    assert "清除" in result.output


def test_chat_run_no_commands(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")
    runner = CliRunner()
    result = runner.invoke(chat_cmd, [], input="/run\nexit\n")
    assert result.exit_code == 0
    assert "沒有" in result.output


def test_chat_normal_conversation(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")
    monkeypatch.setattr(
        ai, "_call_ai", lambda msgs: "## 答案\n`fubon account inventory`"
    )
    runner = CliRunner()
    result = runner.invoke(chat_cmd, [], input="查詢庫存\nexit\n")
    assert result.exit_code == 0
    assert "答案" in result.output or "富邦助理" in result.output


def test_chat_run_with_last_commands(tmp_config, monkeypatch):
    """After receiving AI response with commands, /run offers to execute them."""
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")
    monkeypatch.setattr(
        ai, "_call_ai", lambda msgs: "```bash\nfubon account inventory\n```"
    )
    executed = []
    monkeypatch.setattr(ai, "_run_fubon_command", lambda c: executed.append(c) or "ok")
    runner = CliRunner()
    # ask a question → get commands → /run → confirm → exit
    result = runner.invoke(chat_cmd, [], input="查詢庫存\n/run\ny\nexit\n")
    assert result.exit_code == 0


def test_chat_exception_in_call_ai(tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")

    def _raise(msgs):
        raise RuntimeError("network error")

    monkeypatch.setattr(ai, "_call_ai", _raise)
    runner = CliRunner()
    result = runner.invoke(chat_cmd, [], input="問題\nexit\n")
    assert result.exit_code == 0
    assert "錯誤" in result.output


def test_chat_empty_input_skipped(tmp_config, monkeypatch):
    """Empty input lines are skipped without calling AI."""
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")
    called = []
    monkeypatch.setattr(ai, "_call_ai", lambda msgs: called.append(1) or "answer")
    runner = CliRunner()
    result = runner.invoke(chat_cmd, [], input="\n\nexit\n")
    assert result.exit_code == 0
    assert called == []


@pytest.mark.parametrize("word", ["quit", "q", "bye", "掰掰"])
def test_chat_various_exit_words(word, tmp_config, monkeypatch):
    monkeypatch.setattr(ai, "_has_openai", lambda: True)
    monkeypatch.setattr(ai, "_get_api_key", lambda: "sk-test")
    runner = CliRunner()
    result = runner.invoke(chat_cmd, [], input=f"{word}\n")
    assert result.exit_code == 0


# ─── config commands ──────────────────────────────────────────────────────────


def test_config_set_openai_key(tmp_config):
    runner = CliRunner()
    result = runner.invoke(config_group, ["set", "openai-key", "sk-12345678abcdef"])
    assert result.exit_code == 0
    assert "sk-12345" in result.output
    cfg = json.loads(tmp_config.read_text(encoding="utf-8"))
    assert cfg["openai_api_key"] == "sk-12345678abcdef"


def test_config_set_ai_key_alias(tmp_config):
    runner = CliRunner()
    result = runner.invoke(config_group, ["set", "ai-key", "sk-alias"])
    assert result.exit_code == 0
    cfg = json.loads(tmp_config.read_text(encoding="utf-8"))
    assert cfg["openai_api_key"] == "sk-alias"


def test_config_set_model(tmp_config):
    runner = CliRunner()
    result = runner.invoke(config_group, ["set", "ai-model", "gpt-4o"])
    assert result.exit_code == 0
    assert "gpt-4o" in result.output
    cfg = json.loads(tmp_config.read_text(encoding="utf-8"))
    assert cfg["ai_model"] == "gpt-4o"


def test_config_set_model_alias(tmp_config):
    runner = CliRunner()
    result = runner.invoke(config_group, ["set", "model", "gpt-4-turbo"])
    assert result.exit_code == 0
    cfg = json.loads(tmp_config.read_text(encoding="utf-8"))
    assert cfg["ai_model"] == "gpt-4-turbo"


def test_config_set_invalid_key(tmp_config):
    runner = CliRunner()
    result = runner.invoke(config_group, ["set", "unknown-key", "value"])
    assert result.exit_code == 1
    assert "未知" in result.output


def test_config_show_empty(tmp_config):
    runner = CliRunner()
    result = runner.invoke(config_group, ["show"])
    assert result.exit_code == 0
    assert "無配置" in result.output or "（" in result.output


def test_config_show_with_data(tmp_config):
    tmp_config.write_text(
        json.dumps({"openai_api_key": "sk-test1234", "ai_model": "gpt-4o"}),
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(config_group, ["show"])
    assert result.exit_code == 0
    assert "openai_api_key" in result.output
    assert "sk-test1" in result.output
    assert "gpt-4o" in result.output


def test_config_get_model_key(tmp_config):
    tmp_config.write_text(json.dumps({"ai_model": "gpt-4o"}), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(config_group, ["get", "ai-model"])
    assert result.exit_code == 0
    assert "gpt-4o" in result.output


def test_config_get_api_key_masked(tmp_config):
    tmp_config.write_text(
        json.dumps({"openai_api_key": "sk-12345678"}), encoding="utf-8"
    )
    runner = CliRunner()
    result = runner.invoke(config_group, ["get", "openai-key"])
    assert result.exit_code == 0
    assert "..." in result.output


def test_config_get_not_set(tmp_config):
    runner = CliRunner()
    result = runner.invoke(config_group, ["get", "ai-model"])
    assert result.exit_code == 0
    assert "未設定" in result.output


def test_config_get_unknown_key(tmp_config):
    """Unknown key (not in _KEY_MAP) falls through to raw lookup — not set."""
    runner = CliRunner()
    result = runner.invoke(config_group, ["get", "totally-unknown"])
    assert result.exit_code == 0
    assert "未設定" in result.output
