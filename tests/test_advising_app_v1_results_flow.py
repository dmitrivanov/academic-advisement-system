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
