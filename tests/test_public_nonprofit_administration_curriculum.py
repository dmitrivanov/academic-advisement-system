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


class PublicNonprofitAdministrationCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("pna_as_courses.csv")
        cls.adjustments = {
            row["derived_group_code"]: row
            for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "PNA_AS"
        }
        cls.degree_map = json.loads(
            (DOCS / "bmcc_pna_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_validates_and_reconciles_to_sixty(self):
        self.assertEqual([], validate_file(DOCS / "pna_as_courses.csv", docs_dir=DOCS).errors)
        credits = {row["group_name"]: int(row["required_credits"]) for row in self.rows}
        self.assertEqual(
            {
                "Required Common Core": 12,
                "Flexible Core": 18,
                "Curriculum Requirements": 15,
                "Program Electives": 9,
                "General Electives": 6,
            },
            credits,
        )
        self.assertEqual(60, sum(credits.values()))

    def test_program_identity_is_single_and_uses_map_year(self):
        programs = [row for row in read_csv("programs.csv") if row["program_code"] == "PNA_AS"]
        self.assertEqual(1, len(programs))
        self.assertEqual("2025-2026", programs[0]["catalog_year"])
        self.assertTrue(all(row["catalog_year"] == "2025-2026" for row in self.rows))

    def test_named_curriculum_courses_are_program_requirements(self):
        required = [row for row in self.rows if row["group_name"] == "Curriculum Requirements"]
        self.assertEqual({"program_required"}, {row["group_type"] for row in required})
        self.assertEqual(
            {"BUS 104", "BUS 110", "CIS 100", "PAN 100", "PAN 230"},
            {row["course_code"] for row in required},
        )
        self.assertEqual("PAN 100", next(row for row in required if row["course_code"] == "PAN 230")["prerequisites"])

    def test_program_elective_pool_is_exact_and_machine_counted(self):
        adjustment = self.adjustments["PNA_AS_PROGRAM_ELECTIVES"]
        self.assertEqual("9", adjustment["required_credits"])
        self.assertEqual("3", adjustment["required_course_count"])
        self.assertEqual(
            {"BUS 150", "BUS 200", "ECO 225", "MAR 100", "PAN 240", "PAN 250"},
            set(adjustment["include_course_codes"].split("|")),
        )

    def test_footnotes_are_translated_into_adjustments(self):
        self.assertEqual(
            {"PNA_AS_MATH_QUANT", "PNA_AS_CREATIVE", "PNA_AS_PROGRAM_ELECTIVES", "PNA_AS_GENERAL_ELECTIVE"},
            set(self.adjustments),
        )
        self.assertEqual("MAT 150|MAT 206", self.adjustments["PNA_AS_MATH_QUANT"]["include_course_codes"])
        self.assertEqual("SPE 100|SPE 102", self.adjustments["PNA_AS_CREATIVE"]["exclude_course_codes"])
        self.assertIn("STEM excess", self.adjustments["PNA_AS_GENERAL_ELECTIVE"]["notes"])

    def test_every_placeholder_has_a_populated_base_or_derived_group(self):
        base_codes = {row["group_code"] for row in read_csv("pathways_groups.csv")}
        derived_codes = set(self.adjustments)
        for row in self.rows:
            if row["course_code"].startswith("PNA-AS-"):
                self.assertTrue(row["choice_group_code"])
                self.assertIn(row["choice_group_code"], base_codes | derived_codes)

    def test_degree_map_and_pdf_are_registered(self):
        self.assertEqual(60, self.degree_map["total_credits"])
        self.assertEqual([16, 15, 15, 14], [item["target_credits"] for item in self.degree_map["semesters"]])
        self.assertTrue((DOCS / "degree_maps" / "bmcc_public_nonprofit_administration_2_year_2025_2026.pdf").is_file())
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertEqual(1, page.count('PNA_AS: "/docs/bmcc_pna_degree_map_2025_2026.json"'))


if __name__ == "__main__":
    unittest.main()
