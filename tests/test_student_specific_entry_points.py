from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
CHAT = (ROOT / "frontend" / "cuny_beyond.js").read_text(encoding="utf-8")
LOGIN = (ROOT / "frontend" / "login.html").read_text(encoding="utf-8")
ADVISOR = (ROOT / "frontend" / "advising_entry_context.js").read_text(encoding="utf-8")
PLANNER = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
TRANSFER = (ROOT / "frontend" / "transfer_analysis.html").read_text(encoding="utf-8")
REFERRAL = (ROOT / "frontend" / "cuny_beyond_referral.html").read_text(encoding="utf-8")


def test_both_entry_routes_reuse_the_existing_chatbot_file_and_authentication():
    for route, handler in (
        ("/bmcc_student", "serve_bmcc_student_entry"),
        ("/high_school_student", "serve_high_school_student_entry"),
    ):
        assert f'@app.get("{route}")' in API
        assert f"def {handler}" in API
    configured = API.split("def serve_configured_advising_entry", 1)[1].split("@app.get", 1)[0]
    assert "is_logged_in(request)" in configured
    assert 'FileResponse("frontend/cuny_beyond.html")' in configured
    assert 'RedirectResponse(f"/?next={entry_path}"' in configured


def test_legacy_entry_route_remains_independent():
    legacy = API.split('@app.get("/advising-app_v1")', 1)[1].split("def serve_configured_advising_entry", 1)[0]
    assert "is_logged_in(request)" in legacy
    assert 'FileResponse("frontend/cuny_beyond.html")' in legacy
    assert "serve_configured_advising_entry" not in legacy


def test_direct_entries_preselect_and_namespace_the_student_context():
    assert "'/bmcc_student': { profile: 'current_bmcc', entryMode: 'current_student'" in CHAT
    assert "'/high_school_student': { profile: 'high_school', entryMode: 'high_school_student'" in CHAT
    assert "state.step = Math.max(1, state.step)" in CHAT
    assert "ENTRY_CONTEXT && state.step === 1" in CHAT
    assert "`${BASE_STORAGE_KEY}:${ENTRY_CONTEXT.entryMode}`" in CHAT
    assert "previousEntry !== window.location.pathname" in CHAT
    assert "clearSessionAdvisingContext()" in CHAT


def test_login_round_trip_is_allowlisted():
    assert 'name="next"' in LOGIN
    assert 'Form("", alias="next")' in API
    assert "safe_login_return_path(next_path)" in API
    for path in ("/bmcc_student", "/high_school_student", "/advising-app_v1"):
        assert path in API
        assert path in LOGIN


def test_tool_return_paths_reuse_the_active_entry_url():
    assert "cunyBeyondEntryPathV1" in ADVISOR
    assert "cunyBeyondEntryPathV1" in PLANNER
    assert "cunyBeyondEntryPathV1" in TRANSFER
    assert "cunyBeyondEntryPathV1" in REFERRAL
    assert 'a[href^="/advising-app_v1?returned="]' in ADVISOR


def test_prospective_context_does_not_assume_completed_coursework():
    assert "if (!isCurrentStudent() && !reportedCourses.length)" in CHAT
    assert "sessionStorage.removeItem('cunyBeyondImportedCoursesV1')" in CHAT
    assert "studentStatus: isCurrentStudent() ? 'current' : 'prospective'" in CHAT
