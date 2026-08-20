"""Configuration shared by the public CUNY Beyond prototype."""

from __future__ import annotations

import os


FALSE_VALUES = {"0", "false", "no", "off"}
DEFAULT_SESSION_TTL_HOURS = 24


def is_cuny_beyond_enabled() -> bool:
    """Return whether the public prototype should be served."""
    return os.environ.get("CUNY_BEYOND_ENABLED", "true").strip().lower() not in FALSE_VALUES


def session_ttl_hours() -> int:
    """Return a bounded lifetime for anonymous browser drafts."""
    raw_value = os.environ.get("CUNY_BEYOND_SESSION_TTL_HOURS", str(DEFAULT_SESSION_TTL_HOURS))
    try:
        value = int(raw_value)
    except ValueError:
        return DEFAULT_SESSION_TTL_HOURS
    return min(max(value, 1), 168)


def public_config() -> dict[str, int | bool]:
    return {
        "enabled": is_cuny_beyond_enabled(),
        "session_ttl_hours": session_ttl_hours(),
    }
