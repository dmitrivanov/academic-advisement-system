from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_onboarding_uses_chat_window_history_and_quick_choices():
    page = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    css = (ROOT / "frontend/cuny_beyond.css").read_text(encoding="utf-8")
    js = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    assert "chat-window-header" in page and 'id="chat-history"' in page
    assert "CUNY Beyond guide" in page and "Send answer" in page
    assert ".chat-bubble.assistant" in css and ".chat-bubble.user" in css
    assert ".choice-grid label" in css and "border-radius:999px" in css
    assert "renderChatHistory" in js and "CHAT_QUESTIONS" in js
    assert "chatAnswers" in js and "Private browser draft" in page


def test_chat_preserves_free_text_browse_back_restart_and_accessibility():
    page = (ROOT / "frontend/cuny_beyond.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend/cuny_beyond.js").read_text(encoding="utf-8")
    assert 'name="career_goal" type="text"' in page
    assert "Browse all reviewed careers" in page
    assert 'id="back-button"' in page and 'id="restart-button"' in page
    assert 'role="status" aria-live="polite"' in page
    assert "saveDraft()" in js and "loadDraft()" in js
    assert "MAX_SKILLS = 5" in js


def test_module_documentation_package_is_complete_and_route_grounded():
    folder = ROOT / "docs" / "cuny_beyond_module"
    expected = {"README.md", "ACCESS_AND_ROUTES.md", "RUN_LOCAL_MACOS.md", "RUN_LOCAL_WINDOWS.md", "FEATURES.md", "USER_STORIES.md"}
    assert expected <= {path.name for path in folder.glob("*.md")}
    access = (folder / "ACCESS_AND_ROUTES.md").read_text(encoding="utf-8")
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    for route in ("/cuny-beyond", "/cuny-beyond/referral", "/login", "/program-selector", "/db-progress",
                  "/transfer-analysis", "/schedule-handoff", "/admin", "/admin/major-constructor",
                  "/admin/ai-settings", "/admin/schedule-settings", "/admin/cuny-beyond-governance"):
        assert route in access and f'@app.get("{route}")' in server
    assert "username `admin`, password `admin`" in access
    assert "username `tester`, password `tester`" in access


def test_run_guides_include_clean_install_seed_start_and_public_url():
    folder = ROOT / "docs" / "cuny_beyond_module"
    mac = (folder / "RUN_LOCAL_MACOS.md").read_text(encoding="utf-8")
    win = (folder / "RUN_LOCAL_WINDOWS.md").read_text(encoding="utf-8")
    for content in (mac, win):
        assert "git clone https://github.com/dmitrivanov/academic-advisement-system.git" in content
        assert "requirements.txt" in content and "seed_database.py" in content
        assert "faq_fallback_api:app" in content and "127.0.0.1:8000/cuny-beyond" in content
    assert "source venv/bin/activate" in mac
    assert ".\\venv\\Scripts\\Activate.ps1" in win


def test_features_and_user_stories_cover_module_boundaries():
    folder = ROOT / "docs" / "cuny_beyond_module"
    features = (folder / "FEATURES.md").read_text(encoding="utf-8")
    stories = (folder / "USER_STORIES.md").read_text(encoding="utf-8")
    for phrase in ("Conversational onboarding", "Reviewed career matching", "Prior-learning preparation",
                   "Degree-map handoff", "Transfer and schedule support", "Administration and governance"):
        assert phrase in features
    for audience in ("Prospective or high-school student", "Working adult or returning learner", "Transfer student",
                     "Academic or career advisor", "Content administrator", "Tester and maintainer"):
        assert audience in stories
