import csv
import json
import unittest
from pathlib import Path

from scripts.validate_curriculum_csv import validate_file


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def rows(name):
    with (DOCS / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


class WritingLiteratureCurriculaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.general = rows("wal_aa_courses.csv")
        cls.journalism = rows("wal_jrn_aa_courses.csv")
        cls.adjustments = rows("program_choice_group_adjustments.csv")

    def test_two_concentrations_are_selectable_and_current(self):
        programs = {row["program_code"]: row for row in rows("programs.csv")}
        self.assertEqual("Writing and Literature - General Concentration", programs["WAL_AA"]["program_name"])
        self.assertEqual("Writing and Literature - Journalism Concentration", programs["WAL_JRN_AA"]["program_name"])
        self.assertEqual("2025-2026", programs["WAL_AA"]["catalog_year"])
        self.assertEqual("2025-2026", programs["WAL_JRN_AA"]["catalog_year"])

    def test_both_curricula_validate_and_total_sixty_credits(self):
        for filename, curriculum in (
            ("wal_aa_courses.csv", self.general),
            ("wal_jrn_aa_courses.csv", self.journalism),
        ):
            self.assertEqual([], validate_file(DOCS / filename, docs_dir=DOCS).errors)
            group_credits = {row["group_name"]: int(row["required_credits"]) for row in curriculum}
            self.assertEqual(60, sum(group_credits.values()))

    def test_general_requires_three_different_categories(self):
        category_rows = [row for row in self.general if row["group_name"] == "General Concentration Categories"]
        encoded = [row for row in category_rows if row["required_course_sets"]]
        self.assertEqual(1, len(encoded))
        course_sets = encoded[0]["required_course_sets"].split("||")
        self.assertEqual(4, len(course_sets))
        self.assertEqual("3", encoded[0]["required_course_set_count"])
        self.assertEqual({"9"}, {row["required_credits"] for row in category_rows})

    def test_journalism_fixed_courses_and_or_choice_are_exact(self):
        concentration = [row for row in self.journalism if row["group_name"] == "Journalism Concentration Requirements"]
        by_code = {row["course_code"]: row for row in concentration}
        self.assertEqual({"ENG 300", "ENG 303", "ENG 304", "ENG 314", "ENG 335", "ENG 395"}, set(by_code))
        self.assertEqual("ENG 335|ENG 395", by_code["ENG 314"]["alternatives"])
        self.assertEqual("ENG 314|ENG 395", by_code["ENG 335"]["alternatives"])
        self.assertEqual("ENG 314|ENG 335", by_code["ENG 395"]["alternatives"])

    def test_elective_pools_are_concentration_specific_and_populated(self):
        by_program_group = {
            (row["program_code"], row["derived_group_code"]): row
            for row in self.adjustments
            if row["program_code"] in {"WAL_AA", "WAL_JRN_AA"}
        }
        for program in ("WAL_AA", "WAL_JRN_AA"):
            english = by_program_group[(program, "WAL_ENGLISH_ELECTIVES")]
            codes = set(english["include_course_codes"].split("|"))
            self.assertIn("ENG 321", codes)
            self.assertIn("ASN 339", codes)
            self.assertIn("LAT 338", codes)
            self.assertNotIn("ENG 250", codes)

            language = by_program_group[(program, "WAL_MODERN_LANGUAGE")]
            language_codes = set(language["include_course_codes"].split("|"))
            self.assertIn("SPN 106", language_codes)
            self.assertNotIn("ITL 170", language_codes)
            self.assertTrue(all(not code.endswith("E") for code in language_codes))

        general_liberal = by_program_group[("WAL_AA", "WAL_GEN_LIBERAL")]
        journalism_liberal = by_program_group[("WAL_JRN_AA", "WAL_JRN_LIBERAL")]
        self.assertIn("SPE 245", general_liberal["include_course_codes"].split("|"))
        self.assertIn("AFN", journalism_liberal["include_subject_codes"].split("|"))

        seeder = (ROOT / "seed_database.py").read_text(encoding="utf-8")
        self.assertIn("course.code.upper() in include_codes", seeder)
        self.assertIn("course.code.upper().split()[0] in include_subjects", seeder)
        self.assertIn("*explicit_general_courses", seeder)

    def test_creative_expression_excludes_both_speech_options(self):
        rows_for_group = [
            row for row in self.adjustments
            if row["program_code"] in {"WAL_AA", "WAL_JRN_AA"}
            and row["derived_group_code"] == "WAL_CREATIVE"
        ]
        self.assertEqual(2, len(rows_for_group))
        self.assertTrue(all(row["exclude_course_codes"] == "SPE 100|SPE 102" for row in rows_for_group))

    def test_degree_maps_and_source_pdfs_are_registered(self):
        expected = {
            "WAL_AA": ("bmcc_wal_general_degree_map_2025_2026.json", "bmcc_wal_general_2_year_2025_2026.pdf"),
            "WAL_JRN_AA": ("bmcc_wal_journalism_degree_map_2025_2026.json", "bmcc_wal_journalism_2_year_2025_2026.pdf"),
        }
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        for code, (json_name, pdf_name) in expected.items():
            degree_map = json.loads((DOCS / json_name).read_text(encoding="utf-8"))
            self.assertEqual(60, degree_map["total_credits"])
            self.assertEqual(60, sum(item["target_credits"] for item in degree_map["semesters"]))
            self.assertTrue((DOCS / "degree_maps" / pdf_name).is_file())
            self.assertIn(f'{code}: "/docs/{json_name}"', page)

    def test_frontend_enforces_minimum_required_course_sets(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertIn("group.required_course_set_count", page)
        self.assertIn("completedSetCount < requiredSetCount", page)
        self.assertIn("function programElectiveAllocations(completed)", page)
        self.assertIn("used = requiredCourseAllocations(completed)", page)


if __name__ == "__main__":
    unittest.main()
