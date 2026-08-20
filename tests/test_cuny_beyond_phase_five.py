from types import SimpleNamespace
from pathlib import Path

import pytest

from schedule_link_service import build_global_search_handoff, parse_course_code


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("raw,subject,catalog", [
    ("MAT 301", "MAT", "301"),
    ("MAT 157.5", "MAT", "157.5"),
    ("CSC 111H", "CSC", "111H"),
    ("ENGL101", "ENGL", "101"),
])
def test_course_code_normalization(raw, subject, catalog):
    parsed = parse_course_code(raw)
    assert parsed.subject == subject
    assert parsed.catalog_number == catalog


def test_unmappable_course_and_campus_fail_closed():
    term = SimpleNamespace(name="2026 Fall Term", provider_code="1269", verified_at=__import__("datetime").datetime(2026, 8, 21))
    with pytest.raises(ValueError):
        parse_course_code("Liberal Arts Elective")
    with pytest.raises(ValueError):
        build_global_search_handoff("UNKNOWN", term, "MAT 301")


def test_handoff_is_guided_and_does_not_claim_prefill():
    term = SimpleNamespace(name="2026 Fall Term", provider_code="1269", verified_at=__import__("datetime").datetime(2026, 8, 21))
    result = build_global_search_handoff("BMCC", term, "MAT 157.5", "Online", "Evening")
    assert result["prefilled"] is False
    assert result["institution_label"] == "Borough of Manhattan CC"
    assert result["course"]["catalog_number"] == "157.5"
    assert "Register in CUNYfirst" in result["disclaimer"]
    assert result["url"].startswith("https://globalsearch.cuny.edu/")


def test_term_admin_and_student_interfaces_are_connected():
    api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    student = (ROOT / "frontend" / "schedule_handoff.html").read_text(encoding="utf-8")
    admin = (ROOT / "frontend" / "schedule_settings.html").read_text(encoding="utf-8")
    assert '@router.get("/cuny-beyond/schedule/terms")' in api
    assert '@router.post("/cuny-beyond/schedule/handoff")' in api
    assert '@router.put("/admin/schedule/terms/{term_id}")' in api
    assert '@app.get("/schedule-handoff")' in server
    assert "Copy checklist" in student and "Open CUNY Global Search" in student
    assert "/api/db/admin/schedule/terms" in admin


def test_find_sections_is_available_from_both_planning_results():
    progress = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
    comparison = (ROOT / "frontend" / "transfer_analysis.html").read_text(encoding="utf-8")
    assert "Find Sections" in progress
    assert "Find Sections" in comparison
    assert "/schedule-handoff?institution_code=" in progress
    assert "/schedule-handoff?institution_code=" in comparison

