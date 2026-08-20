import csv
from pathlib import Path

from cuny_beyond_matching import rank_program_matches, resolve_career


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def read_csv(name):
    with (DOCS / name).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def test_career_dataset_has_unique_sourced_records_and_five_skills():
    skills = read_csv("cuny_beyond_skills.csv")
    careers = read_csv("cuny_beyond_careers.csv")
    skill_slugs = {row["slug"] for row in skills}
    assert len(skill_slugs) == len(skills)
    assert len({row["slug"] for row in careers}) == len(careers)
    assert "data-analyst" in {row["slug"] for row in careers}
    for row in careers:
        references = row["skill_slugs"].split("|")
        assert len(references) >= 5
        assert set(references) <= skill_slugs
        assert row["source_url"].startswith("https://")
        assert row["source_title"] and row["reviewed_at"]


def test_program_mappings_reference_existing_populated_curricula():
    mappings = read_csv("cuny_beyond_program_careers.csv")
    careers = {row["slug"] for row in read_csv("cuny_beyond_careers.csv")}
    populated_programs = set()
    for path in DOCS.glob("*_courses.csv"):
        rows = read_csv(path.name)
        for row in rows:
            code = row.get("program_code")
            if code:
                populated_programs.add(code)
    assert len({(row["institution_code"], row["program_code"], row["career_slug"]) for row in mappings}) == len(mappings)
    for row in mappings:
        assert row["career_slug"] in careers
        assert row["program_code"] in populated_programs
        assert row["source_url"].startswith("https://")
        assert row["official_program_url"].startswith("https://")
        assert row["explanation"] and row["reviewed_at"]


def test_data_analyst_resolves_and_ranks_three_programs_stably(monkeypatch):
    career = resolve_career("I want to become a data analyst", [{
        "slug": "data-analyst", "name": "Data Analyst", "aliases": ["data analytics"]
    }])
    assert career["slug"] == "data-analyst"
    monkeypatch.setenv("CUNY_BEYOND_SKILL_POINTS", "6")
    mappings = [
        {"program_code": "CIS", "program_name": "Computer Information Systems", "career_points": 38, "career_skills": ["Analyzing data"], "has_curriculum": True},
        {"program_code": "CS", "program_name": "Computer Science", "career_points": 44, "career_skills": ["Analyzing data"], "has_curriculum": True},
        {"program_code": "DS_AS", "program_name": "Data Science", "career_points": 50, "career_skills": ["Analyzing data"], "has_curriculum": True},
    ]
    ranked = rank_program_matches(mappings, ["Analyzing data"])
    assert [item["program_code"] for item in ranked] == ["DS_AS", "CS", "CIS"]
    assert ranked[0]["score_components"] == {"career": 50, "skills": 6}


def test_empty_curriculum_and_low_evidence_are_not_recommended(monkeypatch):
    monkeypatch.setenv("CUNY_BEYOND_MINIMUM_SCORE", "40")
    mappings = [
        {"program_code": "EMPTY", "program_name": "Empty", "career_points": 80, "career_skills": [], "has_curriculum": False},
        {"program_code": "LOW", "program_name": "Low", "career_points": 39, "career_skills": [], "has_curriculum": True},
    ]
    assert rank_program_matches(mappings, []) == []


def test_results_ui_links_to_existing_degree_planner_without_reselection():
    html = (ROOT / "frontend" / "cuny_beyond.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend" / "cuny_beyond.js").read_text(encoding="utf-8")
    api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
    assert 'id="recommendation-results"' in html
    assert "selectedProgramContext" in js
    assert "window.location.href = '/db-progress'" in js
    assert '@router.post("/cuny-beyond/recommendations")' in api
