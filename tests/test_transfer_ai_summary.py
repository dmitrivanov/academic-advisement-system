from pathlib import Path


HTML_PATH = Path(__file__).resolve().parents[1] / "frontend" / "transfer_analysis.html"


def test_ai_summary_retries_transient_network_failures_with_timeout():
    html = HTML_PATH.read_text(encoding="utf-8")

    assert "const AI_SUMMARY_TIMEOUT_MS = 90000;" in html
    assert "async function requestAISummary(payload, maxAttempts = 2)" in html
    assert "error instanceof TypeError" in html
    assert "responseError.retryable = response.status >= 500;" in html
    assert "controller.abort()" in html


def test_major_change_uses_major_change_ai_identity_and_prompt():
    html = HTML_PATH.read_text(encoding="utf-8")

    assert 'agent_id: isMajorChange ? "major_change_analysis" : "transfer_analysis"' in html
    assert 'page_name: isMajorChange ? "Major Change Analysis" : "Transfer Analysis"' in html
    assert "Explain this major change analysis to the student." in html
    assert "planning estimate rather than an official degree audit" in html
