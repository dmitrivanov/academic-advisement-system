import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def read_csv(name):
    with (DOCS / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


class PsychologyCurriculaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.general = read_csv("psy_aa_courses.csv")
        cls.stem = read_csv("psy_stem_aa_courses.csv")
        cls.adjustments = read_csv("program_choice_group_adjustments.csv")
        cls.general_map = json.loads(
            (DOCS / "bmcc_psy_general_degree_map_2025_2026.json").read_text()
        )
        cls.stem_map = json.loads(
            (DOCS / "bmcc_psy_stem_degree_map_2025_2026.json").read_text()
        )

    def test_two_selectable_concentrations_have_stable_codes(self):
        programs = read_csv("programs.csv")
        psychology = {
            row["program_code"]: row["program_name"]
            for row in programs
            if row["institution_code"] == "BMCC" and row["program_code"].startswith("PSY")
        }
        self.assertEqual(
            {
                "PSY_AA": "Psychology - General Concentration",
                "PSY_STEM_AA": "Psychology - STEM Concentration",
            },
            psychology,
        )

    def test_each_concentration_reconciles_to_sixty_credits(self):
        for rows in (self.general, self.stem):
            groups = {}
            for row in rows:
                groups[row["group_name"]] = int(row["required_credits"])
                self.assertEqual("2025-2026", row["catalog_year"])
                self.assertEqual("AA", row["degree_type"])
            self.assertEqual(60, sum(groups.values()))

    def test_concentration_specific_required_courses(self):
        general_codes = {row["course_code"] for row in self.general}
        stem_codes = {row["course_code"] for row in self.stem}
        self.assertTrue({"PSY 220", "PSY 265", "PSY 240", "PSY 230", "ANT 100"} <= general_codes)
        self.assertTrue({"MAT 301", "PSY 220", "PSY 225", "PSY 255", "PSY 265"} <= stem_codes)
        self.assertNotIn("MAT 301", general_codes)

    def test_psychology_electives_require_nine_credits(self):
        for rows in (self.general, self.stem):
            elective_rows = [row for row in rows if row["group_name"] == "Psychology Electives"]
            self.assertGreaterEqual(len(elective_rows), 8)
            self.assertEqual({"9"}, {row["required_credits"] for row in elective_rows})
            self.assertTrue(all(row["prerequisites"] == "PSY 100" for row in elective_rows))

    def test_program_specific_pathways_adjustments_exist(self):
        by_program = {}
        for row in self.adjustments:
            by_program.setdefault(row["program_code"], set()).add(row["derived_group_code"])
        self.assertEqual(
            {"PSY_GEN_MATH_QUANT", "PSY_GEN_LIFE_PHYSICAL", "PSY_GEN_CREATIVE", "PSY_GEN_INDIVIDUAL"},
            by_program["PSY_AA"],
        )
        self.assertEqual(
            {"PSY_STEM_MATH_QUANT", "PSY_STEM_LIFE_PHYSICAL", "PSY_STEM_CREATIVE", "PSY_STEM_INDIVIDUAL"},
            by_program["PSY_STEM_AA"],
        )

    def test_four_and_five_semester_maps_total_sixty(self):
        for degree_map, default_targets, alternate_targets in (
            (self.general_map, [16, 16, 14, 14], [10, 12, 13, 12, 13]),
            (self.stem_map, [14, 17, 16, 13], [10, 13, 14, 14, 9]),
        ):
            self.assertEqual(60, degree_map["total_credits"])
            self.assertEqual(default_targets, [item["target_credits"] for item in degree_map["semesters"]])
            self.assertEqual(60, sum(default_targets))
            self.assertEqual(alternate_targets, degree_map["alternate_pathways"][0]["semester_credit_targets"])
            self.assertEqual(60, sum(alternate_targets))
            self.assertEqual(2, len(degree_map["source_pdfs"]))

    def test_all_four_source_pdfs_are_retained(self):
        for filename in (
            "bmcc_psychology_general_2_year_2025_2026.pdf",
            "bmcc_psychology_general_5_semester_2025_2026.pdf",
            "bmcc_psychology_stem_2_year_2025_2026.pdf",
            "bmcc_psychology_stem_5_semester_2025_2026.pdf",
        ):
            self.assertTrue((DOCS / "degree_maps" / filename).is_file())

    def test_progress_page_registers_both_maps_and_source_links(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text()
        self.assertIn('PSY_AA: "/docs/bmcc_psy_general_degree_map_2025_2026.json"', page)
        self.assertIn('PSY_STEM_AA: "/docs/bmcc_psy_stem_degree_map_2025_2026.json"', page)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)
        self.assertIn("Official maps", page)


if __name__ == "__main__":
    unittest.main()
