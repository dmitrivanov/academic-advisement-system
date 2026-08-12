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


class FinancialManagementCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("fmg_as_courses.csv")
        cls.adjustments = [
            row for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "FMG_AS"
        ]
        cls.degree_map = json.loads(
            (DOCS / "bmcc_financial_management_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_validates_and_reconciles_to_sixty(self):
        self.assertEqual([], validate_file(DOCS / "fmg_as_courses.csv", docs_dir=DOCS).errors)
        group_credits = {row["group_name"]: int(row["required_credits"]) for row in self.rows}
        self.assertEqual(
            {
                "Required Common Core": 12,
                "Flexible Core": 18,
                "Curriculum Requirements": 25,
                "General Elective": 5,
            },
            group_credits,
        )
        self.assertEqual(60, sum(group_credits.values()))

    def test_program_identity_uses_supplied_map_catalog_year(self):
        programs = [row for row in read_csv("programs.csv") if row["program_code"] == "FMG_AS"]
        self.assertEqual(1, len(programs))
        self.assertEqual("Financial Management", programs[0]["program_name"])
        self.assertEqual("AS", programs[0]["degree_type"])
        self.assertEqual("2025-2026", programs[0]["catalog_year"])
        self.assertTrue(all(row["catalog_year"] == "2025-2026" for row in self.rows))

    def test_named_curriculum_courses_are_program_requirements(self):
        required = [row for row in self.rows if row["group_name"] == "Curriculum Requirements"]
        self.assertEqual({"program_required"}, {row["group_type"] for row in required})
        self.assertEqual(
            {"ACC 122", "BUS 104", "BUS 110", "FNB 100", "FNB 230", "FNB 250", "FNB 300", "MAT 301"},
            {row["course_code"] for row in required},
        )

    def test_prerequisites_and_money_banking_equivalency_are_preserved(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("FNB 100|ACC 122", by_code["FNB 230"]["prerequisites"])
        self.assertEqual("FNB 100|ACC 122", by_code["FNB 300"]["prerequisites"])
        self.assertEqual("FNB 100 or ECO 100 or ECO 201 or ECO 202", by_code["FNB 250"]["prerequisites"])
        self.assertEqual("ECO 250", by_code["FNB 250"]["alternatives"])
        self.assertEqual("MAT 206 or MAT 206.5", by_code["MAT 301"]["prerequisites"])

    def test_general_elective_is_a_complete_program_elective_selector(self):
        elective = [row for row in self.rows if row["group_name"] == "General Elective"]
        self.assertEqual(1, len(elective))
        self.assertEqual("program_elective", elective[0]["group_type"])
        self.assertEqual("5", elective[0]["credits"])
        self.assertEqual("FMG_AS_GENERAL_ELECTIVE", elective[0]["choice_group_code"])

    def test_adjustments_translate_the_program_footnotes(self):
        by_code = {row["derived_group_code"]: row for row in self.adjustments}
        self.assertEqual(
            {
                "FMG_AS_MATH_QUANT",
                "FMG_AS_CREATIVE",
                "FMG_AS_INDIVIDUAL",
                "FMG_AS_US_EXPERIENCE",
                "FMG_AS_GENERAL_ELECTIVE",
            },
            set(by_code),
        )
        self.assertIn("MAT 206", by_code["FMG_AS_MATH_QUANT"]["notes"])
        self.assertEqual("SPE 100|SPE 102", by_code["FMG_AS_CREATIVE"]["exclude_course_codes"])
        self.assertIn("ECO 202", by_code["FMG_AS_INDIVIDUAL"]["notes"])
        self.assertIn("ECO 201", by_code["FMG_AS_US_EXPERIENCE"]["notes"])
        self.assertIn("STEM excess", by_code["FMG_AS_GENERAL_ELECTIVE"]["notes"])
        self.assertIn("MAT 209", by_code["FMG_AS_GENERAL_ELECTIVE"]["notes"])

    def test_every_placeholder_references_a_defined_group(self):
        base_codes = {row["group_code"] for row in read_csv("pathways_groups.csv")}
        derived_codes = {row["derived_group_code"] for row in self.adjustments}
        placeholders = [row for row in self.rows if "-" in row["course_code"]]
        self.assertTrue(placeholders)
        for row in placeholders:
            self.assertTrue(row["choice_group_code"], row["course_code"])
            self.assertIn(row["choice_group_code"], base_codes | derived_codes)

    def test_degree_map_pdf_and_progress_registration(self):
        self.assertEqual(60, self.degree_map["total_credits"])
        self.assertEqual([13, 16, 15, 16], [item["target_credits"] for item in self.degree_map["semesters"]])
        self.assertTrue((DOCS / "degree_maps" / "bmcc_financial_management_2_year_2025_2026.pdf").is_file())
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertEqual(
            1,
            page.count('FMG_AS: "/docs/bmcc_financial_management_degree_map_2025_2026.json"'),
        )


if __name__ == "__main__":
    unittest.main()
