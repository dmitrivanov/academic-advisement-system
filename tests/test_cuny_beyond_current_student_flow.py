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
    assert "/transfer-analysis?mode=major-change" in js
    assert "transferDestinationIntentV1" in js and "transferDestinationIntentV1" in transfer
    assert "cunyBeyondReferralSummaryV1" in js
    assert "requestedTool" in advisor


def test_current_student_referral_keeps_program_semester_goal_and_completed_courses():
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    referral = (ROOT / "frontend/cuny_beyond_referral.html").read_text(encoding="utf-8")
    assert '"current_program"' in server
    assert '"semester"' in server and '"advising_goal"' in server
    assert "Current major" in referral and "Advising goal" in referral
    assert "Save / Print PDF" in referral and "Last 4 ID digits" in referral
