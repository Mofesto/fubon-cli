"""Authentication commands: login, logout, status."""

import sys

import click

from fubon_cli.core import (
    clear_session,
    get_sdk_and_accounts,
    load_session,
    obj_to_dict,
    output,
    save_session,
)


@click.group("login", invoke_without_command=True)
@click.option("--id", "personal_id", required=False, help="Personal ID (身分證字號)")
@click.option("--password", required=False, default=None, help="Login password")
@click.option("--api-key", "api_key", required=False, default=None, help="API Key (v2.2.7+)")
@click.option("--cert-path", required=False, help="Path to certificate file")
@click.option("--cert-password", default=None, help="Certificate password (defaults to ID)")
@click.pass_context
def auth_group(ctx, personal_id, password, api_key, cert_path, cert_password):
    """Login, logout, and session management.

    \b
    Password login:  fubon login --id <ID> --password <PW> --cert-path <PATH>
    API Key login:   fubon login --id <ID> --api-key <KEY> --cert-path <PATH>
    Logout:          fubon login logout
    Status:          fubon login status
    """
    if ctx.invoked_subcommand is not None:
        return

    # Validate credential options
    if password and api_key:
        output(
            None,
            success=False,
            error="Cannot use --password and --api-key together. Choose one login method.",
        )
        sys.exit(1)

    if not personal_id or not cert_path:
        output(
            None,
            success=False,
            error=(
                "Missing required options. Usage:\n"
                "  fubon login --id <ID> --password <PW> --cert-path <PATH>\n"
                "  fubon login --id <ID> --api-key <KEY> --cert-path <PATH>"
            ),
        )
        sys.exit(1)

    if not password and not api_key:
        output(
            None,
            success=False,
            error=(
                "Provide either --password or --api-key. Usage:\n"
                "  fubon login --id <ID> --password <PW> --cert-path <PATH>\n"
                "  fubon login --id <ID> --api-key <KEY> --cert-path <PATH>"
            ),
        )
        sys.exit(1)

    try:
        from fubon_neo.sdk import FubonSDK
    except ImportError:
        output(
            None,
            success=False,
            error="fubon_neo SDK not installed. Run: pip install fubon_neo-2.2.8-cp37-abi3-win_amd64.whl",
        )
        sys.exit(1)

    sdk = FubonSDK()

    if api_key:
        # API Key login (v2.2.7+)
        args = [personal_id, api_key, cert_path]
        if cert_password:
            args.append(cert_password)
        result = sdk.apikey_login(*args)
        if not getattr(result, "is_success", False):
            msg = getattr(result, "message", "Unknown error")
            output(None, success=False, error=f"API Key login failed: {msg}")
            sys.exit(1)
        save_session(
            personal_id, None, cert_path, cert_password or "",
            login_type="apikey", api_key=api_key,
        )
    else:
        # Password login
        args = [personal_id, password, cert_path]
        if cert_password:
            args.append(cert_password)
        result = sdk.login(*args)
        if not getattr(result, "is_success", False):
            msg = getattr(result, "message", "Unknown error")
            output(None, success=False, error=f"Login failed: {msg}")
            sys.exit(1)
        save_session(personal_id, password, cert_path, cert_password or "")

    accounts = []
    for acc in result.data:
        accounts.append(obj_to_dict(acc))

    output({"accounts": accounts}, success=True)


@auth_group.command("logout")
def logout():
    """Clear saved session credentials."""
    clear_session()
    output({"message": "Logged out successfully"}, success=True)


@auth_group.command("status")
def status():
    """Check current login status."""
    session = load_session()
    if session is None:
        output({"logged_in": False}, success=True)
    else:
        login_type = session.get("login_type", "password")
        output(
            {
                "logged_in": True,
                "login_type": login_type,
                "personal_id": session["personal_id"][:3] + "***",
                "cert_path": session["cert_path"],
            },
            success=True,
        )
