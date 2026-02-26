"""Core SDK session management for fubon-cli.

Handles login, session persistence, and SDK instance lifecycle.
"""

import json
import os
import sys

SESSION_FILE = os.path.join(os.path.expanduser("~"), ".fubon-cli-session.json")


def _import_sdk():
    """Import FubonSDK and related modules. Raises clear error if not installed."""
    try:
        from fubon_neo.sdk import FubonSDK, Order
        from fubon_neo.constant import (
            TimeInForce, OrderType, PriceType, MarketType, BSAction,
            FutOptMarketType, FutOptOrderType, FutOptPriceType, CallPut,
        )
        return FubonSDK, Order
    except ImportError:
        print(json.dumps({
            "success": False,
            "error": "fubon_neo SDK not installed. Install the .whl file first: pip install fubon_neo-2.2.8-cp37-abi3-win_amd64.whl"
        }))
        sys.exit(1)


def save_session(personal_id, password, cert_path, cert_password):
    """Save login credentials to session file."""
    data = {
        "personal_id": personal_id,
        "password": password,
        "cert_path": cert_path,
        "cert_password": cert_password,
    }
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def load_session():
    """Load saved credentials from session file."""
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def clear_session():
    """Remove session file."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def get_sdk_and_accounts():
    """Create SDK instance, login with saved session, return (sdk, accounts_data).

    Returns:
        tuple: (sdk_instance, list_of_account_objects)
    """
    session = load_session()
    if session is None:
        print(json.dumps({
            "success": False,
            "error": "Not logged in. Run: fubon login --id <ID> --password <PW> --cert-path <PATH> --cert-password <PW>"
        }))
        sys.exit(1)

    FubonSDK, _ = _import_sdk()
    sdk = FubonSDK()

    args = [session["personal_id"], session["password"], session["cert_path"]]
    if session.get("cert_password"):
        args.append(session["cert_password"])

    result = sdk.login(*args)

    if not getattr(result, "is_success", False):
        msg = getattr(result, "message", "Unknown login error")
        print(json.dumps({"success": False, "error": f"Login failed: {msg}"}))
        sys.exit(1)

    return sdk, result.data


def get_account(sdk, accounts, index=0):
    """Get a specific account from the accounts list."""
    if index < 0 or index >= len(accounts):
        print(json.dumps({
            "success": False,
            "error": f"Account index {index} out of range. Available: 0-{len(accounts) - 1}"
        }))
        sys.exit(1)
    return accounts[index]


def obj_to_dict(obj):
    """Convert an SDK result object to a JSON-serializable dict."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [obj_to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: obj_to_dict(v) for k, v in obj.items()}

    # Try __dict__ first
    if hasattr(obj, "__dict__") and obj.__dict__:
        return {k: obj_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith("_")}

    # Try str/repr for SDK objects (pyo3 objects use __repr__)
    text = str(obj)
    if "{" in text:
        return _parse_sdk_repr(text)

    return text


def _parse_sdk_repr(text):
    """Parse SDK object repr like 'ClassName { field: value, ... }' into dict."""
    import re
    # Remove outer class name and braces
    match = re.match(r"^\w+\s*\{(.*)\}\s*$", text, re.DOTALL)
    if not match:
        return text

    inner = match.group(1).strip()
    if not inner:
        return {}

    result = {}
    # Split on commas that are not inside braces/brackets
    depth = 0
    current = ""
    parts = []
    for ch in inner:
        if ch in "({[":
            depth += 1
            current += ch
        elif ch in ")}]":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current.strip())

    for part in parts:
        colon_idx = part.find(":")
        if colon_idx == -1:
            continue
        key = part[:colon_idx].strip()
        val = part[colon_idx + 1:].strip()

        # Parse value
        if val == "None" or val == "null":
            result[key] = None
        elif val == "True" or val == "true":
            result[key] = True
        elif val == "False" or val == "false":
            result[key] = False
        elif val.startswith('"') and val.endswith('"'):
            result[key] = val[1:-1]
        else:
            try:
                result[key] = int(val)
            except ValueError:
                try:
                    result[key] = float(val)
                except ValueError:
                    # Could be nested object or enum
                    if "{" in val:
                        result[key] = _parse_sdk_repr(val)
                    else:
                        result[key] = val

    return result


def format_result(result, as_json=True):
    """Format an SDK result for output."""
    data = obj_to_dict(result)
    if as_json:
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)
    return str(data)


def output(data, success=True, error=None):
    """Print a standardized JSON response."""
    response = {"success": success}
    if error:
        response["error"] = error
    if data is not None:
        response["data"] = data
    print(json.dumps(response, ensure_ascii=False, indent=2, default=str))
