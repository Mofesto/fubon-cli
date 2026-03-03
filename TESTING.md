# Fubon CLI Testing Guide

This document describes how to test the fubon-cli with real data to ensure all commands work correctly.

## Overview

The fubon-cli provides several test scripts to validate functionality with real market data:

1. **PowerShell Test Script** (`scripts/test_real_data.ps1`) - Windows PowerShell-based testing
2. **Python Test Script** (`scripts/test_real_data.py`) - Cross-platform Python-based testing
3. **Unit Tests** (`tests/`) - Automated unit tests using pytest

## Prerequisites

Before running tests with real data:

1. **Install fubon-cli**:
   ```bash
   pip install -e ".[dev]"
   ```

2. **Install Fubon Neo SDK**:
   ```bash
   pip install wheels/fubon_neo-2.2.8-cp37-abi3-win_amd64.whl
   ```

3. **Login to Fubon account**:
   ```bash
   fubon login --id "YOUR_ID" --password "YOUR_PASSWORD" --cert-path "path/to/cert.pfx" --cert-password "CERT_PASSWORD"
   ```

## Running Tests

### Option 1: PowerShell Test Script (Recommended for Windows)

```powershell
# Run all tests with default settings
.\scripts\test_real_data.ps1

# Run with verbose output
.\scripts\test_real_data.ps1 -Verbose

# Test with a different stock symbol
.\scripts\test_real_data.ps1 -TestSymbol "0050"
```

**Features:**
- ✅ Validates JSON output format
- ✅ Tests all major commands (market data, account, orders)
- ✅ Error handling verification
- ✅ Generates detailed test report (JSON)
- ✅ Color-coded pass/fail indicators

### Option 2: Python Test Script (Cross-platform)

```bash
# Run all tests
python scripts/test_real_data.py

# Run with verbose output
python scripts/test_real_data.py --verbose

# Test with a different stock symbol
python scripts/test_real_data.py --symbol 0050
```

**Features:**
- ✅ Cross-platform compatibility
- ✅ Comprehensive JSON validation
- ✅ Field-level data structure checks
- ✅ Detailed error reporting
- ✅ Exportable test results

### Option 3: Unit Tests (pytest)

```bash
# Run all unit tests
python -m pytest -v

# Run specific test file
python -m pytest tests/test_cli.py -v

# Run with coverage report
python -m pytest --cov=fubon_cli --cov-report=html
```

## Test Coverage

### 1. Authentication Commands

| Command | Test Coverage | Notes |
|---------|--------------|-------|
| `fubon login` | ✅ Manual | Requires credentials |
| `fubon login status` | ✅ Automated | Checks session state |
| `fubon login logout` | ✅ Manual | Session cleanup |

### 2. Market Data Commands

| Command | Test Coverage | Real Data | Notes |
|---------|--------------|-----------|-------|
| `fubon market quote <symbol>` | ✅ Automated | ✅ Yes | Real-time quote |
| `fubon market ticker <symbol>` | ✅ Automated | ✅ Yes | Ticker information |
| `fubon market candles <symbol>` | ✅ Automated | ✅ Yes | K-line/candlestick data |
| `fubon market snapshot <symbol>` | ✅ Automated | ✅ Yes | Market snapshot |
| `fubon market movers` | ✅ Automated | ✅ Yes | Daily movers |
| `fubon market actives` | ✅ Automated | ✅ Yes | Active stocks |

### 3. Account Commands

| Command | Test Coverage | Real Data | Notes |
|---------|--------------|-----------|-------|
| `fubon account inventory` | ✅ Automated | ✅ Yes | Current holdings |
| `fubon account unrealized` | ✅ Automated | ✅ Yes | Unrealized P&L |
| `fubon account settlement` | ✅ Automated | ✅ Yes | Settlement info |

### 4. Stock Trading Commands

| Command | Test Coverage | Real Data | Notes |
|---------|--------------|-----------|-------|
| `fubon stock orders` | ✅ Automated | ✅ Yes | Query orders |
| `fubon stock buy` | ⚠️ Manual | ⚠️ Caution | Real order placement |
| `fubon stock sell` | ⚠️ Manual | ⚠️ Caution | Real order placement |
| `fubon stock cancel` | ⚠️ Manual | ⚠️ Caution | Order cancellation |
| `fubon stock modify-price` | ⚠️ Manual | ⚠️ Caution | Order modification |
| `fubon stock modify-quantity` | ⚠️ Manual | ⚠️ Caution | Order modification |

⚠️ **Warning:** Trading commands require manual testing in a safe environment to avoid unintended real trades.

### 5. Realtime Data Commands

| Command | Test Coverage | Real Data | Notes |
|---------|--------------|-----------|-------|
| `fubon realtime subscribe` | ⚠️ Manual | ✅ Yes | WebSocket subscription |
| `fubon realtime unsubscribe` | ⚠️ Manual | ✅ Yes | Unsubscribe |

