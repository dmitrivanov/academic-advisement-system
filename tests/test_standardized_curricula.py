import csv
import unittest
from pathlib import Path

from scripts.validate_curriculum_csv import validate_file


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def rows(filename):
    with (DOCS / filename).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


class StandardizedCurriculaTests(unittest.TestCase):
    def test_every_curriculum_uses_full_schema(self):
        legacy = []
        for path in sorted(DOCS.glob("*_courses.csv")):
            if path.name == "pathways_courses.csv":
                continue
            with path.open(newline="", encoding="utf-8-sig") as handle:
                headers = set(csv.DictReader(handle).fieldnames or [])
            if "institution_code" not in headers or "source" not in headers:
                legacy.append(path.name)
        self.assertEqual([], legacy)

    def test_every_choice_reference_is_declared(self):
        base = {row["group_code"] for row in rows("pathways_groups.csv")}
        derived = {
            row["derived_group_code"]
            for row in rows("program_choice_group_adjustments.csv")
        }
        missing = []
        for path in sorted(DOCS.glob("*_courses.csv")):
            if path.name == "pathways_courses.csv":
                continue
            for row in rows(path.name):
                code = row.get("choice_group_code", "")
                if code and code not in base | derived:
                    missing.append(f"{path.name}:{row['course_code']} -> {code}")
        self.assertEqual([], missing)

    def test_bmcc_computing_programs_are_complete_and_valid(self):
        expected = {
            "cs_courses.csv": ("CS", "AS", 60),
            "cis_courses.csv": ("CIS", "AAS", 60),
            "cnt_courses.csv": ("CNT", "AAS", 60),
        }
        for filename, (program, degree, total) in expected.items():
            with self.subTest(filename=filename):
                curriculum = rows(filename)
                self.assertFalse(validate_file(DOCS / filename, docs_dir=DOCS).errors)
                self.assertEqual({program}, {row["program_code"] for row in curriculum})
                self.assertEqual({degree}, {row["degree_type"] for row in curriculum})
                groups = {row["group_name"]: int(row["required_credits"]) for row in curriculum}
                self.assertEqual(total, sum(groups.values()))
                self.assertTrue({"common_core", "flexible_core", "program_required", "program_elective"}.issubset(
                    {row["group_type"] for row in curriculum}
                ))

    def test_good_cs_selection_is_preserved_and_footnotes_corrected(self):
        curriculum = rows("cs_courses.csv")
        by_group = {}
        for row in curriculum:
            by_group.setdefault(row["group_name"], set()).add(row["course_code"])

        expected_electives = {
            "CIS 317", "CIS 345", "CIS 359", "CIS 362", "CIS 364", "CIS 385",
            "CIS 395", "CSC 103", "GIS 201", "CIS 316", "CIS 272", "CIS 285", "CSC 203",
        }
        self.assertEqual(expected_electives, by_group["Program Electives"])
        self.assertEqual(
            {"CSC 211", "CSC 215", "CSC 231", "CSC 331", "CSC 350", "MAT 302"},
            by_group["Curriculum Requirements"],
        )

        adjustments = {row["derived_group_code"]: row for row in rows("program_choice_group_adjustments.csv")}
        self.assertEqual("MAT 206|MAT 301", adjustments["CS_MATH_QUANT"]["include_course_codes"])
        self.assertEqual("PHY 215", adjustments["CS_LIFE_PHYSICAL"]["include_course_codes"])
        self.assertEqual("SPE 100|SPE 102", adjustments["CS_CREATIVE"]["include_course_codes"])

    def test_ccny_placeholders_are_bound_to_separate_ccny_pools(self):
        curriculum = rows("ccny_cs_bs_courses.csv")
        placeholders = [row for row in curriculum if row["course_code"].startswith("CCNY-")]
        self.assertTrue(placeholders)
        self.assertTrue(all(row["choice_group_code"].startswith("CCNY_") for row in placeholders))


if __name__ == "__main__":
    unittest.main()
