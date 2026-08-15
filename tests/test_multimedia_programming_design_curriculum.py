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


class MultimediaProgrammingDesignCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("mmp_as_courses.csv")
        cls.degree_map = json.loads(
            (DOCS / "bmcc_mmp_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "mmp_as_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_sixty_credit_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("MMA", row["department_code"])
            self.assertEqual("MMP_AS", row["program_code"])
            self.assertEqual("Multimedia Programming and Design", row["program_name"])
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
        self.assertEqual(24, group_credits["Program Requirements"])
        self.assertEqual(6, group_credits["Multimedia Discipline Sequence"])
        self.assertEqual(6, group_credits["Multimedia Program Elective"])
        self.assertEqual(3, group_credits["Multimedia Advised Elective"])
        self.assertEqual(3, group_credits["General Elective"])

    def test_pathways_substitute_courses_are_fixed_program_requirements(self):
        by_code = {row["course_code"]: row for row in self.rows}
        for code in ("MES 152", "ART 113", "MES 160"):
            self.assertEqual("Program Requirements", by_code[code]["group_name"], code)
            self.assertEqual("", by_code[code]["choice_group_code"], code)

    def test_discipline_sequence_pool_is_choose_two_of_nine(self):
        rows = [row for row in self.rows if row["group_name"] == "Multimedia Discipline Sequence"]
        codes = {row["course_code"] for row in rows}
        self.assertEqual(
            {"MMP 210", "MMP 270", "MMP 271", "MMP 240", "MMP 350", "MMP 202", "MMA 215", "MMA 225", "MMA 235"},
            codes,
        )

    def test_program_elective_and_discipline_sequence_overlap_is_documented(self):
        # The source explicitly forbids double-counting between these two
        # pools, but 9 courses appear in both -- confirm the overlap is
        # real (not accidental) and documented, since the schema cannot
        # enforce the no-double-counting rule itself.
        discipline_codes = {row["course_code"] for row in self.rows if row["group_name"] == "Multimedia Discipline Sequence"}
        elective_codes = {row["course_code"] for row in self.rows if row["group_name"] == "Multimedia Program Elective"}
        self.assertEqual(9, len(discipline_codes & elective_codes))
        sources_text = " ".join((DOCS / "mmp_as_sources.md").read_text(encoding="utf-8").split())
        self.assertIn("cannot count both as MMD program elective", sources_text)

    def test_mmp_460_prerequisite(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("MMP 200", by_code["MMP 460"]["prerequisites"])

    def test_ani_260_and_ani_401_match_sibling_majors(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("MMP 100 or MMA 100", by_code["ANI 260"]["prerequisites"])
        self.assertEqual("MMP 100 or MMA 100", by_code["ANI 401"]["prerequisites"])

    def test_unverified_advised_elective_courses_are_not_guessed_at(self):
        codes = {row["course_code"] for row in self.rows}
        for code in ("ART 102", "ART 104", "ART 107", "ART 133", "ART 174", "ART 176", "ART 183", "ART 233", "MUS 123", "SBE 100"):
            self.assertNotIn(code, codes)

    def test_speech_and_internship_alternatives_are_reciprocal(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("SPE 102", by_code["SPE 100"]["alternatives"])
        self.assertEqual("SPE 100", by_code["SPE 102"]["alternatives"])
        self.assertEqual("MEA 201", by_code["MEA 371"]["alternatives"])
        self.assertEqual("MEA 371", by_code["MEA 201"]["alternatives"])

    def test_no_duplicate_rows_within_a_group(self):
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
            "bmcc_mmd_2_year_2025_2026.pdf",
            "bmcc_mmd_5_semester_2025_2026.pdf",
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

    def test_progress_page_registers_mmp_map_exactly_once(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        occurrences = page.count('MMP_AS: "/docs/bmcc_mmp_degree_map_2025_2026.json"')
        self.assertEqual(1, occurrences)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)


if __name__ == "__main__":
    unittest.main()
