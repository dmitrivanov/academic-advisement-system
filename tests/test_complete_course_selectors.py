import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class CompleteCourseSelectorTests(unittest.TestCase):
    def test_every_bmcc_placeholder_has_a_choice_group(self):
        missing = []
        for path in sorted(DOCS.glob("*_courses.csv")):
            with path.open(newline="", encoding="utf-8-sig") as handle:
                for row_number, row in enumerate(csv.DictReader(handle), start=2):
                    if row.get("institution_code") != "BMCC":
                        continue
                    code = row.get("course_code", "")
                    if "-" in code and not row.get("choice_group_code"):
                        missing.append(f"{path.name}:{row_number} {code}")
        self.assertEqual([], missing)

    def test_broad_elective_groups_are_declared(self):
        with (DOCS / "pathways_groups.csv").open(newline="", encoding="utf-8-sig") as handle:
            codes = {row["group_code"] for row in csv.DictReader(handle)}
        self.assertTrue({
            "BMCC_GENERAL_ELECTIVE",
            "BMCC_LIBERAL_ARTS_ELECTIVE",
            "BMCC_MODERN_LANGUAGE_CONTINUATION",
        }.issubset(codes))

    def test_selector_supports_multiple_courses_and_credit_targets(self):
        source = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertIn("function selectedChoiceCourses", source)
        self.assertIn("function selectedChoiceCredits", source)
        self.assertIn("Choose approved courses totaling", source)
        self.assertIn("Math.min(selectedChoiceCredits(code)", source)

    def test_seed_populates_institutional_elective_groups_after_majors(self):
        source = (ROOT / "seed_database.py").read_text(encoding="utf-8")
        self.assertIn("def seed_institutional_elective_groups", source)
        self.assertLess(source.index("for major in major_files:"), source.rindex("seed_institutional_elective_groups(db)"))


if __name__ == "__main__":
    unittest.main()
