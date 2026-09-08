from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_downloadable_launchers_are_present_and_secret_free():
    mac = ROOT / "launchers" / "AI_Academic_Advisement_Mac.command"
    windows = ROOT / "launchers" / "AI_Academic_Advisement_Windows.cmd"
    assert mac.is_file() and windows.is_file()
    for content in (mac.read_text(encoding="utf-8"), windows.read_text(encoding="utf-8")):
        assert "git clone" in content
        assert "pull --ff-only" in content
        assert "advising2_0" in content
        assert "requirements.txt" in content
        assert "seed_database.py" in content
        assert "faq_fallback_api:app" in content
        assert "GEMINI_API_KEY" in content
        assert "PASTE_THE_GEMINI" not in content


def test_launcher_download_routes_and_page_links_are_exposed():
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    page = (ROOT / "frontend" / "cuny_beyond.html").read_text(encoding="utf-8")
    dashboard = (ROOT / "frontend" / "admin_dashboard.html").read_text(encoding="utf-8")
    assert '@app.get("/downloads/macos-launcher")' in server
    assert '@app.get("/downloads/windows-launcher")' in server
    assert 'def download_macos_launcher(_admin=Depends(require_admin))' in server
    assert 'def download_windows_launcher(_admin=Depends(require_admin))' in server
    assert 'href="/downloads/macos-launcher"' not in page
    assert 'href="/downloads/windows-launcher"' not in page
    assert 'href="/downloads/macos-launcher"' in dashboard
    assert 'href="/downloads/windows-launcher"' in dashboard
    assert (ROOT / "frontend" / "downloads" / "AI_Academic_Advisement_Mac.zip").is_file()
    assert (ROOT / "frontend" / "downloads" / "AI_Academic_Advisement_Windows.zip").is_file()


def test_dotenv_is_loaded_before_local_application_imports():
    server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
    assert "from dotenv import load_dotenv" in server
    assert server.index("load_dotenv()") < server.index("from auth import")
