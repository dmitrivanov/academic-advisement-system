import csv
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

from scripts.validate_curriculum_csv import validate_file


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def read_csv(name):
    with (DOCS / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


class EconomicsCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("eco_aa_courses.csv")
        cls.adjustments = [
            row for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "ECO_AA"
        ]
        cls.degree_map = json.loads(
            (DOCS / "bmcc_eco_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "eco_aa_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_catalog_year(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("SSH", row["department_code"])
            self.assertEqual("ECO_AA", row["program_code"])
            self.assertEqual("Economics", row["program_name"])
            self.assertEqual("AA", row["degree_type"])
            self.assertEqual("2025-2026", row["catalog_year"])

    def test_requirement_groups_reconcile_to_sixty_credits(self):
        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(
            {
                "Required Common Core": 12,
                "Flexible Core": 18,
                "Program Requirements": 17,
                "Economics Electives": 9,
                "General Elective": 4,
            },
            group_credits,
        )
        self.assertEqual(60, sum(group_credits.values()))

    def test_core_courses_are_represented_correctly(self):
        by_code = {row["course_code"]: row for row in self.rows}

        self.assertIn("ECO 201", by_code)
        self.assertIn("ECO 202", by_code)
        self.assertEqual("Program Requirements", by_code["ECO 201"]["group_name"])
        self.assertEqual("Program Requirements", by_code["ECO 202"]["group_name"])

        self.assertEqual("MAT 206", by_code["MAT 301"]["prerequisites"])
        self.assertEqual("MAT 206 or MAT 206.5", by_code["MAT 209"]["prerequisites"])
        self.assertEqual("4", by_code["MAT 301"]["credits"])
        self.assertEqual("4", by_code["MAT 209"]["credits"])

    def test_economics_elective_group_is_a_choice_not_mandatory(self):
        elective_rows = [row for row in self.rows if row["group_name"] == "Economics Electives"]
        elective_codes = {row["course_code"] for row in elective_rows}

        self.assertEqual({"9"}, {row["required_credits"] for row in elective_rows})
        self.assertGreater(len(elective_rows), 3, "listed options must exceed the required count")
        self.assertGreater(
            sum(int(row["credits"]) for row in elective_rows),
            9,
            "listed elective credits should exceed required_credits so options are not all mandatory",
        )
        self.assertNotIn("ECO 201", elective_codes)
        self.assertNotIn("ECO 202", elective_codes)
        self.assertEqual(
            {"ECO 215", "ECO 221", "ECO 223", "ECO 225", "ECO 226", "ECO 229",
             "ECO 230", "ECO 235", "ECO 240", "ECO 245", "ECO 250"},
            elective_codes,
        )

    def test_program_specific_pathways_adjustments_match_footnotes(self):
        by_code = {row["derived_group_code"]: row for row in self.adjustments}
        self.assertEqual(
            {"ECO_AA_MATH_QUANT", "ECO_AA_LIFE_PHYSICAL", "ECO_AA_HISTORY"},
            set(by_code),
        )
        self.assertEqual("MAT 206", by_code["ECO_AA_MATH_QUANT"]["include_course_codes"])
        self.assertEqual(
            "AST 110|PHY 110",
            by_code["ECO_AA_LIFE_PHYSICAL"]["include_course_codes"],
        )
        self.assertEqual(
            "HIS|ANT|GEO|PHI|POL|PSY|SOC",
            by_code["ECO_AA_HISTORY"]["include_subject_codes"],
        )

    def test_every_placeholder_has_a_populated_choice_group_reference(self):
        placeholders = [row for row in self.rows if row["course_code"].startswith("ECO-AA-")]
        self.assertTrue(placeholders)
        for row in placeholders:
            self.assertTrue(row["choice_group_code"], row["course_code"])

    def test_no_duplicate_rows(self):
        seen = set()
        for row in self.rows:
            key = (row["group_name"], row["course_code"])
            self.assertNotIn(key, seen, f"duplicate curriculum row: {key}")
            seen.add(key)

    def test_no_malformed_source_urls(self):
        for row in self.rows:
            parsed = urlparse(row["source"])
            self.assertEqual("https", parsed.scheme, row["source"])
            self.assertTrue(parsed.netloc.endswith("bmcc.cuny.edu"), row["source"])
        for row in self.adjustments:
            parsed = urlparse(row["source"])
            self.assertEqual("https", parsed.scheme, row["source"])

    def test_degree_map_has_default_and_alternate_sequences_totaling_sixty(self):
        self.assertEqual(4, self.degree_map["default_semesters"])
        self.assertEqual(60, self.degree_map["total_credits"])

        default_targets = [item["target_credits"] for item in self.degree_map["semesters"]]
        self.assertEqual([13, 16, 16, 15], default_targets)
        self.assertEqual(60, sum(default_targets))

        alternate = self.degree_map["alternate_pathways"][0]["semester_credit_targets"]
        self.assertEqual([10, 13, 12, 12, 13], alternate)
        self.assertEqual(60, sum(alternate))

    def test_both_official_pdfs_are_retained_and_registered(self):
        self.assertEqual(2, len(self.degree_map["source_pdfs"]))
        for filename in (
            "bmcc_economics_2_year_2025_2026.pdf",
            "bmcc_economics_5_semester_2025_2026.pdf",
        ):
            self.assertTrue((DOCS / "degree_maps" / filename).is_file())
            self.assertTrue(
                any(filename in source["url"] for source in self.degree_map["source_pdfs"]),
                f"{filename} is not referenced in source_pdfs",
            )

    def test_progress_page_registers_economics_map_and_source_links(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertIn('ECO_AA: "/docs/bmcc_eco_degree_map_2025_2026.json"', page)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)
        self.assertIn("Official maps", page)


if __name__ == "__main__":
    unittest.main()
