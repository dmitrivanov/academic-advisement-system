import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CcnyTransferEquivalencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "docs/course_equivalencies.csv").open(newline="", encoding="utf-8-sig") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_official_bmcc_ccny_cs_rules_are_present(self):
        mappings = {
            (row["source_course_code"], row["target_course_code"]): row
            for row in self.rows
            if row["source_institution_code"] == "BMCC" and row["target_institution_code"] == "CCNY"
        }
        expected = {
            ("ENG 101", "ENGL 11000"),
            ("CSC 111 + CSC 211", "CSC 10300"),
            ("CSC 215", "CSC 21100"),
            ("CSC 231", "CSC 10400"),
            ("CSC 331", "CSC 21200"),
            ("MAT 301", "MATH 20100"),
            ("MAT 302", "MATH 21200"),
            ("PHY 215", "PHYS 20700"),
        }
        self.assertTrue(expected.issubset(mappings))
        self.assertTrue(all(mappings[key]["status"] == "approved" for key in expected))
        self.assertTrue(all(mappings[key]["source_reference"].startswith("https://explorer.cuny.edu/") for key in expected))

    def test_intro_programming_equivalency_requires_both_bmcc_courses(self):
        rule = next(row for row in self.rows if row["target_course_code"] == "CSC 10300")
        self.assertEqual("combination", rule["equivalency_type"])
        self.assertEqual("CSC 111 + CSC 211", rule["source_course_code"])

    def test_transfer_ui_consumes_every_source_in_a_combination(self):
        source = (ROOT / "frontend/transfer_analysis.html").read_text(encoding="utf-8")
        self.assertIn("function equivalencySourceCodes(rule)", source)
        self.assertIn("equivalencySourceCodes(rule).every(code => completedCodes.has(code))", source)
        self.assertIn("matchedSourceCodes.forEach(code => usedSourceCourses.add(code))", source)

    def test_admin_api_accepts_but_validates_combination_rules(self):
        source = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
        self.assertIn('{"direct", "combination"}', source)
        self.assertIn("A combination equivalency requires at least two source courses", source)


if __name__ == "__main__":
    unittest.main()
