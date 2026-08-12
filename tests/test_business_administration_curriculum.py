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


class BusinessAdministrationCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("bba_as_courses.csv")
        cls.adjustments = [
            row for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "BBA_AS"
        ]
        cls.degree_map = json.loads(
            (DOCS / "bmcc_business_administration_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_validates_and_reconciles_to_sixty(self):
        self.assertEqual([], validate_file(DOCS / "bba_as_courses.csv", docs_dir=DOCS).errors)
        group_credits = {row["group_name"]: int(row["required_credits"]) for row in self.rows}
        self.assertEqual(
            {
                "Required Common Core": 12,
                "Flexible Core": 18,
                "Curriculum Requirements": 26,
                "Business Elective": 3,
                "Liberal Arts Elective": 1,
            },
            group_credits,
        )
        self.assertEqual(60, sum(group_credits.values()))

    def test_program_identity_uses_map_catalog_year(self):
        programs = [row for row in read_csv("programs.csv") if row["program_code"] == "BBA_AS"]
        self.assertEqual(1, len(programs))
        self.assertEqual("Business Administration", programs[0]["program_name"])
        self.assertEqual("AS", programs[0]["degree_type"])
        self.assertEqual("2025-2026", programs[0]["catalog_year"])
        self.assertTrue(all(row["catalog_year"] == "2025-2026" for row in self.rows))

    def test_named_curriculum_courses_are_program_requirements(self):
        required = [row for row in self.rows if row["group_name"] == "Curriculum Requirements"]
        self.assertEqual({"program_required"}, {row["group_type"] for row in required})
        self.assertEqual(
            {"ACC 122", "BUS 104", "BUS 110", "BUS 150", "CIS 200", "MAR 100", "MAT 209", "MAT 301", "BUS 320"},
            {row["course_code"] for row in required},
        )

    def test_calculus_and_analytics_are_reciprocal_alternatives(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("BUS 320", by_code["MAT 301"]["alternatives"])
        self.assertEqual("MAT 301", by_code["BUS 320"]["alternatives"])
        self.assertEqual("MAT 206 or MAT 206.5", by_code["MAT 301"]["prerequisites"])
        self.assertEqual("MAT 209", by_code["BUS 320"]["prerequisites"])

    def test_required_course_prerequisites_are_preserved(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("ENG 101|ENG 201|BUS 104", by_code["BUS 150"]["prerequisites"])
        self.assertEqual("ACC 122 or BUS 104", by_code["CIS 200"]["prerequisites"])
        self.assertEqual("MAT 206 or MAT 206.5", by_code["MAT 209"]["prerequisites"])

    def test_business_elective_pool_matches_footnote(self):
        electives = [row for row in self.rows if row["group_name"] == "Business Elective"]
        self.assertEqual({"program_elective"}, {row["group_type"] for row in electives})
        self.assertEqual({"3"}, {row["required_credits"] for row in electives})
        self.assertEqual(
            {"ACC 222", "BUS 200", "BUS 201", "BUS 225", "FNB 100", "SBE 100"},
            {row["course_code"] for row in electives},
        )

    def test_core_adjustments_translate_every_program_footnote(self):
        by_code = {row["derived_group_code"]: row for row in self.adjustments}
        self.assertEqual(
            {"BBA_AS_MATH_QUANT", "BBA_AS_LIFE_PHYSICAL", "BBA_AS_CREATIVE", "BBA_AS_SCIENTIFIC_WORLD"},
            set(by_code),
        )
        self.assertEqual("RC_MATH_QUANT", by_code["BBA_AS_MATH_QUANT"]["base_group_code"])
        self.assertEqual("", by_code["BBA_AS_MATH_QUANT"]["include_course_codes"])
        self.assertIn("recommended", by_code["BBA_AS_MATH_QUANT"]["notes"].lower())
        self.assertEqual("SPE 100|SPE 102", by_code["BBA_AS_CREATIVE"]["exclude_course_codes"])
        self.assertIn("stem variant", by_code["BBA_AS_LIFE_PHYSICAL"]["notes"].lower())
        self.assertIn("stem variant", by_code["BBA_AS_SCIENTIFIC_WORLD"]["notes"].lower())

    def test_all_placeholders_reference_defined_groups(self):
        base_codes = {row["group_code"] for row in read_csv("pathways_groups.csv")}
        derived_codes = {row["derived_group_code"] for row in self.adjustments}
        placeholders = [row for row in self.rows if "-" in row["course_code"]]
        self.assertTrue(placeholders)
        for row in placeholders:
            self.assertTrue(row["choice_group_code"], row["course_code"])
            self.assertIn(row["choice_group_code"], base_codes | derived_codes)

    def test_stem_excess_and_cross_group_limit_are_documented(self):
        sources = (DOCS / "bba_as_sources.md").read_text(encoding="utf-8")
        self.assertIn("Automatic cross-group surplus-credit application is not", sources)
        self.assertIn("cannot enforce a subject-count cap across groups", sources)

    def test_degree_map_pdf_and_progress_registration(self):
        self.assertEqual(60, self.degree_map["total_credits"])
        self.assertEqual([13, 16, 16, 15], [item["target_credits"] for item in self.degree_map["semesters"]])
        self.assertTrue((DOCS / "degree_maps" / "bmcc_business_administration_2_year_2025_2026.pdf").is_file())
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertEqual(
            1,
            page.count('BBA_AS: "/docs/bmcc_business_administration_degree_map_2025_2026.json"'),
        )


if __name__ == "__main__":
    unittest.main()
