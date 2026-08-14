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


class VideoArtsTechnologyCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("vat_as_courses.csv")
        cls.degree_map = json.loads(
            (DOCS / "bmcc_vat_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "vat_as_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_sixty_credit_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("MMA", row["department_code"])
            self.assertEqual("VAT_AS", row["program_code"])
            self.assertEqual("Video Arts and Technology", row["program_name"])
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
        self.assertEqual(6, group_credits["Flexible Core"])
        self.assertEqual(18, group_credits["Program Requirements"])
        self.assertEqual(12, group_credits["VAT Production Courses"])
        self.assertEqual(3, group_credits["VAT Advised Elective"])
        self.assertEqual(3, group_credits["VAT Program Elective"])
        self.assertEqual(2, group_credits["Media Arts and Technology Internship"])
        self.assertEqual(4, group_credits["General Elective"])

    def test_vat_production_course_pool_is_choose_four_of_six(self):
        rows = [row for row in self.rows if row["group_name"] == "VAT Production Courses"]
        codes = {row["course_code"] for row in rows}
        self.assertEqual(
            {"VAT 161", "VAT 165", "VAT 171", "VAT 261", "VAT 265", "VAT 271"},
            codes,
        )
        self.assertEqual({"3"}, {row["credits"] for row in rows})

    def test_vat_production_course_prerequisites(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("VAT 100|MES 153", by_code["VAT 161"]["prerequisites"])
        self.assertEqual("VAT 100|MES 153", by_code["VAT 165"]["prerequisites"])
        self.assertEqual("VAT 100|MES 153", by_code["VAT 171"]["prerequisites"])
        self.assertEqual("VAT 161", by_code["VAT 261"]["prerequisites"])
        self.assertEqual("VAT 165|MMP 100", by_code["VAT 265"]["prerequisites"])
        self.assertEqual("VAT 171", by_code["VAT 271"]["prerequisites"])

    def test_speech_and_internship_alternatives_are_reciprocal(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("SPE 102", by_code["SPE 100"]["alternatives"])
        self.assertEqual("SPE 100", by_code["SPE 102"]["alternatives"])
        self.assertEqual("MEA 201", by_code["MEA 371"]["alternatives"])
        self.assertEqual("MEA 371", by_code["MEA 201"]["alternatives"])
        self.assertEqual(by_code["MEA 371"]["credits"], by_code["MEA 201"]["credits"])

    def test_vat_100_uses_official_course_listing_title(self):
        by_code = {row["course_code"]: row for row in self.rows}
        # The degree maps print "Introduction to Video Arts and Technology",
        # but the official course-listings page's title is used instead
        # (lesson 2: match the official course listing, not the map).
        self.assertEqual("Introduction to Video Technology", by_code["VAT 100"]["title"])

    def test_vat_301_and_ani_301_are_both_present_as_distinct_courses(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertIn("VAT 301", by_code)
        self.assertIn("ANI 301", by_code)
        self.assertNotEqual(by_code["VAT 301"]["title"], by_code["ANI 301"]["title"])
        # VAT 301's real AND-of-OR prerequisite can't be represented in the
        # flat grammar and must not be guessed at.
        self.assertEqual("", by_code["VAT 301"]["prerequisites"])

    def test_unverified_courses_are_not_guessed_at(self):
        codes = {row["course_code"] for row in self.rows}
        # Officially eligible per the degree map footnotes, but their
        # titles/credits could not be independently verified -- must not
        # appear as fabricated rows (see vat_as_sources.md).
        for code in ("COM 245", "HED 250", "MUS 225", "THE 110", "VAT 300", "VAT 306"):
            self.assertNotIn(code, codes)

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
            "bmcc_vat_2_year_2025_2026.pdf",
            "bmcc_vat_3_year_2025_2026.pdf",
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

    def test_progress_page_registers_vat_map_exactly_once(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        occurrences = page.count('VAT_AS: "/docs/bmcc_vat_degree_map_2025_2026.json"')
        self.assertEqual(1, occurrences)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)


if __name__ == "__main__":
    unittest.main()
