from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_current_student_branch_has_major_semester_and_three_course_intake_methods():
    html = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    assert 'id="current-major-search"' in html
    assert 'name="semester_standing"' in html
    assert 'id="current-transcript-file"' in html
    assert 'id="manual-course-entry"' in html
    assert 'id="open-completed-selector"' in html
    assert "state.profile === 'working_adult' ? 2 : 3" in js
    assert "/api/cuny-beyond/recognize-courses" in js


def test_completed_course_selector_returns_context_to_chatbot_session():
    chatbot = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    progress = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    assert "advising-completed-courses" in chatbot
    assert "advising-completed-courses" in progress
    assert "cunyBeyondImportedCoursesV1" in chatbot
    assert "transferSnapshot" in chatbot
    assert 'id="open-next-semester-plan"' in (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")


def test_completed_course_intake_is_compact_reviewable_and_saves_from_modal():
    html = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    css = (ROOT / "frontend/cuny_beyond.css").read_text(encoding="utf-8")
    chatbot = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    assert 'class="course-intake-card visual-selector-card"' in html
    assert "comma-separated" in html.lower()
    assert "Review entered courses" in html
    assert "grid-template-columns:repeat(3,minmax(0,1fr))" in css
    assert ".recognized-course-chip" in css
    assert "Approve completed courses" in chatbot
    assert "mode=course-intake&from=structured-chatbot" in chatbot
    assert "advising-completed-courses-saved" in chatbot
    assert "advising-completed-courses-saved" in planner
    assert "Save completed classes and return to chatbot" in planner


def test_manual_course_recognition_is_closed_to_selected_program_catalog():
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    assert '@app.post("/api/cuny-beyond/recognize-courses")' in server
    assert "Use only exact codes from the catalog" in server
    assert "Do not invent equivalencies" in server


def test_current_student_results_route_to_full_advising_tools_and_report():
    html = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    advisor = (ROOT / "frontend/current_student_advisor.js").read_text(encoding="utf-8")
    transfer = (ROOT / "frontend/transfer_analysis.html").read_text(encoding="utf-8")
    for element_id in ("open-next-semester-plan", "open-major-change", "open-general-advising", "open-transfer-analysis", "prepare-current-summary"):
        assert f'id="{element_id}"' in html
    assert "/current-student-advisor?tool=" in js
    assert "'/db-progress?mode=ai-plan&from=structured-chatbot'" in js
    assert "/transfer-analysis?mode=major-change" in js
    assert "transferDestinationIntentV1" in js and "transferDestinationIntentV1" in transfer
    assert "cunyBeyondReferralSummaryV1" in js
    assert "requestedTool" in advisor


def test_current_student_actions_are_compact_and_direct_plan_returns_with_saved_artifacts():
    html = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    css = (ROOT / "frontend/cuny_beyond.css").read_text(encoding="utf-8")
    js = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    for element_id in ("open-next-semester-plan", "open-major-change", "show-transfer-options", "open-general-advising"):
        assert f'id="{element_id}"' in html
    assert ".advising-goal-grid{display:flex" in css
    assert "flex:1 1 0" in css
    assert "@media (max-width:980px) { .advising-goal-grid" not in css
    assert 'id="transfer-intent-card"' in html and 'aria-expanded="false"' in html
    assert 'id="generate-ai-plan-here"' in html
    assert 'class="advising-goal-card primary plan-goal-card"' in html
    assert "Destination campus" in html and "Destination major" in html
    assert "cuny_beyond.css?v=20261026-3" in html and "cuny_beyond.js?v=20261026-3" in html
    assert "autogenerate=1&from=structured-chatbot" in js
    assert "advising-degree-plan-saved" in js and "advising-degree-plan-saved" in planner
    assert "generateAIStudyPlan()" in planner
    assert "...existing" in js
    assert "returnedTool" in js and "state.step = steps.length - 1" in js


def test_modern_language_curricula_and_spanish_teacher_mapping_are_seedable():
    for filename, code in (
        ("frn_aa_courses.csv", "FRN_AA"),
        ("ita_aa_courses.csv", "ITA_AA"),
        ("spa_aa_courses.csv", "SPA_AA"),
        ("sti_aa_courses.csv", "STI_AA"),
    ):
        content = (ROOT / "docs" / filename).read_text(encoding="utf-8")
        assert code in content
        assert "Required Common Core" in content and "Flexible Core" in content
        assert "Program Electives" in content and "General Electives" in content
    careers = (ROOT / "docs/cuny_beyond_careers.csv").read_text(encoding="utf-8")
    mappings = (ROOT / "docs/cuny_beyond_program_careers.csv").read_text(encoding="utf-8")
    assert "spanish-teacher,Spanish Teacher" in careers
    assert "BMCC,SPA_AA,spanish-teacher,50,strong" in mappings


def test_current_student_referral_keeps_program_semester_goal_and_completed_courses():
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    referral = (ROOT / "frontend/cuny_beyond_referral.html").read_text(encoding="utf-8")
    assert '"current_program"' in server
    assert '"semester"' in server and '"advising_goal"' in server
    assert "Current major" in referral and "Advising goal" in referral
    assert "Save summary PDF" in referral and "Save academic plan PDF" in referral and "Last 4 ID digits" in referral


def test_degree_planner_can_save_artifacts_and_return_to_structured_chatbot():
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    chatbot = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    referral = (ROOT / "frontend/cuny_beyond_referral.html").read_text(encoding="utf-8")
    assert 'id="chatbotReturnBar"' in planner
    assert "savePlannerArtifactsForChatbot" in planner
    assert "returnToStructuredChatbot" in planner
    assert 'window.location.href = "/advising-app_v1?returned=degree-plan"' in planner
    assert "cunyBeyondAnonymousDraftV1" in planner
    assert "cunyBeyondReferralSummaryV1" in planner
    assert "LAST_DEGREE_PLAN" in planner and "ai_explanation" in planner
    assert 'id="saved-degree-plan"' in (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    assert "Academic plan document is ready" in chatbot
    assert "Academic and Next-Semester Plan" in referral


def test_embedded_ai_plan_has_generation_state_and_separate_final_documents():
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    chatbot = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    referral = (ROOT / "frontend/cuny_beyond_referral.html").read_text(encoding="utf-8")
    assert 'id="embeddedPlanLoading"' in planner
    assert "Preparing your academic plan" in planner
    assert "showEmbeddedPlanLoading" in planner
    assert "hideEmbeddedPlanLoading" in planner
    assert "academic_plan_document" in planner
    assert "academic_plan_document" in chatbot
    assert 'id="advising-summary-document"' in referral
    assert 'id="academic-plan-document"' in referral
    assert "Save summary PDF" in referral
    assert "Save academic plan PDF" in referral


def test_ai_plan_explanation_is_normalized_into_professional_markdown_sections():
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    referral = (ROOT / "frontend/cuny_beyond_referral.html").read_text(encoding="utf-8")
    assert "normalizeAdvisorNarrative" in planner
    assert "## Next Semester" in planner
    assert "### Course recommendations" in planner
    assert ".prospectus-commentary .advisor-markdown" in planner
    assert ".advisor-markdown li" in planner
    assert "normalizePlanNarrative" in referral
    assert 'class="commentary-intro"' in referral


def test_final_advising_package_uses_compact_notice_and_document_tabs():
    referral = (ROOT / "frontend/cuny_beyond_referral.html").read_text(encoding="utf-8")
    assert '<header class="public-header">' not in referral
    assert 'class="package-notice"' in referral
    assert 'class="document-tabs"' in referral
    assert 'id="summary-document-tab"' in referral
    assert 'id="academic-document-tab"' in referral
    assert "Two documents, one advising session" not in referral
    assert "The academic-plan document appears" not in referral
    assert "activateDocument" in referral


def test_saved_academic_plan_renders_markdown_without_raw_markers():
    referral = (ROOT / "frontend/cuny_beyond_referral.html").read_text(encoding="utf-8")
    assert "renderPlanMarkdown" in referral
    assert "inlinePlanMarkdown" in referral
    assert "plan-markdown-section" in referral
    assert "replace(/#{2,6}/g" in referral
    assert "break-inside:avoid" in referral
    assert "@media print" in referral and ".ai-commentary" in referral


def test_embedded_degree_progress_removes_redundant_program_panel():
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    assert ".embedded-transcript .program-card { display:none!important; }" in planner


def test_workspace_chat_handles_structured_api_errors_and_bounded_context():
    advisor = (ROOT / "frontend/current_student_advisor.js").read_text(encoding="utf-8")
    assert "function apiErrorMessage" in advisor
    assert "Array.isArray(detail)" in advisor
    assert "function compactConversationSummary" in advisor
    assert ".slice(0,2400)" in advisor
    assert "new Error(apiErrorMessage(data))" in advisor


def test_advising_workspace_does_not_render_duplicate_selected_program_panel():
    html = (ROOT / "frontend/current_student_advisor.html").read_text(encoding="utf-8")
    advisor = (ROOT / "frontend/current_student_advisor.js").read_text(encoding="utf-8")
    assert 'class="selected-program compact"' not in html
    assert "getElementById('program-name')" not in advisor
    assert "getElementById('program-meta')" not in advisor
    assert "getElementById('degree-map-link')" not in advisor
