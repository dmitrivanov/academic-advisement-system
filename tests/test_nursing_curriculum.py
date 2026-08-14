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


class NursingCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("nur_aas_courses.csv")
        cls.degree_map = json.loads(
            (DOCS / "bmcc_nur_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "nur_aas_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_sixty_five_credit_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("NUR", row["department_code"])
            self.assertEqual("NUR_AAS", row["program_code"])
            self.assertEqual("Nursing", row["program_name"])
            self.assertEqual("AAS", row["degree_type"])
            self.assertEqual("2025-2026", row["catalog_year"])

        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(65, sum(group_credits.values()))

    def test_group_totals(self):
        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(13, group_credits["Required Common Core"])
        self.assertEqual(10, group_credits["Flexible Core"])
        self.assertEqual(42, group_credits["Curriculum Requirements"])

    def test_no_elective_choice_groups(self):
        # Unlike the BMCC A.A. majors already in this system, Nursing is a
        # fully-prescribed AAS curriculum with no elective placeholders.
        for row in self.rows:
            self.assertEqual("", row["choice_group_code"], row["course_code"])
            self.assertNotEqual("program_elective", row["group_type"], row["course_code"])

    def test_speech_alternatives_are_visible_and_reciprocal(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertIn("SPE 102", by_code)
        self.assertEqual("SPE 102", by_code["SPE 100"]["alternatives"])
        self.assertEqual("SPE 100", by_code["SPE 102"]["alternatives"])
        self.assertEqual("Flexible Core", by_code["SPE 100"]["group_name"])
        self.assertEqual("Flexible Core", by_code["SPE 102"]["group_name"])

    def test_chemistry_biology_prerequisite_chain_is_machine_enforced(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("CHE 121", by_code["BIO 425"]["prerequisites"])
        self.assertEqual("BIO 425", by_code["BIO 426"]["prerequisites"])
        self.assertEqual("BIO 426", by_code["BIO 420"]["prerequisites"])

    def test_nursing_process_sequence_is_machine_enforced(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual(
            "CHE 121|ENG 101|BIO 425|MAT 104|PSY 100",
            by_code["NUR 112"]["prerequisites"],
        )
        self.assertEqual("NUR 112|BIO 426", by_code["NUR 211"]["prerequisites"])
        self.assertEqual("NUR 211", by_code["NUR 313"]["prerequisites"])
        self.assertEqual("NUR 313", by_code["NUR 411"]["prerequisites"])
        self.assertEqual("NUR 313", by_code["NUR 415"]["prerequisites"])

    def test_nur_211_does_not_reference_psy_240(self):
        # The official course-listings page additionally lists PSY 240 as a
        # prerequisite for NUR 211, but PSY 240 is not part of this
        # curriculum or any of the three official degree maps -- it must
        # not be guessed at (see nur_aas_sources.md "Prerequisite review").
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertNotIn("PSY 240", by_code["NUR 211"]["prerequisites"])
        codes = {row["course_code"] for row in self.rows}
        self.assertNotIn("PSY 240", codes)

    def test_evening_weekend_track_addition_is_documented_as_unenforced(self):
        sources_text = (DOCS / "nur_aas_sources.md").read_text(encoding="utf-8")
        self.assertIn("evening/weekend students must complete BIO 426 and BIO 420", sources_text)
        self.assertIn("not enforced", sources_text)

        by_code = {row["course_code"]: row for row in self.rows}
        # The universal (Day-track) minimum only, not the stricter
        # Evening/Weekend-track superset -- confirms the "knowingly
        # stricter substitution" mistake from the Sociology review was not
        # repeated here.
        self.assertNotIn("BIO 426", by_code["NUR 112"]["prerequisites"])
        self.assertNotIn("BIO 420", by_code["NUR 112"]["prerequisites"])

    def test_all_three_official_pdfs_are_retained_and_registered(self):
        self.assertEqual(3, len(self.degree_map["source_pdfs"]))
        for filename in (
            "bmcc_nursing_fall_start_2025_2026.pdf",
            "bmcc_nursing_spring_day_2025_2026.pdf",
            "bmcc_nursing_spring_evening_2025_2026.pdf",
        ):
            self.assertTrue((DOCS / "degree_maps" / filename).is_file())
            self.assertTrue(
                any(filename in source["url"] for source in self.degree_map["source_pdfs"]),
                f"{filename} is not referenced in source_pdfs",
            )

    def test_degree_map_sequences_all_total_sixty_five_credits(self):
        self.assertEqual(65, self.degree_map["total_credits"])

        default_targets = [item["target_credits"] for item in self.degree_map["semesters"]]
        self.assertEqual(65, sum(default_targets))

        self.assertEqual(2, len(self.degree_map["alternate_pathways"]))
        for alternate in self.degree_map["alternate_pathways"]:
            self.assertEqual(65, sum(alternate["semester_credit_targets"]))

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

    def test_progress_page_registers_nursing_map_exactly_once(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        occurrences = page.count('NUR_AAS: "/docs/bmcc_nur_degree_map_2025_2026.json"')
        self.assertEqual(1, occurrences)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)


if __name__ == "__main__":
    unittest.main()
