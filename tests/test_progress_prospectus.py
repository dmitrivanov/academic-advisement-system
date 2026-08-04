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

    def test_page_has_no_duplicate_html_ids(self):
        parser = IdCollector()
        parser.feed(self.html)
        duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
        self.assertEqual([], duplicates)


if __name__ == "__main__":
    unittest.main()
