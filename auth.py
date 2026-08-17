import hmac
import os

from fastapi import HTTPException, Request


DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"
DEFAULT_TESTER_USERNAME = "tester"
DEFAULT_TESTER_PASSWORD = "tester"


def configured_accounts():
    """Return the two supported prototype accounts and their authorization roles."""
    return {
        os.environ.get("APP_USERNAME", DEFAULT_ADMIN_USERNAME): {
            "password": os.environ.get("APP_PASSWORD", DEFAULT_ADMIN_PASSWORD),
            "role": "admin",
        },
        os.environ.get("TESTER_USERNAME", DEFAULT_TESTER_USERNAME): {
            "password": os.environ.get("TESTER_PASSWORD", DEFAULT_TESTER_PASSWORD),
            "role": "tester",
        },
    }


def authenticate(username: str, password: str):
    account = configured_accounts().get(username)
    if not account or not hmac.compare_digest(password, account["password"]):
        return None
    return {"username": username, "role": account["role"]}


def is_logged_in(request: Request):
    return request.session.get("logged_in") is True


def is_admin(request: Request):
    return is_logged_in(request) and request.session.get("role") == "admin"


def require_admin(request: Request):
    if not is_logged_in(request):
        raise HTTPException(status_code=401, detail="Login required")
    if not is_admin(request):
        raise HTTPException(status_code=403, detail="Administrator access required")
    return request.session.get("username")
