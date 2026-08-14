import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BrooklynComputerScienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "docs/bc_cs_bs_courses.csv").open(newline="", encoding="utf-8-sig") as handle:
            cls.rows = list(csv.DictReader(handle))
        with (ROOT / "docs/pathways_courses.csv").open(newline="", encoding="utf-8-sig") as handle:
            cls.pathways = list(csv.DictReader(handle))

    def test_latest_official_map_totals(self):
        manifest = json.loads((ROOT / "docs/bc_cs_degree_map_2026_2027.json").read_text())
        self.assertEqual("2026-2027", manifest["catalog_year"])
        self.assertEqual(120, manifest["total_credits"])
        self.assertEqual(8, len(manifest["semesters"]))

    def test_major_credit_structure_is_56_credits(self):
        # Count one representative from each OR group and the full elective pool.
        required = {
            "Programming Foundation": 4, "Major Requirements": 20,
            "Architecture Alternative": 3, "Theory Alternative": 3,
            "Ethics Alternative": 3, "Capstone Alternative": 3,
            "Mathematics Requirements": 8, "Statistics Alternative": 3,
            "Advanced CISC Electives": 9,
        }
        self.assertEqual(56, sum(required.values()))
        by_group = {row["group_name"]: row["required_credits"] for row in self.rows}
        for name, credits in required.items():
            self.assertEqual(str(credits), by_group[name])

    def test_all_or_blocks_are_machine_enforced(self):
        expected = {
            "Programming Foundation": {"CISC 1115", "CISC 1170"},
            "Architecture Alternative": {"CISC 3305", "CISC 3310"},
            "Theory Alternative": {"CISC 3220", "CISC 3230"},
            "Ethics Alternative": {"CISC 2820W", "PHIL 3318W"},
            "Capstone Alternative": {"CISC 4900", "CISC 5001"},
            "Statistics Alternative": {"MATH 2501", "MATH 3501"},
        }
        for group, codes in expected.items():
            rows = [row for row in self.rows if row["group_name"] == group]
            self.assertEqual(codes, {row["course_code"] for row in rows})
            self.assertEqual({"||".join(sorted(codes))}, {"||".join(sorted(row["completion_options"].split("||"))) for row in rows})
            self.assertTrue(all(row["alternatives"] in codes for row in rows))

    def test_precalculus_placement_alternative_is_not_double_counted(self):
        rows = [
            row for row in self.rows
            if row["group_name"] == "Required Core"
            and row["course_code"] in {"MATH 1011", "MATH 1012"}
        ]
        self.assertEqual({"MATH 1011", "MATH 1012"}, {row["course_code"] for row in rows})
        self.assertEqual({"MATH 1011", "MATH 1012"}, {row["alternatives"] for row in rows})
        # Required Core contains several independent requirements, so the OR
        # relationship belongs on these rows rather than the whole group.
        self.assertTrue(all(not row["completion_options"] for row in rows))

    def test_math_1006_is_optional_placement_preparation(self):
        rows = [row for row in self.rows if row["course_code"] == "MATH 1006"]
        self.assertEqual(1, len(rows))
        self.assertEqual("Mathematics Placement Preparation", rows[0]["group_name"])
        self.assertEqual("0", rows[0]["required_credits"])

    def test_every_selector_is_populated(self):
        memberships = {(row["institution_code"], row["group_code"]) for row in self.pathways}
        with (ROOT / "docs/program_choice_group_adjustments.csv").open(newline="", encoding="utf-8-sig") as handle:
            derived = {
                (row["institution_code"], row["derived_group_code"])
                for row in csv.DictReader(handle)
            }
        for row in self.rows:
            if row["choice_group_code"]:
                self.assertIn(("BROOKLYN", row["choice_group_code"]), memberships | derived)

    def test_course_identity_is_campus_plus_code(self):
        source = (ROOT / "models.py").read_text(encoding="utf-8")
        self.assertIn('UniqueConstraint("institution_id", "code", name="uq_course_institution_code")', source)
        self.assertNotIn("code = Column(String, nullable=False, unique=True)", source)


if __name__ == "__main__":
    unittest.main()
