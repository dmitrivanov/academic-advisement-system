from pathlib import Path

from cuny_beyond import is_cuny_beyond_enabled, session_ttl_hours


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "frontend" / "cuny_beyond.html").read_text(encoding="utf-8")
JS = (ROOT / "frontend" / "cuny_beyond.js").read_text(encoding="utf-8")
API = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")


def test_public_route_does_not_require_login():
    route = API.split('@app.get("/cuny-beyond")', 1)[1].split('@app.get("/api/cuny-beyond/config")', 1)[0]
    assert "is_logged_in" not in route
    assert 'FileResponse("frontend/cuny_beyond.html")' in route


def test_feature_flag_can_disable_public_route(monkeypatch):
    monkeypatch.setenv("CUNY_BEYOND_ENABLED", "false")
    assert not is_cuny_beyond_enabled()
    assert 'raise HTTPException(status_code=404' in API


def test_anonymous_draft_lifetime_is_bounded(monkeypatch):
    monkeypatch.setenv("CUNY_BEYOND_SESSION_TTL_HOURS", "999")
    assert session_ttl_hours() == 168
    monkeypatch.setenv("CUNY_BEYOND_SESSION_TTL_HOURS", "invalid")
    assert session_ttl_hours() == 24


def test_intake_has_all_six_profiles_and_five_skill_limit():
    for profile in ("high_school", "working_adult", "some_college", "transfer", "returning", "degree_holder"):
        assert f'value="{profile}"' in HTML
    assert "const MAX_SKILLS = 5" in JS
    assert "slice(0, MAX_SKILLS)" in JS


def test_intake_has_accessibility_and_privacy_controls():
    assert 'class="skip-link"' in HTML
    assert 'role="alert"' in HTML
    assert 'aria-live="polite"' in HTML
    assert "Do not enter your name, email, CUNY ID" in HTML
    assert "localStorage.removeItem(STORAGE_KEY)" in JS
    assert "Date.now() >= draft.expiresAt" in JS


def test_current_student_handoff_uses_login_and_current_student_tag():
    assert 'class="login-link" href="/login">Log in</a>' in HTML
    assert 'value="current_bmcc"' in HTML
    assert "Current BMCC student" in HTML
