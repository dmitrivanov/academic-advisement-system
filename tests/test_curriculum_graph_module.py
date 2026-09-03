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
        self.assertIn("Degree Map Tree", progress)
        self.assertIn("CurriculumGraph.open", progress)
        self.assertIn("data-open-graph", chatbot)
        self.assertIn("/admin/curriculum-graph", dashboard)
        self.assertIn('@app.get("/admin/curriculum-graph")', server)

    def test_degree_trees_live_on_planner_and_matched_cards_without_global_browser(self):
        page = (ROOT / "frontend" / "cuny_beyond.html").read_text(encoding="utf-8")
        progress = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertIn('curriculum_graph.js', page)
        self.assertNotIn('degree-tree-browser-button', page)
        self.assertIn('id="dependencyGraphButton"', progress)
        self.assertIn("isSupported(program.code)", progress)

    def test_group_branches_are_compact_sequenced_and_course_cards_expand(self):
        component = (ROOT / "frontend" / "curriculum_graph.js").read_text(encoding="utf-8")
        styles = (ROOT / "frontend" / "curriculum_graph.css").read_text(encoding="utf-8")
        self.assertIn('<details class="curriculum-group-tree', component)
        self.assertIn('function layeredSubset', component)
        self.assertIn("const startOpen = false", component)
        self.assertIn("cluster.type === 'elective_choice'", component)
        self.assertIn("cluster.display_node_ids || cluster.node_ids", component)
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

    def test_degree_tree_constructor_imports_csv_and_supports_dragged_relationships(self):
        editor = (ROOT / "frontend" / "curriculum_graph_admin.html").read_text(encoding="utf-8")
        self.assertIn("Degree Tree Constructor", editor)
        self.assertIn('id="graphCsv"', editor)
        self.assertIn("source_course,target_course,relation_type,group_id,note", editor)
        self.assertIn("function parseCsv", editor)
        self.assertIn("function previewCsv", editor)
        self.assertIn('class="drag-course" draggable="true"', editor)
        self.assertIn("Save imported relationships", editor)


if __name__ == "__main__":
    unittest.main()
