import csv
import unittest
from pathlib import Path

from scripts.validate_curriculum_csv import validate_file


ROOT = Path(__file__).resolve().parents[1]
CURRICULUM_PATH = ROOT / "docs" / "ds_as_courses.csv"


class DataScienceCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CURRICULUM_PATH.open(newline="", encoding="utf-8-sig") as handle:
            cls.rows = list(csv.DictReader(handle))

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(CURRICULUM_PATH, docs_dir=ROOT / "docs")
        self.assertEqual([], result.errors)

    def test_program_identity_and_published_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("MAT", row["department_code"])
            self.assertEqual("DS_AS", row["program_code"])
            self.assertEqual("Data Science", row["program_name"])
            self.assertEqual("AS", row["degree_type"])
            self.assertEqual("2024-2025", row["catalog_year"])

        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(60, sum(group_credits.values()))

    def test_required_courses_electives_and_prerequisites(self):
        rows_by_code = {row["course_code"]: row for row in self.rows}
        expected_required = {"MAT 200", "MAT 301", "MAT 302", "MAT 409", "MAT 415"}
        expected_electives = {"MAT 420", "CSC 203", "CSC 211", "CIS 395", "CIS 490"}

        self.assertTrue(expected_required.issubset(rows_by_code))
        self.assertTrue(expected_electives.issubset(rows_by_code))
        self.assertEqual("MAT 206.5", rows_by_code["MAT 301"]["prerequisites"])
        self.assertEqual("MAT 301", rows_by_code["MAT 302"]["prerequisites"])
        self.assertEqual("MAT 301", rows_by_code["MAT 409"]["prerequisites"])
        self.assertEqual("MAT 301", rows_by_code["MAT 415"]["prerequisites"])
        self.assertEqual("CIS 395", rows_by_code["CIS 490"]["prerequisites"])


if __name__ == "__main__":
    unittest.main()
