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


class CriminalJusticeCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("crj_aa_courses.csv")
        cls.adjustments = [
            row for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "CRJ_AA"
        ]
        cls.pathways_groups = read_csv("pathways_groups.csv")
        cls.pathways_courses = read_csv("pathways_courses.csv")
        cls.degree_map = json.loads(
            (DOCS / "bmcc_crj_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "crj_aa_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_sixty_credit_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("CRJ", row["department_code"])
            self.assertEqual("CRJ_AA", row["program_code"])
            self.assertEqual("Criminal Justice", row["program_name"])
            self.assertEqual("AA", row["degree_type"])
            self.assertEqual("2025-2026", row["catalog_year"])

        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(60, sum(group_credits.values()))

    def test_common_and_flexible_core_totals(self):
        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(12, group_credits["Required Common Core"])
        self.assertEqual(18, group_credits["Flexible Core"])
        self.assertEqual(27, group_credits["Program Requirements"])
        self.assertEqual(3, group_credits["General Elective"])

    def test_all_crj_program_courses_are_present_and_required(self):
        by_code = {row["course_code"]: row for row in self.rows}
        for code in ("CRJ 101", "CRJ 102", "CRJ 200", "CRJ 201", "CRJ 202", "CRJ 204"):
            self.assertIn(code, by_code)
            self.assertEqual("Program Requirements", by_code[code]["group_name"])
            self.assertEqual("3", by_code[code]["credits"])

    def test_crj_204_prerequisite_and_title(self):
        by_code = {row["course_code"]: row for row in self.rows}
        crj_204 = by_code["CRJ 204"]
        # Both degree map PDFs and the official course-listings page agree:
        # CRJ 101 AND CRJ 102 (not CRJ 200 -- an early image-based misread
        # was corrected against the actual PDF text before encoding this).
        self.assertEqual("CRJ 101|CRJ 102", crj_204["prerequisites"])
        # The course-listings page, not the degree map's wording, is the
        # source of truth for official titles (lesson 2).
        self.assertEqual("Criminal Justice and the Urban Community", crj_204["title"])

    def test_crj_102_and_crj_200_prerequisites(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("SOC 100", by_code["CRJ 102"]["prerequisites"])
        self.assertEqual("POL 100", by_code["CRJ 200"]["prerequisites"])
        # CRJ 201 and CRJ 202 both require CRJ 101 specifically, per the
        # course-listings page -- not the map's looser "all 200-level CRJ
        # courses" footnote (CRJ 200's actual prerequisite is POL 100).
        self.assertEqual("CRJ 101", by_code["CRJ 201"]["prerequisites"])
        self.assertEqual("CRJ 101", by_code["CRJ 202"]["prerequisites"])

    def test_math_quant_selector_includes_both_map_variants(self):
        by_code = {row["course_code"]: row for row in self.rows}
        statistics = by_code["CRJ-AA-MATH"]
        self.assertEqual("Required Common Core", statistics["group_name"])
        self.assertEqual("4", statistics["credits"])
        self.assertEqual("CRJ_AA_MATH_QUANT", statistics["choice_group_code"])

        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "CRJ_AA_MATH_QUANT")
        self.assertEqual("RC_MATH_QUANT", adjustment["base_group_code"])
        self.assertEqual({"MAT 150", "MAT 150.5"}, set(adjustment["include_course_codes"].split("|")))

    def test_english_or_forensic_linguistics_selector_is_complete(self):
        by_code = {row["course_code"]: row for row in self.rows}
        selector = by_code["CRJ-AA-ENGLISH"]
        self.assertEqual("Program Requirements", selector["group_name"])
        self.assertEqual("CRJ_AA_ENGLISH_OR_LIN", selector["choice_group_code"])

        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "CRJ_AA_ENGLISH_OR_LIN")
        choices = set(adjustment["include_course_codes"].split("|"))
        self.assertIn("LIN 250", choices)
        self.assertIn("ENG 300", choices)
        self.assertIn("ENG 395", choices)
        self.assertTrue(all(code == "LIN 250" or code.startswith("ENG 3") for code in choices))

    def test_creative_expression_second_course_excludes_speech_courses(self):
        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "CRJ_AA_CREATIVE")
        self.assertEqual("FC_CREATIVE", adjustment["base_group_code"])
        self.assertEqual("SPE 100|SPE 102", adjustment["exclude_course_codes"])

    def test_modern_language_selector_reuses_established_continuation_list(self):
        by_code = {row["course_code"]: row for row in self.rows}
        modlang_row = by_code["CRJ-AA-MODLANG"]
        self.assertEqual("Program Requirements", modlang_row["group_name"])
        self.assertEqual("CRJ_AA_MODERN_LANGUAGE", modlang_row["choice_group_code"])

        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "CRJ_AA_MODERN_LANGUAGE")
        self.assertEqual("FC_WORLD_CULTURES", adjustment["base_group_code"])

        # Reuses the identical, already-reviewed continuation-course list
        # already established for WAL_AA / WAL_JRN_AA, not a re-derived one.
        wal_adjustment = next(
            row for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "WAL_AA" and row["derived_group_code"] == "WAL_MODERN_LANGUAGE"
        )
        self.assertEqual(
            set(wal_adjustment["include_course_codes"].split("|")),
            set(adjustment["include_course_codes"].split("|")),
        )

    def test_general_elective_selector_is_populated_and_requires_three_credits(self):
        rows = [row for row in self.rows if row["group_name"] == "General Elective"]
        self.assertEqual(1, len(rows))
        self.assertEqual("3", rows[0]["required_credits"])
        self.assertEqual("3", rows[0]["credits"])
        self.assertEqual("BMCC_GENERAL_ELECTIVE", rows[0]["choice_group_code"])

        group_codes = {row["group_code"] for row in self.pathways_groups}
        self.assertIn("BMCC_GENERAL_ELECTIVE", group_codes)

    def test_every_referenced_choice_group_exists_and_has_selectable_courses(self):
        base_group_codes = {row["group_code"] for row in self.pathways_groups}
        derived_group_codes = {row["derived_group_code"] for row in self.adjustments}
        all_known_group_codes = base_group_codes | derived_group_codes

        referenced = {row["choice_group_code"] for row in self.rows if row["choice_group_code"]}
        for code in referenced:
            self.assertIn(code, all_known_group_codes, f"{code} is not defined anywhere")

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

    def test_degree_map_has_default_and_alternate_sequences_totaling_sixty(self):
        self.assertEqual(4, self.degree_map["default_semesters"])
        self.assertEqual(60, self.degree_map["total_credits"])

        default_targets = [item["target_credits"] for item in self.degree_map["semesters"]]
        self.assertEqual([16, 15, 15, 14], default_targets)
        self.assertEqual(60, sum(default_targets))

        alternate = self.degree_map["alternate_pathways"][0]["semester_credit_targets"]
        self.assertEqual([10, 12, 12, 12, 14], alternate)
        self.assertEqual(60, sum(alternate))

    def test_both_official_pdfs_are_retained_and_registered(self):
        self.assertEqual(2, len(self.degree_map["source_pdfs"]))
        for filename in (
            "bmcc_criminal_justice_2_year_2025_2026.pdf",
            "bmcc_criminal_justice_5_semester_2025_2026.pdf",
        ):
            self.assertTrue((DOCS / "degree_maps" / filename).is_file())
            self.assertTrue(
                any(filename in source["url"] for source in self.degree_map["source_pdfs"]),
                f"{filename} is not referenced in source_pdfs",
            )

    def test_progress_page_registers_crj_map_exactly_once(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        occurrences = page.count('CRJ_AA: "/docs/bmcc_crj_degree_map_2025_2026.json"')
        self.assertEqual(1, occurrences)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)


if __name__ == "__main__":
    unittest.main()
