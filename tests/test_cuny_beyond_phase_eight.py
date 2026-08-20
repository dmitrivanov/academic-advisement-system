from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from schedule_provider_service import CircuitBreaker, build_section_fallback, provider_readiness, validate_provider_config


ROOT = Path(__file__).resolve().parents[1]


def config(**overrides):
    values = dict(enabled=False, approval_status="not_approved", api_base_url=None,
        data_owner=None, permission_reference=None, attribution=None, support_contact=None,
        refresh_seconds=300, retention_seconds=900, name="CUNY official live sections")
    values.update(overrides)
    return SimpleNamespace(**values)


def test_live_provider_is_fail_closed_until_approved_and_complete():
    assert provider_readiness(None)["reason"] == "official_provider_not_configured"
    assert provider_readiness(config())["reason"] == "official_provider_not_enabled"
    errors = validate_provider_config(config(enabled=True, approval_status="pending"))
    assert "Provider must be approved before it can be enabled" in errors
    assert "API base URL must use HTTPS" in errors


def test_complete_governance_is_still_adapter_gated():
    approved = config(enabled=True, approval_status="approved", api_base_url="https://api.example.edu",
        data_owner="Registrar", permission_reference="Agreement 123", attribution="CUNY",
        support_contact="support@example.edu")
    assert validate_provider_config(approved) == []
    assert provider_readiness(approved)["reason"] == "official_provider_adapter_pending"


def test_fallback_never_claims_live_sections_or_seats():
    handoff = {"provider": "CUNY Global Search", "instructions": ["Select term"]}
    result = build_section_fallback(config(), handoff)
    assert result["mode"] == "guided_handoff"
    assert result["live_sections"] == []
    assert result["live_data_claimed"] is False
    assert result["handoff"] is handoff


def test_circuit_breaker_opens_and_recovers_after_cooldown():
    now = datetime(2026, 8, 21, tzinfo=timezone.utc)
    breaker = CircuitBreaker(failure_threshold=2, cooldown_seconds=60)
    breaker.record_failure(now); assert breaker.can_attempt(now)
    breaker.record_failure(now); assert breaker.state == "open" and not breaker.can_attempt(now)
    assert breaker.can_attempt(now + timedelta(seconds=61))
    breaker.record_success(); assert breaker.state == "closed"


def test_phase_eight_routes_ui_and_no_scraping_contract():
    api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
    service = (ROOT / "schedule_provider_service.py").read_text(encoding="utf-8")
    student = (ROOT / "frontend/schedule_handoff.html").read_text(encoding="utf-8")
    admin = (ROOT / "frontend/schedule_settings.html").read_text(encoding="utf-8")
    assert '@router.post("/cuny-beyond/schedule/sections")' in api
    assert '@router.get("/admin/schedule/provider")' in api
    assert '@router.put("/admin/schedule/provider")' in api
    assert "Depends(require_admin)" in api
    assert "/api/db/cuny-beyond/schedule/sections" in student and 'aria-live="polite"' in student
    assert "/api/db/admin/schedule/provider" in admin and "Enable live provider" in admin
    assert "requests.get" not in service and "BeautifulSoup" not in service


def test_seed_preserves_existing_admin_provider_configuration():
    seed = (ROOT / "seed_database.py").read_text(encoding="utf-8")
    assert 'if not db.query(ScheduleProviderConfig).filter_by(code="cuny_official_sections").first()' in seed
