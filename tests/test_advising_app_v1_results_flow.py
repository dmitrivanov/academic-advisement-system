from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_prospective_results_are_automatic_and_profile_is_folded():
    html = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    assert 'class="student-profile-fold"' in html
    assert "if (submittedPriorLearning) await requestRecommendations();" in js
    assert "if (state.step === steps.length - 1 && !isCurrentStudent()) await requestRecommendations();" in js


def test_enter_submits_and_report_is_available_in_chat_modal():
    html = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    assert "form.addEventListener('keydown'" in js
    assert "event.key !== 'Enter'" in js
    assert 'id="open-ready-report"' in html
    assert "/advising-app_v1/referral?embedded=1" in js


def test_internal_exploration_tools_have_return_paths():
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    transfer = (ROOT / "frontend/transfer_analysis.html").read_text(encoding="utf-8")
    advisor = (ROOT / "frontend/current_student_advisor.html").read_text(encoding="utf-8")
    assert "Save plan and return to chatbot" in planner
    assert "Return to chatbot" in transfer
    assert "Return to chatbot" in advisor


def test_start_over_clears_cross_module_coursework_and_context():
    js = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    for key in (
        "cunyBeyondImportedCoursesV1",
        "cunyBeyondReferralSummaryV1",
        "selectedProgramContext",
        "transferSnapshot",
        "transferDestinationIntentV1",
    ):
        assert f"'{key}'" in js
    assert "writingIntensiveCompleted:" in js


def test_requirements_bundle_choice_groups_to_avoid_n_plus_one_loads():
    api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    assert '"choice_groups": choice_group_payloads' in api
    assert "CURRENT_REQUIREMENTS.choice_groups?.[placeholder.choice_group_code]" in planner


def test_prospective_planner_starts_without_unreported_coursework():
    chatbot = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    planner = (ROOT / "frontend/db_progress_graph.html").read_text(encoding="utf-8")
    assert "studentStatus: isCurrentStudent() ? 'current' : 'prospective'" in chatbot
    assert "sessionStorage.removeItem('cunyBeyondImportedCoursesV1')" in chatbot
    assert 'saved.studentStatus === "prospective" && !saved.hasReportedCoursework' in planner


def test_advisor_workspace_is_compact_and_tools_are_actionable_in_chat():
    html = (ROOT / "frontend/current_student_advisor.html").read_text(encoding="utf-8")
    css = (ROOT / "frontend/current_student_advisor_compact.css").read_text(encoding="utf-8")
    js = (ROOT / "frontend/current_student_advisor.js").read_text(encoding="utf-8")
    assert "current_student_advisor_compact.css" in html
    assert "grid-template-columns: minmax(330px, .68fr) minmax(620px, 1.32fr)" in css
    assert 'data-inline-action' in js
    assert "openTool(button.dataset.inlineAction)" in js
    assert "form.requestSubmit()" in js


def test_degree_tree_renders_in_the_right_workspace_before_expansion():
    js = (ROOT / "frontend/current_student_advisor.js").read_text(encoding="utf-8")
    assert "async function renderTreeInStage" in js
    assert "window.CurriculumGraph.load(program.code,target)" in js
    assert "if(action.id==='tree'){renderTreeInStage(stage);return}" in js