## Manual Testing Checklist

For commands that require careful manual testing:

### Safe Read-Only Tests (Always Safe)

- [ ] Get stock quote for multiple symbols (2330, 0050, 2881)
- [ ] Get market snapshot during trading hours
- [ ] Check account inventory
- [ ] Query current orders
- [ ] Get unrealized P&L
- [ ] Test odd-lot quote queries
- [ ] Verify JSON output format for all commands

### Trading Commands (Test in Paper/Demo Account)

- [ ] Place a limit buy order (small quantity)
- [ ] Place a limit sell order (small quantity)
- [ ] Cancel a pending order
- [ ] Modify order price
- [ ] Modify order quantity
- [ ] Test IOC (Immediate or Cancel) order
- [ ] Test FOK (Fill or Kill) order
- [ ] Verify order status updates

### Edge Cases and Error Handling

- [ ] Invalid stock symbol
- [ ] Invalid quantity (negative, zero)
- [ ] Invalid price
- [ ] Missing required parameters
- [ ] Invalid account index
- [ ] Network disconnection handling
- [ ] Session expiration handling

## Test Data Validation

### JSON Output Structure

All commands should output valid JSON with the following structure:

```json
{
  "success": true,
  "data": { /* command-specific data */ },
  "timestamp": "2026-02-26T10:30:00"
}
```

Or on error:

```json
{
  "success": false,
  "error": "Error message description"
}
```

### Common Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Command success status |
| `data` | object/array | Command output data |
| `error` | string | Error message (if failed) |
| `timestamp` | string | ISO 8601 timestamp |

### Market Data Fields

For market data commands, expect fields like:

```json
{
  "symbol": "2330",
  "price": "580.00",
  "volume": 123456,
  "bid": "579.00",
  "ask": "581.00",
  "change": "+5.00",
  "change_percent": "+0.87%"
}
```

## Interpreting Test Results

### Test Report Structure

Both test scripts generate JSON reports with:

```json
{
  "summary": {
    "total": 20,
    "passed": 18,
    "failed": 2,
    "pass_rate": 90.0,
    "timestamp": "2026-02-26T10:30:00"
  },
  "results": [
    {
      "test_name": "Get Stock Quote (2330)",
      "command": "fubon market quote 2330",
      "passed": true,
      "timestamp": "2026-02-26T10:30:05",
      "stdout": "...",
      "is_valid_json": true
    }
  ]
}
```

### Success Criteria

- **Pass Rate ≥ 90%**: Excellent
- **Pass Rate 70-89%**: Good (review failed tests)
- **Pass Rate < 70%**: Issues detected (investigate immediately)

### Common Failure Reasons

1. **Not Logged In**: Run `fubon login` first
2. **Network Issues**: Check internet connection
3. **Invalid Credentials**: Verify login credentials
4. **Market Closed**: Some data unavailable outside trading hours
5. **Insufficient Permissions**: Account may lack certain permissions

## Continuous Integration

### GitHub Actions Integration

Add to `.github/workflows/test.yml`:

```yaml
name: Test Real Data
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install wheels/fubon_neo-2.2.8-*.whl
      - name: Run tests
        run: python -m pytest -v
```

## Troubleshooting

### Issue: "fubon_neo SDK not installed"

**Solution:**
```bash
pip install wheels/fubon_neo-2.2.8-cp37-abi3-win_amd64.whl
```

### Issue: "Not logged in"

**Solution:**
```bash
fubon login --id <ID> --password <PW> --cert-path <PATH> --cert-password <PW>
fubon login status  # Verify login
```

### Issue: "JSON parse error"

**Possible causes:**
- Command outputting to stderr instead of stdout
- SDK returning non-JSON format
- Network or connection error

**Solution:**
- Check command output manually
- Verify SDK version compatibility
- Check network connection

### Issue: Test timeout

**Solution:**
- Increase timeout in test script
- Check network speed
- Verify API endpoint availability

## Best Practices

1. **Always test in a safe environment first**
2. **Use small quantities for trading command tests**
3. **Verify read-only commands before testing write operations**
4. **Keep test credentials separate from production**
5. **Run tests during market hours for complete data**
6. **Review test reports after each run**
7. **Document any recurring issues**
8. **Update tests when adding new commands**

## Contributing

When adding new commands:

1. Add test cases to test scripts
2. Update this documentation
3. Ensure JSON output format consistency
4. Add error handling tests
5. Document expected data fields

## Resources

- [Fubon Neo SDK Documentation](https://fubon-neo-sdk-docs.url)
- [CLI Command Reference](README.md#command-reference)
- [Issue Tracker](https://github.com/your-repo/fubon-cli/issues)

---

Last Updated: 2026-02-26
