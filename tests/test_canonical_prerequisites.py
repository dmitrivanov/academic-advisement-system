import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class CanonicalPrerequisiteTests(unittest.TestCase):
    def test_verified_campus_wide_rules_are_declared_once(self):
        with (DOCS / "course_prerequisites.csv").open(newline="", encoding="utf-8-sig") as handle:
            rows = {row["course_code"]: row for row in csv.DictReader(handle)}

        self.assertEqual("CSC 110 or CSC 111 or CIS 165", rows["CIS 316"]["prerequisites"])
        self.assertEqual("MAT 157 or MAT 157.5", rows["MAT 206"]["prerequisites"])
        self.assertEqual("MAT 206 or MAT 206.5", rows["MAT 301"]["prerequisites"])
        self.assertEqual("CSC 111", rows["CSC 211"]["prerequisites"])
        self.assertEqual("CIS 440|CIS 345", rows["CIS 459"]["prerequisites"])

    def test_cis_program_electives_include_verified_prerequisites(self):
        with (DOCS / "cis_courses.csv").open(newline="", encoding="utf-8-sig") as handle:
            rows = {row["course_code"]: row for row in csv.DictReader(handle)}
        expected = {
            "CIS 272": "CSC 101",
            "CIS 285": "CSC 101",
            "CIS 359": "CSC 110 or CSC 111 or CIS 165",
            "CIS 362": "CSC 110 or CSC 111 or CIS 165",
            "CIS 364": "CSC 210",
            "CIS 459": "CIS 440|CIS 345",
            "CIS 490": "CIS 395",
        }
        self.assertEqual(expected, {code: rows[code]["prerequisites"] for code in expected})

    def test_legacy_cis_and_cnt_no_longer_omit_cis_316_rule(self):
        for filename in ("cis_courses.csv", "cnt_courses.csv"):
            with (DOCS / filename).open(newline="", encoding="utf-8-sig") as handle:
                row = next(row for row in csv.DictReader(handle) if row["course_code"] == "CIS 316")
            self.assertEqual("CSC 110 or CSC 111 or CIS 165", row["prerequisites"], filename)

    def test_seed_applies_canonical_rules_after_all_programs_and_choice_groups(self):
        source = (ROOT / "seed_database.py").read_text(encoding="utf-8")
        self.assertIn("def seed_canonical_course_prerequisites", source)
        self.assertGreater(
            source.rindex("seed_canonical_course_prerequisites(db)"),
            source.rindex("seed_program_choice_group_adjustments(db)"),
        )
        canonical = source[source.index("def seed_canonical_course_prerequisites"):source.index("def seed_ccny_elective_groups")]
        self.assertIn("explicit_or_existing", canonical)
        self.assertIn("if explicit_or_existing:", canonical)
        self.assertNotIn(".delete(", canonical)

    def test_prerequisite_support_courses_are_cataloged_and_exposed_without_degree_credit(self):
        with (DOCS / "course_catalog.csv").open(newline="", encoding="utf-8-sig") as handle:
            rows = {row["course_code"]: row for row in csv.DictReader(handle)}
        self.assertEqual("4", rows["MAT 157"]["credits"])
        self.assertEqual("4", rows["MAT 157.5"]["credits"])

        api = (ROOT / "api_db_routes.py").read_text(encoding="utf-8")
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertIn('"prerequisite_support_courses": prerequisite_support_courses', api)
        self.assertIn("ChoiceGroupCourse.choice_group_id.in_", api)
        self.assertIn("function attachPrerequisiteSupportGroup", page)
        self.assertIn("excluded_from_degree: true", page)
        self.assertIn("if (group.excluded_from_degree) return total", page)


if __name__ == "__main__":
    unittest.main()
