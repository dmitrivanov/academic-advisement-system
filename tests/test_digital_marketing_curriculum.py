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


class DigitalMarketingCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("dmk_as_courses.csv")
        cls.adjustments = [
            row for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "DMK_AS"
        ]
        cls.degree_map = json.loads(
            (DOCS / "bmcc_dmk_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "dmk_as_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_sixty_credit_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("BUS", row["department_code"])
            self.assertEqual("DMK_AS", row["program_code"])
            self.assertEqual("Digital Marketing", row["program_name"])
            self.assertEqual("AS", row["degree_type"])
            self.assertEqual("2025-2026", row["catalog_year"])

        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(60, sum(group_credits.values()))

    def test_group_totals(self):
        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(12, group_credits["Required Common Core"])
        self.assertEqual(18, group_credits["Flexible Core"])
        self.assertEqual(15, group_credits["Program Requirements"])
        self.assertEqual(9, group_credits["Program Elective"])
        self.assertEqual(6, group_credits["General Elective"])

    def test_speech_alternatives_are_visible_and_reciprocal(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertIn("SPE 102", by_code)
        self.assertEqual("SPE 102", by_code["SPE 100"]["alternatives"])
        self.assertEqual("SPE 100", by_code["SPE 102"]["alternatives"])

    def test_creative_expression_second_course_excludes_speech_courses(self):
        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "DMK_AS_CREATIVE")
        self.assertEqual("FC_CREATIVE", adjustment["base_group_code"])
        self.assertEqual("SPE 100|SPE 102", adjustment["exclude_course_codes"])

    def test_mar_330_mixed_and_or_prerequisite_is_exactly_encoded(self):
        by_code = {row["course_code"]: row for row in self.rows}
        # Official text: "ENG 101 and MAT 150 and [MAR 100 or PSY 100]".
        # The `|` separator creates top-level AND groups; each group may
        # independently contain an ` or ` OR-list, so this mixed
        # AND/OR expression is exactly representable, not an approximation.
        self.assertEqual(
            "ENG 101|MAT 150|MAR 100 or PSY 100",
            by_code["MAR 330"]["prerequisites"],
        )
        self.assertEqual("MAR 330", by_code["MAR 340"]["prerequisites"])

    def test_mar_elective_prerequisites(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("MAR 100", by_code["MAR 210"]["prerequisites"])
        self.assertEqual("ENG 101|MAR 100", by_code["MAR 220"]["prerequisites"])
        self.assertEqual("ENG 101|MAR 100", by_code["MAR 230"]["prerequisites"])

    def test_com_245_course_prerequisite_is_enforced(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("SPE 100", by_code["COM 245"]["prerequisites"])

    def test_program_elective_pool_is_choose_three_of_seven(self):
        rows = [row for row in self.rows if row["group_name"] == "Program Elective"]
        codes = {row["course_code"] for row in rows}
        self.assertEqual(
            {"MAR 210", "MAR 220", "MAR 230", "BUS 150", "CIS 200", "COM 245", "MMP 240"},
            codes,
        )
        self.assertEqual({"3"}, {row["credits"] for row in rows})

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

    def test_both_official_pdfs_are_retained_and_registered(self):
        self.assertEqual(2, len(self.degree_map["source_pdfs"]))
        for filename in (
            "bmcc_digital_marketing_2_year_2025_2026.pdf",
            "bmcc_digital_marketing_5_semester_2025_2026.pdf",
        ):
            self.assertTrue((DOCS / "degree_maps" / filename).is_file())
            self.assertTrue(
                any(filename in source["url"] for source in self.degree_map["source_pdfs"]),
                f"{filename} is not referenced in source_pdfs",
            )

    def test_degree_map_sequences_total_sixty_credits(self):
        self.assertEqual(60, self.degree_map["total_credits"])
        default_targets = [item["target_credits"] for item in self.degree_map["semesters"]]
        self.assertEqual(60, sum(default_targets))
        alternate = self.degree_map["alternate_pathways"][0]["semester_credit_targets"]
        self.assertEqual(60, sum(alternate))

    def test_progress_page_registers_dmk_map_exactly_once(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        occurrences = page.count('DMK_AS: "/docs/bmcc_dmk_degree_map_2025_2026.json"')
        self.assertEqual(1, occurrences)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)


if __name__ == "__main__":
    unittest.main()
