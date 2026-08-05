import csv
import unittest
from pathlib import Path

from scripts.validate_curriculum_csv import validate_file


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


PROGRAMS = {
    "bte_as_courses.csv": ("BTE_AS", "Biotechnology Science", "2026-2027", 60),
    "esc_as_courses.csv": ("ESC_AS", "Engineering Science", "2026-2027", 65),
    "fsc_as_courses.csv": ("FSC_AS", "Science for Forensics", "2026-2027", 68),
    "sci_as_courses.csv": ("SCI_AS", "Science", "2025-2026", 60),
    "shp_as_courses.csv": ("SHP_AS", "Science for Health", "2025-2026", 60),
}


class ScienceCurriculaTests(unittest.TestCase):
    def test_identity_totals_and_validation(self):
        for filename, (code, name, year, total) in PROGRAMS.items():
            with self.subTest(filename=filename):
                path = DOCS / filename
                with path.open(newline="", encoding="utf-8-sig") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertTrue(rows)
                self.assertFalse(validate_file(path, docs_dir=DOCS).errors)
                self.assertEqual({code}, {row["program_code"] for row in rows})
                self.assertEqual({name}, {row["program_name"] for row in rows})
                self.assertEqual({year}, {row["catalog_year"] for row in rows})
                groups = {row["group_name"]: int(row["required_credits"]) for row in rows}
                self.assertEqual(total, sum(groups.values()))

    def test_published_sequences_are_locked(self):
        expected = {
            "bte_as_courses.csv": {"BIO 220": "BIO 210", "CHE 240": "CHE 230", "BTE 201": "BIO 220|CHE 202"},
            "esc_as_courses.csv": {"MAT 303": "MAT 302", "PHY 225": "PHY 215", "MAT 501": "MAT 302"},
            "fsc_as_courses.csv": {"CHE 205": "CHE 202|MAT 206", "CHE 240": "CHE 230", "PHY 225": "PHY 215"},
            "shp_as_courses.csv": {"CHE 122": "CHE 121", "BIO 425": "CHE 121", "BIO 426": "BIO 425"},
        }
        for filename, relationships in expected.items():
            with (DOCS / filename).open(newline="", encoding="utf-8-sig") as handle:
                by_code = {row["course_code"]: row for row in csv.DictReader(handle)}
            for code, prerequisite in relationships.items():
                self.assertEqual(prerequisite, by_code[code]["prerequisites"])

    def test_engineering_science_exposes_common_and_flexible_core(self):
        with (DOCS / "esc_as_courses.csv").open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))

        groups = {(row["group_name"], row["group_type"]) for row in rows}
        self.assertIn(("Required Common Core", "common_core"), groups)
        self.assertIn(("Flexible Core", "flexible_core"), groups)

        common_codes = {
            row["course_code"] for row in rows if row["group_type"] == "common_core"
        }
        flexible_codes = {
            row["course_code"] for row in rows if row["group_type"] == "flexible_core"
        }
        self.assertEqual({"ENG 101", "ENG 201", "MAT 206", "CHE 201"}, common_codes)
        self.assertTrue(
            {"SPE 100", "CHE 202", "SCI 120", "FC-INDIVIDUAL", "FC-US-EXP", "FC-WORLD-CULTURES"}
            .issubset(flexible_codes)
        )


if __name__ == "__main__":
    unittest.main()
