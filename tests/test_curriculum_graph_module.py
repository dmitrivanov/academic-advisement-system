import unittest
from pathlib import Path

from curriculum_graph_service import _layers


ROOT = Path(__file__).resolve().parents[1]


class CurriculumGraphModuleTests(unittest.TestCase):
    def test_graph_scope_is_every_populated_program(self):
        service = (ROOT / "curriculum_graph_service.py").read_text(encoding="utf-8")
        api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
        self.assertIn("def is_graph_program", service)
        self.assertNotIn("CS_GRAPH_PROGRAM_CODES", service)
        self.assertNotIn("CS_GRAPH_PROGRAM_CODES", api)

    def test_dependency_layers_and_cycle_reporting_are_deterministic(self):
        edges = [
            {"source_id": 1, "target_id": 2, "relation_type": "prerequisite"},
            {"source_id": 2, "target_id": 3, "relation_type": "prerequisite"},
            {"source_id": 4, "target_id": 3, "relation_type": "recommended"},
        ]
        layers, cycles = _layers({1, 2, 3, 4}, edges)
        self.assertEqual([[1, 4], [2], [3]], layers)
        self.assertEqual([], cycles)

        cyclic, cycle_nodes = _layers(
            {1, 2},
            [
                {"source_id": 1, "target_id": 2, "relation_type": "prerequisite"},
                {"source_id": 2, "target_id": 1, "relation_type": "prerequisite"},
            ],
        )
        self.assertEqual([[1, 2]], cyclic)
        self.assertEqual([1, 2], cycle_nodes)

    def test_student_and_admin_surfaces_use_reusable_component(self):
        progress = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        chatbot = (ROOT / "frontend" / "cuny_beyond.js").read_text(encoding="utf-8")
        dashboard = (ROOT / "frontend" / "admin_dashboard.html").read_text(encoding="utf-8")
        server = (ROOT / "faq_fallback_api.py").read_text(encoding="utf-8")
        self.assertIn("Dependency Map", progress)
        self.assertIn("CurriculumGraph.open", progress)
        self.assertIn("data-open-graph", chatbot)
        self.assertIn("/admin/curriculum-graph", dashboard)
        self.assertIn('@app.get("/admin/curriculum-graph")', server)

    def test_public_fallback_page_can_browse_every_populated_degree_tree(self):
        page = (ROOT / "frontend" / "cuny_beyond.html").read_text(encoding="utf-8")
        client = (ROOT / "frontend" / "cuny_beyond.js").read_text(encoding="utf-8")
        api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
        self.assertIn('id="degree-tree-browser-button"', page)
        self.assertIn('id="degree-tree-browser"', page)
        self.assertIn("/api/db/programs/graphs", client)
        self.assertIn("data-browse-graph", client)
        self.assertIn('@router.get("/programs/graphs")', api)
        self.assertIn("_curriculum_graph_program_list", api)

    def test_group_branches_are_compact_sequenced_and_course_cards_expand(self):
        component = (ROOT / "frontend" / "curriculum_graph.js").read_text(encoding="utf-8")
        styles = (ROOT / "frontend" / "curriculum_graph.css").read_text(encoding="utf-8")
        self.assertIn('<details class="curriculum-group-tree', component)
        self.assertIn('function layeredSubset', component)
        self.assertIn("const startOpen = hasSequence", component)
        self.assertIn('aria-expanded="false"', component)
        self.assertIn("card.classList.toggle('expanded'", component)
        self.assertIn('.curriculum-group-card', styles)
        self.assertIn('.curriculum-node.expanded .node-details', styles)

    def test_graph_redraws_after_resizing_and_highlights_downstream_path(self):
        component = (ROOT / "frontend" / "curriculum_graph.js").read_text(encoding="utf-8")
        styles = (ROOT / "frontend" / "curriculum_graph.css").read_text(encoding="utf-8")
        self.assertIn('new ResizeObserver(scheduleDrawEdges)', component)
        self.assertIn("setTimeout(() => requestAnimationFrame(drawEdges), 180)", component)
        self.assertIn('function downstreamPath', component)
        self.assertIn("path.setAttribute('stroke-width', '5')", component)
        self.assertIn('.curriculum-node.path-destination', styles)
        self.assertIn("#16a34a", component)

    def test_choice_groups_pdf_or_logic_and_cs_math_entry_are_exposed(self):
        component = (ROOT / "frontend" / "curriculum_graph.js").read_text(encoding="utf-8")
        progress = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        service = (ROOT / "curriculum_graph_service.py").read_text(encoding="utf-8")
        self.assertIn("Download / save PDF", component)
        self.assertIn("window.print()", component)
        self.assertIn("onGroupOpen", component)
        self.assertIn("openChoiceModal(placeholderCode)", progress)
        self.assertIn('"logic"] =', service)
        self.assertIn('["MAT 206"] if program.code == "CS"', service)

    def test_admin_changes_are_stored_as_overrides_not_canonical_rows(self):
        models = (ROOT / "models.py").read_text(encoding="utf-8")
        api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
        self.assertIn('class CurriculumGraphEdgeOverride', models)
        self.assertIn('action = Column(String', models)
        self.assertIn('CurriculumGraphEdgeOverride(', api)
        self.assertNotIn('db.add(CoursePrerequisite(', api.split('@router.put("/admin/curriculum-graphs/', 1)[1])


if __name__ == "__main__":
    unittest.main()
