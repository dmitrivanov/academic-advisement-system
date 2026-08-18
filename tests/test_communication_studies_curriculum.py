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


class CommunicationStudiesCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("com_aa_courses.csv")
        cls.adjustments = [
            row for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "COM_AA"
        ]
        cls.degree_map = json.loads(
            (DOCS / "bmcc_com_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "com_aa_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_sixty_credit_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("SCT", row["department_code"])
            self.assertEqual("COM_AA", row["program_code"])
            self.assertEqual("Communication Studies", row["program_name"])
            self.assertEqual("AA", row["degree_type"])
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
        self.assertEqual(24, group_credits["Program Requirements"])
        self.assertEqual(12, group_credits["COM Advised Elective"])
        self.assertEqual(6, group_credits["COM Program Elective"])

    def test_advised_elective_is_modeled_as_four_courses_not_five(self):
        # Both official degree maps' footnotes say "5 courses / 15
        # credits", but both maps' own course tables only show 4 slots,
        # and the published 60-credit total only balances with 4.
        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "COM_AA_ADVISED")
        self.assertEqual("12", adjustment["required_credits"])
        self.assertEqual("4", adjustment["required_course_count"])

    def test_speech_alternatives_are_reciprocal(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("SPE 102", by_code["SPE 100"]["alternatives"])
        self.assertEqual("SPE 100", by_code["SPE 102"]["alternatives"])

    def test_the_100_four_way_alternative_cluster(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("MES 153|MUS 107|ART 106", by_code["THE 100"]["alternatives"])
        self.assertEqual("THE 100", by_code["MES 153"]["alternatives"])
        self.assertEqual("THE 100", by_code["MUS 107"]["alternatives"])
        self.assertEqual("THE 100", by_code["ART 106"]["alternatives"])

    def test_com_prerequisites(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("SPE 100", by_code["COM 240"]["prerequisites"])
        self.assertEqual("SPE 100", by_code["COM 245"]["prerequisites"])
        self.assertEqual("SPE 100 or SPE 102", by_code["COM 255"]["prerequisites"])

    def test_advised_elective_named_course_prerequisites(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("ENG 101|MAR 100", by_code["MAR 220"]["prerequisites"])
        self.assertEqual("ENG 101|MAR 100", by_code["MAR 230"]["prerequisites"])
        self.assertEqual("ENG 101|ENG 201|BUS 104", by_code["BUS 150"]["prerequisites"])

    def test_program_elective_is_com_subject_wildcard(self):
        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "COM_AA_PROGRAM")
        self.assertEqual("COM", adjustment["include_subject_codes"])
        self.assertEqual("2", adjustment["required_course_count"])

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
            "bmcc_com_2_year_2025_2026.pdf",
            "bmcc_com_5_semester_2025_2026.pdf",
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

    def test_progress_page_registers_com_map_exactly_once(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        occurrences = page.count('COM_AA: "/docs/bmcc_com_degree_map_2025_2026.json"')
        self.assertEqual(1, occurrences)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)


if __name__ == "__main__":
    unittest.main()
