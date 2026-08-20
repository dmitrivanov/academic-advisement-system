import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def read_csv(name):
    with (DOCS / name).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def test_cpl_types_are_complete_published_and_source_backed():
    rows = read_csv("cuny_beyond_cpl_types.csv")
    expected = {
        "previous-college-credit", "standardized-exams", "ace-reviewed-learning",
        "employer-training", "military-learning", "licenses-certifications",
        "biliteracy-language", "portfolio-experiential",
    }
    assert {row["code"] for row in rows} == expected
    for row in rows:
        assert row["description"] and row["evidence_requested"] and row["next_step"]
        assert row["official_url"].startswith("https://")
        assert row["source_title"] and row["reviewed_at"]
        assert row["status"] == "published" and row["active"] == "true"


def test_program_cpl_guidance_references_existing_program_and_type():
    types = {row["code"] for row in read_csv("cuny_beyond_cpl_types.csv")}
    guidance = read_csv("cuny_beyond_program_cpl_guidance.csv")
    populated = set()
    for path in DOCS.glob("*_courses.csv"):
        for row in read_csv(path.name):
            if row.get("program_code"):
                populated.add(row["program_code"])
    assert len({(row["institution_code"], row["program_code"], row["cpl_type_code"]) for row in guidance}) == len(guidance)
    for row in guidance:
        assert row["program_code"] in populated
        assert row["cpl_type_code"] in types
        assert row["guidance"] and row["evidence_requested"]
        assert row["source_url"].startswith("https://")
        assert row["status"] == "published"


def test_public_cpl_contract_is_nonbinding_and_does_not_change_degree_totals():
    api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
    endpoint = api.split('@router.post("/cuny-beyond/cpl-screening")', 1)[1]
    assert "Possible CPL opportunity - evaluation required" in endpoint
    assert "Nothing here changes remaining credits or degree totals" in endpoint
    assert "Unknown CPL selection" in endpoint
    assert "ProgramCourse" not in endpoint.split("return {", 1)[0]


def test_questionnaire_supports_all_paths_not_sure_and_none():
    html = (ROOT / "frontend" / "cuny_beyond.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend" / "cuny_beyond.js").read_text(encoding="utf-8")
    for code in (
        "previous-college-credit", "standardized-exams", "ace-reviewed-learning",
        "employer-training", "military-learning", "licenses-certifications",
        "biliteracy-language", "portfolio-experiential", "not-sure", "none",
    ):
        assert f'value="{code}"' in html
    assert "if (changed.value === 'none')" in js
    assert "cplSelections" in js
    assert "/api/db/cuny-beyond/cpl-screening" in js


def test_cpl_results_are_visually_separate_from_program_recommendations():
    html = (ROOT / "frontend" / "cuny_beyond.html").read_text(encoding="utf-8")
    assert 'id="recommendation-results"' in html
    assert 'id="cpl-results-section"' in html
    assert 'id="cpl-disclaimer"' in html
    assert 'id="cpl-checklist"' in html
