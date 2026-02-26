# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

`fubon-cli` is a Python CLI tool wrapping the Fubon Neo SDK (a Taiwan securities brokerage). Every command outputs structured JSON to stdout, designed explicitly for AI agent automation. The binary entry point is `fubon`, mapped to `fubon_cli.main:cli`.

## Setup

```bash
# Install platform-specific fubon_neo wheel first
pip install ./wheels/fubon_neo-2.2.8-cp37-abi3-win_amd64.whl          # Windows
pip install ./wheels/fubon_neo-2.2.8-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl  # Linux
pip install ./wheels/fubon_neo-2.2.8-cp37-abi3-macosx_11_0_arm64.whl  # macOS ARM

pip install -e ".[dev]"
```

## Common Commands

**Run tests:**
```bash
pytest -v --tb=short -m "not integration"
```

**Run a single test file:**
```bash
pytest tests/test_core.py -v --tb=short
```

**Run with coverage (CI requires 95%):**
```bash
pytest -v --tb=short -m "not integration" --cov=fubon_cli --cov-branch --cov-fail-under=95 --cov-report=term-missing
```

**Lint (blocking — syntax/undefined names):**
```bash
flake8 fubon_cli --count --select=E9,F63,F7,F82 --show-source --statistics
```

**Format check:**
```bash
black --check fubon_cli tests
isort --check-only fubon_cli tests
```

**Type check:**
```bash
mypy fubon_cli
```

**Build package:**
```bash
python -m build
```

## Architecture

### Core Data Flow

```
fubon <command>
  -> main.py: cli() Click group
    -> command module (e.g. commands/stock.py)
      -> core.get_sdk_and_accounts()   # loads ~/.fubon-cli-session.json, re-authenticates
        -> SDK call
          -> core.obj_to_dict()        # converts pyo3 objects to JSON-safe dicts
            -> core.output()           # prints {"success": bool, "data": ..., "error": ...}
```

### Key Files

- **`fubon_cli/main.py`** — assembles all command groups into the `cli` Click group
- **`fubon_cli/core.py`** — shared plumbing: `save_session`, `load_session`, `get_sdk_and_accounts()`, `obj_to_dict()`, `output()`
- **`fubon_cli/commands/`** — one module per command group; each is independent and imports only from `fubon_cli.core`
- **`tests/conftest.py`** — complete mock SDK (`MockSDK`, `StockClient`, `FutoptClient`, etc.) used by all tests

### Session & Config Storage

- Trading session credentials: `~/.fubon-cli-session.json` (plaintext)
- AI assistant config (OpenAI key, model): `~/.fubon-cli-config.json`
- `get_sdk_and_accounts()` re-authenticates on every CLI invocation — intentionally stateless for AI agent use

### Command Groups

| Group | File | Purpose |
|---|---|---|
| `login` / `logout` / `status` | `commands/auth.py` | Authentication |
| `stock` | `commands/stock.py` | Stock orders, batch operations |
| `account` | `commands/account.py` | Inventory, P&L, balance queries |
| `market` | `commands/market.py` | Quotes, candles, technical indicators, corp actions |
| `realtime` | `commands/realtime.py` | WebSocket streaming |
| `futopt` | `commands/futopt.py` | Futures/options orders |
| `condition` | `commands/condition.py` | Conditional orders (accepts raw JSON args) |
| `ask` / `chat` / `config` | `commands/ai.py` | OpenAI-powered assistant |

### Testing Notes

- The active pytest config is `pytest.ini` (not `pyproject.toml` — the `[tool.pytest.ini_options]` there has a non-standard flag that conflicts)
- All SDK calls are fully mocked via `tests/conftest.py`; no real brokerage credentials are needed for tests
- `fubon_neo` is a pyo3 Rust extension — `obj_to_dict()` in `core.py` handles recursive conversion of its objects to plain dicts
