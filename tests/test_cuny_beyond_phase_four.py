from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_supported_career_catalog_is_public_and_used_by_onboarding():
    api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
    html = (ROOT / "frontend" / "cuny_beyond.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend" / "cuny_beyond.js").read_text(encoding="utf-8")
    assert '@router.get("/cuny-beyond/careers")' in api
    assert 'id="career-options"' in html
    assert 'id="career-suggestions"' in html
    assert "/api/db/cuny-beyond/careers" in js
    assert "data-retry-career" in js


def test_major_change_entry_opens_at_the_correct_guided_step():
    page = (ROOT / "frontend" / "program_selector.html").read_text(encoding="utf-8")
    assert 'get("intent")' in page
    assert 'entryIntent === "major-change"' in page
    assert 'SMART_STATE.advisingIntent = "change_major"' in page
    assert "SMART_STATE.step = 3" in page


def test_major_change_reuses_snapshot_and_limits_shortlist():
    page = (ROOT / "frontend" / "transfer_analysis.html").read_text(encoding="utf-8")
    assert 'sessionStorage.getItem("transferSnapshot")' in page
    assert 'sessionStorage.getItem("majorChangeShortlist")' in page
    assert "MAJOR_CHANGE_SHORTLIST.length >= 3" in page
    assert 'program.code === sourceProgramCode' in page
    assert 'institution.code === sourceInstitutionCode' in page


def test_major_change_explains_outcomes_and_official_next_steps():
    page = (ROOT / "frontend" / "transfer_analysis.html").read_text(encoding="utf-8")
    for expected in (
        "Current major",
        "Proposed majors (up to 3)",
        "Completed Courses Not Automatically Applied",
        "Advisor Review Recommended",
        "Completed credits applied",
        "Prerequisite sequence:",
        "student-resources-forms/student-forms/",
        "academics/advisement/advisement/",
    ):
        assert expected in page
