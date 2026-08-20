import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def rows(name):
    with (DOCS / name).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def populated_program_codes():
    result = set()
    for path in DOCS.glob("*_courses.csv"):
        for row in rows(path.name):
            if row.get("program_code"):
                result.add(row["program_code"])
    return result


def test_every_active_career_has_a_unique_active_mapping():
    careers = [row for row in rows("cuny_beyond_careers.csv") if row["active"] == "true"]
    mappings = [row for row in rows("cuny_beyond_program_careers.csv") if row["active"] == "true"]
    mapped = {row["career_slug"] for row in mappings}
    assert {row["slug"] for row in careers} <= mapped
    keys = [(row["institution_code"], row["program_code"], row["career_slug"]) for row in mappings]
    assert len(keys) == len(set(keys))


def test_active_mappings_have_sources_explanations_and_curricula():
    populated = populated_program_codes()
    for row in rows("cuny_beyond_program_careers.csv"):
        if row["active"] != "true":
            continue
        assert row["source_url"].startswith("https://")
        assert row["official_program_url"].startswith("https://")
        assert row["source_title"] and row["explanation"] and row["reviewed_at"]
        assert row["program_code"] in populated


def test_registered_nurse_is_reviewed_and_maps_only_to_populated_nursing_aas():
    career = next(row for row in rows("cuny_beyond_careers.csv") if row["slug"] == "registered-nurse")
    mapping = next(row for row in rows("cuny_beyond_program_careers.csv") if row["career_slug"] == "registered-nurse")
    assert "RN" in career["aliases"] and career["active"] == "true"
    assert mapping["program_code"] == "NUR_AAS"
    assert mapping["evidence_level"] == "strong"
    assert "nursing/nursing-program" in mapping["source_url"]


def test_governance_workflow_is_admin_only_versioned_and_fail_closed():
    api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
    page = (ROOT / "frontend" / "governance_dashboard.html").read_text(encoding="utf-8")
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    for route in ("/admin/governance/dashboard", "/admin/governance/catalog", "/admin/governance/drafts"):
        assert route in api
    assert "GovernanceDraftVersion" in api
    assert '"draft": {"review"}' in api
    assert '"review": {"draft", "approved"}' in api
    assert '"approved": {"published", "draft"}' in api
    assert 'draft.source_url.startswith("https://")' in api
    assert 'if payload.action == "archived": archive_governed_entity' in api
    assert "Rollback previous" in page
    assert '@app.get("/admin/cuny-beyond-governance")' in server


def test_public_recommendations_never_query_governance_drafts():
    api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
    public = api.split('@router.post("/cuny-beyond/recommendations")', 1)[1].split('@router.post("/cuny-beyond/cpl-screening")', 1)[0]
    assert "GovernanceDraft" not in public
    assert "ProgramCareer.active.is_(True)" in public


def test_seed_does_not_overwrite_admin_governed_records():
    seed = (ROOT / "seed_database.py").read_text(encoding="utf-8")
    mapping_section = seed.split("def seed_cuny_beyond_mappings", 1)[1].split("def seed_cuny_beyond_cpl", 1)[0]
    assert "if existing:\n            continue" in mapping_section
    assert "ProgramCareer.career_id.in_" not in mapping_section
