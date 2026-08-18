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


class AnimationMotionGraphicsCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("amg_as_courses.csv")
        cls.adjustments = [
            row for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "AMG_AS"
        ]
        cls.degree_map = json.loads(
            (DOCS / "bmcc_amg_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "amg_as_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_sixty_credit_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("MMA", row["department_code"])
            self.assertEqual("AMG_AS", row["program_code"])
            self.assertEqual("Animation and Motion Graphics", row["program_name"])
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
        self.assertEqual(13, group_credits["Required Common Core"])
        self.assertEqual(9, group_credits["Flexible Core"])
        self.assertEqual(38, group_credits["Program Requirements"])

    def test_speech_and_internship_alternatives_are_reciprocal(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("SPE 102", by_code["SPE 100"]["alternatives"])
        self.assertEqual("SPE 100", by_code["SPE 102"]["alternatives"])
        self.assertEqual("MEA 201", by_code["MEA 371"]["alternatives"])
        self.assertEqual("MEA 371", by_code["MEA 201"]["alternatives"])
        self.assertEqual("ANI 360", by_code["ANI 402"]["alternatives"])
        self.assertEqual("ANI 402", by_code["ANI 360"]["alternatives"])

    def test_ani_360_has_its_own_distinct_prerequisite(self):
        # Unlike SPE 100/SPE 102 or MEA 371/MEA 201, ANI 360 is an
        # alternative to ANI 402 but has a genuinely different
        # prerequisite chain of its own.
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("MMP 260 or ANI 260", by_code["ANI 360"]["prerequisites"])
        self.assertEqual("ANI 401|MMP 250", by_code["ANI 402"]["prerequisites"])

    def test_creative_expression_second_course_excludes_three_courses(self):
        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "AMG_AS_CREATIVE")
        self.assertEqual("FC_CREATIVE", adjustment["base_group_code"])
        self.assertEqual("SPE 100|SPE 102|MES 153", adjustment["exclude_course_codes"])

    def test_ani_301_uses_official_course_listing_title_not_map_error(self):
        by_code = {row["course_code"]: row for row in self.rows}
        ani_301 = by_code["ANI 301"]
        # The degree map mislabels this course as "Introduction to Video
        # Graphics" (actually VAT 301/MMP 301's title); the verified
        # official course-listings title is used instead.
        self.assertEqual("Introduction to Motion Graphics and Visual Effects", ani_301["title"])
        self.assertEqual("VAT 161 or VAT 171 or MMA 100 or MMP 100", ani_301["prerequisites"])

    def test_ani_301_matches_vat_as_encoding_for_the_shared_course(self):
        # vat_as_courses.csv only exists once VAT_AS is merged upstream;
        # skip gracefully rather than fail on a cross-branch dependency.
        vat_path = DOCS / "vat_as_courses.csv"
        if not vat_path.is_file():
            self.skipTest("vat_as_courses.csv not present on this branch")
        vat_rows = read_csv("vat_as_courses.csv")
        vat_by_code = {row["course_code"]: row for row in vat_rows}
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual(vat_by_code["ANI 301"]["title"], by_code["ANI 301"]["title"])
        self.assertEqual(vat_by_code["ANI 301"]["prerequisites"], by_code["ANI 301"]["prerequisites"])

    def test_ani_260_and_ani_401_use_catalog_or_not_map_and(self):
        by_code = {row["course_code"]: row for row in self.rows}
        # The catalog's OR was used over the map footnote's AND, and
        # matches ANI 401's existing encoding in vat_as_courses.csv.
        self.assertEqual("MMP 100 or MMA 100", by_code["ANI 260"]["prerequisites"])
        self.assertEqual("MMP 100 or MMA 100", by_code["ANI 401"]["prerequisites"])

    def test_art_176_is_not_guessed_at(self):
        codes = {row["course_code"] for row in self.rows}
        self.assertNotIn("ART 176", codes)

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
            "bmcc_ani_2_year_2025_2026.pdf",
            "bmcc_ani_5_semester_2025_2026.pdf",
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

    def test_progress_page_registers_amg_map_exactly_once(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        occurrences = page.count('AMG_AS: "/docs/bmcc_amg_degree_map_2025_2026.json"')
        self.assertEqual(1, occurrences)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)


if __name__ == "__main__":
    unittest.main()
