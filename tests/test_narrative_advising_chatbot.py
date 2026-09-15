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
    assert "state.goal_type === 'general' ? 'workspace' : 'route'" in chat
    assert '@app.get("/current-student-advisor")' in server
    assert '@app.post("/api/current-student-advisor/ask")' in server
    assert '@router.get("/programs/{program_code}/degree-map-source")' in api
    assert 'class="advisor-panel"' in workspace and 'class="tools-panel"' in workspace
    for label in ("Degree progress", "Next semester", "Transfer analysis", "Major change", "Interactive degree tree"):
        assert label in workspace_js
    assert "recommended_actions" in server and "recommended-tools" in workspace


def test_college_students_supply_institution_major_goal_and_courses_before_routing():
    chat = (ROOT / "frontend/advising_chatbot.js").read_text(encoding="utf-8")
    assert "state.stage = 'institution'" in chat
    assert "What major or degree are you pursuing" in chat
    assert "askGoal()" in chat and "askCompletedCourses()" in chat
    assert "List courses in chat" in (ROOT / "frontend/advising_chatbot.html").read_text(encoding="utf-8")
    assert "Select manually" in (ROOT / "frontend/advising_chatbot.html").read_text(encoding="utf-8")
    assert "course_list" in chat and "narrative-${recognitionSource}-import" in chat
    assert "cunyBeyondImportedCoursesV1" in chat and "resolveTypedCourses" in chat
    assert "is not currently loaded in our curriculum database" in chat
    assert 'href="/login"' not in chat


def test_typed_courses_use_same_colored_import_path_as_transcript_courses():
    chat = (ROOT / "frontend/advising_chatbot.js").read_text(encoding="utf-8")
    progress = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    assert "persistImportedCourses(selected, 'transcript')" in chat
    assert "persistImportedCourses(state.transcript_courses, 'chat-entered')" in chat
    assert "AUTO_IMPORTED_COURSE_LABELS" in progress
    assert "Entered in chatbot — review this selection" in progress
    assert "DIRECT_COMPLETED_COURSES.add(code)" in progress
    assert "form.hidden = false" in chat.split("function showTranscript()", 1)[1].split("async function analyzeTranscript", 1)[0]


def test_matched_program_actions_share_consistent_layout():
    css = (ROOT / "frontend/advising_chatbot_current.css").read_text(encoding="utf-8")
    assert ".current-program-card .recommendation-actions a" in css
    assert "grid-template-columns: repeat(3" in css
    assert "background: #174ea6" in css and "text-decoration: none" in css


def test_login_is_archived_for_render_and_new_tools_use_open_routes():
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    workspace = (ROOT / "frontend/current_student_advisor.js").read_text(encoding="utf-8")
    shell = (ROOT / "frontend/app_shell.js").read_text(encoding="utf-8")
    for route in ("/program-selector", "/db-progress", "/transfer-analysis", "/schedule-handoff", "/careers"):
        section = server.split(f'@app.get("{route}")', 1)[1].split('@app.get(', 1)[0]
        assert 'RedirectResponse("/login"' not in section
    assert 'href="/login"' not in (ROOT / "frontend/advising_chatbot.js").read_text(encoding="utf-8")
    assert 'href="/logout"' not in shell
    assert "'/db-progress?embedded=workspace'" in workspace and "'/transfer-analysis?embedded=workspace'" in workspace


def test_advising_workspace_embeds_tools_and_shares_active_mode_with_ai():
    html = (ROOT / "frontend/current_student_advisor.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend/current_student_advisor.js").read_text(encoding="utf-8")
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    assert 'class="tool-tabs"' in html and 'id="tool-frame"' in html
    assert 'id="expand-tool"' in html and 'id="tool-modal"' in html
    assert "active_tool:{...activeAction" in js and "is active" in js
    assert "active_tool: Dict[str, Any]" in server and '"active_tool": {' in server


def test_primary_intake_restores_grouped_identity_and_ap_selectors():
    html = (ROOT / "frontend/advising_chatbot.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend/advising_chatbot.js").read_text(encoding="utf-8")
    legacy = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    assert "setIdentitySuggestions" in js and "New students" in js and "Current students" in js
    assert 'class="ap-selector"' in html and "/api/db/cuny-beyond/ap-equivalencies" in js
    assert "Returning BMCC student" not in js and "Returning BMCC student" not in legacy


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
