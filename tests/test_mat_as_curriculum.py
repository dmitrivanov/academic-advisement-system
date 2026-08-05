import csv
import json
import unittest
from pathlib import Path

from scripts.validate_curriculum_csv import validate_file


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def read_csv(name):
    with (DOCS / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


class MathematicsCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("mat_as_courses.csv")
        cls.pathways = read_csv("pathways_courses.csv")
        cls.adjustments = read_csv("program_choice_group_adjustments.csv")

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "mat_as_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_published_group_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("MAT", row["department_code"])
            self.assertEqual("MAT_AS", row["program_code"])
            self.assertEqual("Mathematics", row["program_name"])
            self.assertEqual("AS", row["degree_type"])
            self.assertEqual("2025-2026", row["catalog_year"])

        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(60, sum(group_credits.values()))

    def test_calculus_sequence_and_program_electives(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("MAT 206", by_code["MAT 301"]["prerequisites"])
        self.assertEqual("MAT 301", by_code["MAT 302"]["prerequisites"])
        self.assertEqual("MAT 302", by_code["MAT 303"]["prerequisites"])
        self.assertEqual("MAT 302", by_code["MAT 315"]["prerequisites"])

        elective_codes = {
            row["course_code"]
            for row in self.rows
            if row["group_name"] == "Program Electives"
        }
        self.assertEqual(
            {"CSC 210", "CSC 211", "MAT 200", "MAT 209", "MAT 300",
             "MAT 310", "MAT 320", "MAT 501", "MAT 505", "MAT 601"},
            elective_codes,
        )

    def test_shared_pathways_are_complete_and_group_scoped(self):
        expected_groups = {
            "RC_ENGLISH_COMPOSITION", "RC_MATH_QUANT", "RC_LIFE_PHYSICAL",
            "FC_CREATIVE", "FC_INDIVIDUAL", "FC_SCIENTIFIC_WORLD",
            "FC_US_EXPERIENCE", "FC_WORLD_CULTURES",
        }
        actual_groups = {row["group_code"] for row in self.pathways}
        self.assertEqual(expected_groups, actual_groups)
        self.assertGreaterEqual(len(self.pathways), 300)

        memberships = [(row["group_code"], row["course_code"]) for row in self.pathways]
        self.assertEqual(len(memberships), len(set(memberships)))
        self.assertTrue(all(row["source"].startswith("https://www.bmcc.cuny.edu/") for row in self.pathways))

    def test_mathematics_derived_choice_groups(self):
        by_code = {
            row["derived_group_code"]: row
            for row in self.adjustments
            if row["program_code"] == "MAT_AS"
        }
        self.assertEqual(
            {"MAT_AS_CREATIVE", "MAT_AS_LIFE_PHYSICAL", "MAT_AS_SCIENTIFIC_WORLD"},
            set(by_code),
        )
        self.assertEqual("SPE 100|SPE 102", by_code["MAT_AS_CREATIVE"]["exclude_course_codes"])
        self.assertEqual(
            "BIO 210|CHE 201|PHY 210|PHY 215",
            by_code["MAT_AS_LIFE_PHYSICAL"]["include_course_codes"],
        )
        self.assertEqual(
            "BIO 220|CHE 202|CSC 110|CSC 111|PHY 220|PHY 225",
            by_code["MAT_AS_SCIENTIFIC_WORLD"]["include_course_codes"],
        )

    def test_degree_map_contains_four_and_five_semester_paths(self):
        degree_map = json.loads((DOCS / "bmcc_mat_degree_map_2025_2026.json").read_text())
        self.assertEqual(4, degree_map["default_semesters"])
        self.assertEqual([14, 17, 16, 13], [item["target_credits"] for item in degree_map["semesters"]])
        self.assertEqual([10, 13, 14, 14, 9], degree_map["alternate_pathways"][0]["semester_credit_targets"])
        self.assertEqual(60, sum(item["target_credits"] for item in degree_map["semesters"]))


if __name__ == "__main__":
    unittest.main()
