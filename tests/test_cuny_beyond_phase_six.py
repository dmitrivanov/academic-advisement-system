from pathlib import Path

import faq_fallback_api as api


ROOT = Path(__file__).resolve().parents[1]


def sample_summary():
    return {
        "pathway": "High-school student", "career_goal": "Data Analyst",
        "matched_career": "Data Analyst", "skills": ["Analyzing data"] * 8,
        "recommended_programs": [{"code": "DS_AS", "name": "Data Science", "explanation": "Reviewed match", "extra": "drop"}] * 5,
        "cpl_possibilities": [{"name": "AP exam", "next_step": "Request evaluation"}],
        "completed_courses": [{"code": "ENG 101"}],
        "schedule_checklist": {"instructions": ["Select institution: Borough of Manhattan CC"]},
    }


def test_summary_is_whitelisted_and_bounded():
    clean = api.clean_referral_summary(sample_summary())
    assert len(clean["skills"]) == 5
    assert len(clean["recommended_programs"]) == 3
    assert "extra" not in clean["recommended_programs"][0]
    assert clean["completed_courses"] == ["ENG 101"]


def test_manual_fallback_requires_consent_and_returns_copyable_email(monkeypatch):
    events = []
    monkeypatch.setattr(api, "log_referral_delivery", lambda *args: events.append(args))
    monkeypatch.delenv("BMCC_ADVISING_REFERRAL_ENABLED", raising=False)
    payload = api.AdvisingReferralPayload(
        name="Test Student", email="student@example.edu", id_last_four="1234",
        consent=True, summary=sample_summary(),
    )
    result = api.submit_cuny_beyond_referral(payload)
    assert result["sent"] is False
    assert "Data Analyst" in result["subject"]
    assert "Test Student" in result["body"]
    assert events[0][1:] == ("prepared", "manual_fallback")


def test_delivery_log_schema_excludes_student_pii():
    source = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    logger = source.split("def log_referral_delivery", 1)[1].split("@app.post", 1)[0]
    assert '"event_id"' in logger and '"status"' in logger and '"delivery_mode"' in logger
    for forbidden in ('"name"', '"email"', '"id_last_four"', '"summary"'):
        assert forbidden not in logger


def test_public_referral_page_has_consent_exports_and_failure_fallback():
    page = (ROOT / "frontend" / "cuny_beyond_referral.html").read_text(encoding="utf-8")
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    assert '@app.get("/cuny-beyond/referral")' in server
    assert '@app.post("/api/cuny-beyond/referral")' in server
    for text in ("Save / Print PDF", "Download text summary", "Last 4 ID digits", "I consent", "Prepared email fallback"):
        assert text in page
    assert "session_access.js" not in page


def test_phase_six_summary_carries_prior_phase_context():
    onboarding = (ROOT / "frontend" / "cuny_beyond.js").read_text(encoding="utf-8")
    schedule = (ROOT / "frontend" / "schedule_handoff.html").read_text(encoding="utf-8")
    for field in ("recommended_programs", "cpl_possibilities", "completed_courses", "transfer_options", "schedule_checklist", "sources"):
        assert field in onboarding
    assert "cunyBeyondScheduleChecklistV1" in schedule
    assert "cunyBeyondReferralSummaryV1" in onboarding

