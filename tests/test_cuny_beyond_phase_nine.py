import csv
from pathlib import Path

from cuny_beyond_matching import resolve_career


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def rows(name):
    with (DOCS / name).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def career_records():
    return [{"name": row["name"], "aliases": row["aliases"].split("|")}
            for row in rows("cuny_beyond_careers.csv") if row["active"] == "true"]


def test_phase_nine_expands_reviewed_catalog_and_program_families():
    careers = rows("cuny_beyond_careers.csv")
    mappings = rows("cuny_beyond_program_careers.csv")
    assert len([row for row in careers if row["active"] == "true"]) >= 46
    assert len([row for row in mappings if row["active"] == "true"]) >= 50
    assert {"ACCT_AAS", "HMS_AS", "PSY_AA", "PSY_STEM_AA", "CRJ_AA", "PNA_AS", "URB_AA", "POL_AA", "GER_AS"} <= {row["program_code"] for row in mappings}


def test_reproducible_aliases_resolve_to_reviewed_careers():
    careers = career_records()
    expected = {"bookkeeper": "Accounting Clerk", "case worker": "Case Manager",
        "law enforcement": "Police Officer", "city planner": "Urban Planner",
        "healthcare administrator": "Health Services Administrator"}
    for phrase, name in expected.items():
        assert resolve_career(phrase, careers)["name"] == name


def test_new_mappings_disclose_education_or_credential_limits_where_needed():
    mappings = rows("cuny_beyond_program_careers.csv")
    explanations = lambda slug: " ".join(row["explanation"] for row in mappings if row["career_slug"] == slug)
    assert "additional education" in explanations("accountant-auditor")
    assert "licensure" in explanations("mental-health-counselor")
    assert "further education" in explanations("forensic-psychologist")


def test_browse_interface_is_filterable_accessible_and_uses_server_catalog():
    page = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
    assert "Browse all reviewed careers" in page and 'type="search"' in page
    assert 'id="career-browser-count"' in page and 'aria-live="polite"' in page
    assert "renderCareerBrowser" in js and "program_count" in js
    assert '"program_count"' in api


def test_every_new_mapping_uses_an_official_bmcc_or_bmcc_openlab_source():
    new_programs = {"ACCT_AAS", "HMS_AS", "PSY_AA", "PSY_STEM_AA", "CRJ_AA", "PNA_AS", "URB_AA", "POL_AA", "GER_AS"}
    for row in rows("cuny_beyond_program_careers.csv"):
        if row["program_code"] in new_programs:
            assert row["source_url"].startswith(("https://www.bmcc.cuny.edu/", "https://openlab.bmcc.cuny.edu/"))
            assert row["explanation"] and row["reviewed_at"]
