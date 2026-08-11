import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


PAGE = Path(__file__).resolve().parents[1] / "frontend" / "db_progress_graph.html"


class IdCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])


class ProgressProspectusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")

    def test_prospectus_controls_and_print_layout_exist(self):
        expected = {
            'id="planProspectusModal"',
            'id="planProspectusDocument"',
            'onclick="printPlanProspectus()"',
            '@media print',
            'body.printing-prospectus',
            '.prospectus-modal.hidden',
            '.prospectus-backdrop.hidden',
        }
        for marker in expected:
            self.assertIn(marker, self.html)

    def test_recommendation_and_degree_plan_open_same_document(self):
        self.assertIn('openPlanProspectus("recommendation")', self.html)
        self.assertIn("openPlanProspectus('degree')", self.html)
        self.assertRegex(
            self.html,
            re.compile(r"async function generateAIStudyPlan\(\).*?openPlanProspectus\(\"degree\"\)", re.DOTALL),
        )

    def test_degree_planner_exposes_direct_pdf_export(self):
        self.assertIn('id="downloadPlanPdfButton"', self.html)
        self.assertIn('onclick="downloadPlanPdf()"', self.html)
        self.assertRegex(
            self.html,
            re.compile(
                r"function downloadPlanPdf\(\).*?openPlanProspectus\(\"degree\"\);"
                r".*?requestAnimationFrame\(printPlanProspectus\)",
                re.DOTALL,
            ),
        )

    def test_ai_commentary_preserves_sanitized_markdown_html(self):
        self.assertIn('class="prospectus-commentary"', self.html)
        self.assertIn('class="advisor-markdown"', self.html)
        self.assertIn('?.innerHTML?.trim()', self.html)
        self.assertNotIn('?.textContent?.trim() || "";', self.html)

    def test_page_has_no_duplicate_html_ids(self):
        parser = IdCollector()
        parser.feed(self.html)
        duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
        self.assertEqual([], duplicates)

    def test_selected_choice_courses_satisfy_prerequisites(self):
        self.assertIn("function hasSelectedChoiceCourse(courseCode)", self.html)
        self.assertIn("completed.has(prereq) || hasSelectedChoiceCourse(prereq)", self.html)

    def test_advisor_drawer_closed_state_is_not_focusable_or_exposed(self):
        self.assertRegex(
            self.html,
            re.compile(
                r'id="advisorDrawer"[^>]*role="dialog"[^>]*aria-modal="true"'
                r'[^>]*aria-labelledby="advisorDrawerTitle"[^>]*aria-hidden="true"[^>]*inert'
            ),
        )
        self.assertRegex(
            self.html,
            re.compile(
                r"function openAdvisorDrawer\(\).*?drawer\.inert = false;"
                r'.*?drawer\.setAttribute\("aria-hidden", "false"\);',
                re.DOTALL,
            ),
        )
        self.assertRegex(
            self.html,
            re.compile(
                r"function closeAdvisorDrawer\(\).*?drawer\.inert = true;"
                r'.*?drawer\.setAttribute\("aria-hidden", "true"\);',
                re.DOTALL,
            ),
        )


if __name__ == "__main__":
    unittest.main()
