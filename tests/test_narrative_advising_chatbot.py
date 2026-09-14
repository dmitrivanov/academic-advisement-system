from pathlib import Path

from narrative_intake import deterministic_narrative_intake


ROOT = Path(__file__).resolve().parents[1]


def test_new_narrative_chatbot_is_primary_and_legacy_is_preserved():
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    root_route = server.split('@app.get("/")', 1)[1].split('@app.get("/progress")', 1)[0]
    legacy_route = server.split('@app.get("/cuny-beyond")', 1)[1].split('@app.get("/advising-chatbot")', 1)[0]
    assert 'FileResponse("frontend/advising_chatbot.html")' in root_route
    assert 'FileResponse("frontend/cuny_beyond.html")' in legacy_route
    assert '@app.get("/advising-chatbot")' in server


def test_narrative_page_uses_one_composer_and_optional_quick_replies():
    html = (ROOT / "frontend/advising_chatbot.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend/advising_chatbot.js").read_text(encoding="utf-8")
    assert 'id="message-input"' in html and 'id="composer"' in html
    assert 'type="radio"' not in html and "choice-grid" not in html
    assert 'id="suggestions"' in html and "data-answer" in js
    assert "/api/advising-chatbot/interpret" in js
    assert "/api/db/cuny-beyond/recommendations" in js
    assert "/api/cuny-beyond/transcript-extract" in js


def test_current_bmcc_pipeline_resolves_major_and_opens_advising_workspace():
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
    chat = (ROOT / "frontend/advising_chatbot.js").read_text(encoding="utf-8")
    workspace = (ROOT / "frontend/current_student_advisor.html").read_text(encoding="utf-8")
    workspace_js = (ROOT / "frontend/current_student_advisor.js").read_text(encoding="utf-8")
    assert "showCurrentProgramCard" in chat and "selectedProgramContext" in chat
    assert "View interactive degree tree" in chat and "View degree-map PDF" in chat
    assert "askConfirmation('workspace')" in chat
    assert '@app.get("/current-student-advisor")' in server
    assert '@app.post("/api/current-student-advisor/ask")' in server
    assert '@router.get("/programs/{program_code}/degree-map-source")' in api
    assert 'class="advisor-panel"' in workspace and 'class="tools-panel"' in workspace
    for label in ("Interactive degree planner", "AI degree / next-semester plan", "Transfer analysis", "Major change", "Interactive degree tree"):
        assert label in workspace_js
    assert "recommended_actions" in server and "recommended-tools" in workspace


def test_deterministic_router_handles_professor_pipeline_examples():
    current = deterministic_narrative_intake(
        "I am a current BMCC student and want to change my major", "identity"
    )
    assert current["student_type"] == "current_bmcc"
    assert current["goal_type"] == "change_major"

    prospective = deterministic_narrative_intake(
        "I am a high school student with no college credits", "identity"
    )
    assert prospective["student_type"] == "high_school"
    assert prospective["has_college_courses"] is False

    transfer = deterministic_narrative_intake(
        "I attend another college and have a transcript", "identity"
    )
    assert transfer["student_type"] == "other_college"
    assert transfer["has_college_courses"] is True
