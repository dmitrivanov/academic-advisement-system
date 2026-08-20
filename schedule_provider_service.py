"""Fail-closed contract for future approved live-section providers.

This module deliberately performs no scraping or network I/O. A provider can only
be enabled after governance fields are complete; until an official response
contract is implemented, callers receive a guided-search fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


REQUIRED_APPROVAL_FIELDS = (
    "api_base_url", "data_owner", "permission_reference", "attribution", "support_contact",
)


def validate_provider_config(config) -> list[str]:
    errors = []
    if config.approval_status not in {"not_approved", "pending", "approved", "revoked"}:
        errors.append("Unknown approval status")
    if config.enabled:
        if config.approval_status != "approved":
            errors.append("Provider must be approved before it can be enabled")
        for field in REQUIRED_APPROVAL_FIELDS:
            if not (getattr(config, field, None) or "").strip():
                errors.append(f"{field.replace('_', ' ').title()} is required")
        if not (config.api_base_url or "").startswith("https://"):
            errors.append("API base URL must use HTTPS")
        if not 30 <= config.refresh_seconds <= 86400:
            errors.append("Refresh interval must be between 30 and 86400 seconds")
        if not config.refresh_seconds <= config.retention_seconds <= 604800:
            errors.append("Retention must be at least the refresh interval and no more than 7 days")
    return errors


class CircuitBreaker:
    def __init__(self, failure_threshold=3, cooldown_seconds=300):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures = 0
        self.opened_at = None

    def can_attempt(self, now=None):
        now = now or datetime.now(timezone.utc)
        return not self.opened_at or now >= self.opened_at + timedelta(seconds=self.cooldown_seconds)

    def record_success(self):
        self.failures, self.opened_at = 0, None

    def record_failure(self, now=None):
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = now or datetime.now(timezone.utc)

    @property
    def state(self):
        return "open" if self.opened_at else "closed"


@dataclass(frozen=True)
class SectionResult:
    course_code: str
    section: str
    meeting_pattern: str
    modality: str
    campus: str
    status: str
    source_url: str
    fetched_at: str


def provider_readiness(config):
    if config is None:
        return {"ready": False, "reason": "official_provider_not_configured", "errors": []}
    errors = validate_provider_config(config)
    if not config.enabled:
        return {"ready": False, "reason": "official_provider_not_enabled", "errors": errors}
    if errors:
        return {"ready": False, "reason": "official_provider_not_approved", "errors": errors}
    # The official schema/credentials adapter is intentionally still gated.
    return {"ready": False, "reason": "official_provider_adapter_pending", "errors": []}


def build_section_fallback(config, handoff):
    readiness = provider_readiness(config)
    return {
        "mode": "guided_handoff",
        "live_sections": [],
        "live_data_claimed": False,
        "provider_status": readiness,
        "source": {
            "name": getattr(config, "name", None) or "CUNY Global Search",
            "attribution": getattr(config, "attribution", None),
            "fetched_at": None,
        },
        "handoff": handoff,
    }
