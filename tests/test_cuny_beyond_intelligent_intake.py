import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_chat_has_universal_text_ai_and_import_controls():
    page = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    for control in ("profile-free", "career-goal", "employment-free", "skills-free", "cpl-free"):
        assert f'id="{control}"' in page
    assert 'id="ai-assisted"' in page and "checked" in page
    assert 'accept="application/pdf,image/jpeg,image/png"' in page
    assert "transcript-review" in page and "ap-details" in page


def test_branding_is_inside_chat_header_and_old_public_bar_is_removed():
    page = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    assert "chat-header-logo-bmcc" in page and "chat-header-logo-hub" in page
    assert "advisor-avatar" not in page
    assert '<header class="public-header"' not in page
    assert 'href="https://www.bmcc.cuny.edu/"' in page
    assert 'href="https://aichallenge.aitechhub.tech/web/generic/index.php"' in page
    assert page.count('target="_blank" rel="noopener"') >= 2


def test_ap_reference_is_complete_and_source_backed():
    path = ROOT / "docs/bmcc_ap_equivalencies.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 29
    assert {"AP Calculus AB", "AP Biology", "AP Statistics"} <= {row["exam"] for row in rows}
    assert all(row["source_url"].startswith("https://www.bmcc.cuny.edu/") for row in rows)
    assert all(row["score_3"] and row["score_4"] and row["score_5"] for row in rows)


def test_ai_and_transcript_endpoints_have_bounded_public_inputs():
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    assert '@app.post("/api/cuny-beyond/interpret")' in server
    assert '@app.post("/api/cuny-beyond/transcript-extract")' in server
    assert "8 * 1024 * 1024" in server
    assert 'allowed_types = {"application/pdf", "image/jpeg", "image/png"}' in server
    assert "Never infer equivalency or official credit" in server


def test_degree_map_and_import_handoffs_are_wired():
    routes = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
    chat = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    assert 'recommendation["degree_map"]' in routes
    assert "degree-map-preview" in chat
    assert "cunyBeyondImportedCoursesV1" in chat
    assert "applyCunyBeyondImportedCourses" in planner
    assert "isBmccRecord" in planner and "hasPublishedBmccEquivalency" in planner
    assert "openPlannerModal" in chat and "planner-modal-frame" in chat
    assert "AUTO_IMPORTED_COURSES" in planner and "auto-recognized-badge" in planner


def test_embedded_transcript_planner_suppresses_full_app_shell():
    shell = (ROOT / "frontend/app_shell.js").read_text(encoding="utf-8")
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    assert "has('embedded')" in shell
    assert "embedded-transcript" in planner
