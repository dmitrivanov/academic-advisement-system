from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = (ROOT / "faq_fallback_api.py").read_text()
PAGE = (ROOT / "frontend/cs_degree_tree_v3.html").read_text()
SCRIPT = (ROOT / "frontend/cs_degree_tree_v3.js").read_text()
STYLE = (ROOT / "frontend/cs_degree_tree_v3.css").read_text()
LOGIN = (ROOT / "frontend/login.html").read_text()


def test_v3_is_a_separate_authenticated_entry_point():
    route = SERVER.split('@app.get("/advising-app_v3")', 1)[1].split('@app.get(', 1)[0]
    assert 'FileResponse("frontend/cs_degree_tree_v3.html")' in route
    assert 'RedirectResponse("/?next=/advising-app_v3"' in route
    assert '"/advising-app_v3"' in LOGIN
    assert '"/advising-app_v3"' in SERVER.split("def safe_login_return_path", 1)[1]


def test_tree_uses_canonical_graph_api_and_limits_program_selector_scope():
    assert "/api/db/programs?selector_only=true" in SCRIPT
    assert "/api/db/programs/${encodeURIComponent(code)}/graph" in SCRIPT
    assert "program.department_code === 'CIS'" in SCRIPT
    assert "program.institution_code === 'BMCC'" in SCRIPT


def test_course_selection_drives_status_and_deterministic_plan():
    assert 'data-course-code' in SCRIPT
    assert "localStorage.setItem(storageKey" in SCRIPT
    assert "function prerequisiteSatisfied" in SCRIPT
    assert "function deterministicPlan" in SCRIPT
    assert "downstreamCount(b.id) - downstreamCount(a.id)" in SCRIPT
    assert "corequisites(node.id)" in SCRIPT


def test_stable_tree_shows_electives_and_dependency_connectors():
    assert "['Foundation','Gateway courses','Advanced sequence','Degree completion']" in SCRIPT
    assert 'Program elective pathways' in SCRIPT
    assert 'class="tree-connectors"' in SCRIPT
    assert "edge.relation_type === 'prerequisite' || edge.relation_type === 'corequisite'" in SCRIPT
    assert ".elective-orbit" in STYLE
    assert ".tree-connectors" in STYLE


def test_page_explains_prototype_boundary():
    assert "central degree-tree design and deterministic sequencing" in PAGE
    assert "Chatbot and report integration come after" in PAGE


def test_page_assets_use_the_frontend_static_mount():
    assert 'href="/frontend/cs_degree_tree_v3.css' in PAGE
    assert 'src="/frontend/cs_degree_tree_v3.js' in PAGE
    assert 'href="/static/' not in PAGE
    assert 'src="/static/' not in PAGE
