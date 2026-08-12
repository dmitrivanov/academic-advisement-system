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


class AccountingCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("acct_aas_courses.csv")
        cls.adjustments = [
            row for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "ACCT_AAS"
        ]

    def test_curriculum_validates_and_totals_sixty(self):
        self.assertEqual([], validate_file(DOCS / "acct_aas_courses.csv", docs_dir=DOCS).errors)
        group_credits = {row["group_name"]: int(row["required_credits"]) for row in self.rows}
        self.assertEqual(60, sum(group_credits.values()))
        self.assertEqual(14, group_credits["Required Common Core"])
        self.assertEqual(6, group_credits["Flexible Core"])

    def test_active_program_identity_is_current(self):
        programs = [row for row in read_csv("programs.csv") if row["program_code"] == "ACCT_AAS"]
        self.assertEqual(1, len(programs))
        self.assertEqual("Accounting", programs[0]["program_name"])
        self.assertEqual("AAS", programs[0]["degree_type"])
        self.assertEqual("2025-2026", programs[0]["catalog_year"])

    def test_common_and_flexible_core_alternatives_are_exact(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("MAT 206", by_code["MAT 150"]["alternatives"])
        self.assertEqual("MAT 150", by_code["MAT 206"]["alternatives"])
        self.assertEqual("PHY 110", by_code["AST 110"]["alternatives"])
        self.assertEqual("AST 110", by_code["PHY 110"]["alternatives"])
        self.assertEqual("SPE 102", by_code["SPE 100"]["alternatives"])

        media = next(row for row in self.adjustments if row["derived_group_code"] == "ACCT_MEDIA_ARTS")
        self.assertEqual("FC_CREATIVE", media["base_group_code"])
        self.assertEqual({"ART", "MUS"}, set(media["include_subject_codes"].split("|")))

    def test_required_accounting_sequence_and_elective_pool(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("ACC 122", by_code["ACC 222"]["prerequisites"])
        self.assertEqual("ACC 222", by_code["ACC 330"]["prerequisites"])
        self.assertEqual("ACC 330", by_code["ACC 430"]["prerequisites"])

        electives = {
            row["course_code"] for row in self.rows
            if row["group_name"] == "Accounting Elective"
        }
        self.assertEqual({"ACC 150", "ACC 242", "ACC 331", "ACC 360", "ACC 370"}, electives)
        self.assertEqual("ACC 222|ACC 241", by_code["ACC 242"]["prerequisites"])

    def test_economics_and_cis_choices_preserve_gating(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("ECO 202", by_code["ECO 201"]["alternatives"])
        self.assertEqual("MAT 206", by_code["ECO 202"]["prerequisites"])
        self.assertEqual("CIS 200", by_code["CIS 100"]["alternatives"])
        self.assertEqual("ACC 122", by_code["CIS 200"]["prerequisites"])

    def test_health_selector_contains_hsd_and_acl_205(self):
        health = next(row for row in self.adjustments if row["derived_group_code"] == "ACCT_HEALTH")
        self.assertEqual("BMCC_GENERAL_ELECTIVE", health["base_group_code"])
        self.assertEqual("ACL 205", health["include_course_codes"])
        self.assertEqual("HSD", health["include_subject_codes"])

    def test_degree_map_and_pdf_are_registered(self):
        degree_map = json.loads((DOCS / "bmcc_accounting_degree_map_2025_2026.json").read_text(encoding="utf-8"))
        self.assertEqual(60, degree_map["total_credits"])
        self.assertEqual([16, 15, 14, 15], [semester["target_credits"] for semester in degree_map["semesters"]])
        self.assertTrue((DOCS / "degree_maps" / "bmcc_accounting_2_year_2025_2026.pdf").is_file())
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertIn('ACCT_AAS: "/docs/bmcc_accounting_degree_map_2025_2026.json"', page)


if __name__ == "__main__":
    unittest.main()
