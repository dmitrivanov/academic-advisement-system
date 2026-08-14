import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class JohnJayCSISCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "docs/jjay_csis_bs_courses.csv").open(newline="", encoding="utf-8-sig") as handle:
            cls.rows = list(csv.DictReader(handle))
        with (ROOT / "docs/pathways_courses.csv").open(newline="", encoding="utf-8-sig") as handle:
            cls.pathways = list(csv.DictReader(handle))

    def test_official_major_structure(self):
        by_group = {}
        for row in self.rows:
            by_group.setdefault(row["group_name"], []).append(row)

        self.assertEqual(33, sum(int(row["credits"]) for row in by_group["Computer Science Core"]))
        self.assertEqual(10, sum(int(row["credits"]) for row in by_group["Mathematics Requirements"]))
        self.assertEqual({"CSCI 400", "CSCI 401"}, {row["course_code"] for row in by_group["Senior Capstone"]})
        self.assertEqual("0", by_group["Foundational Mathematics (placement-dependent)"][0]["required_credits"])

    def test_elective_categories_are_complete(self):
        memberships = {}
        for row in self.pathways:
            if row["institution_code"] == "JOHNJAY":
                memberships.setdefault(row["group_code"], set()).add(row["course_code"])
        self.assertEqual(8, len(memberships["JJAY_CSIS_CSCI_ELECTIVE"]))
        self.assertEqual(10, len(memberships["JJAY_CSIS_MATH_ELECTIVE"]))
        self.assertIn("MAT 244", memberships["JJAY_CSIS_MATH_ELECTIVE"])

    def test_every_placeholder_has_nonempty_selector(self):
        memberships = {
            (row["institution_code"], row["group_code"])
            for row in self.pathways
        }
        for row in self.rows:
            code = row["choice_group_code"]
            if code:
                self.assertIn(("JOHNJAY", code), memberships, row["course_code"])

    def test_student_map_assets_exist(self):
        manifest_path = ROOT / "docs/jjay_csis_degree_map_2024_2025.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(120, manifest["total_credits"])
        for source in manifest["source_pdfs"]:
            self.assertTrue((ROOT / source["url"].lstrip("/")).is_file())

    def test_course_storage_is_campus_scoped(self):
        model_source = (ROOT / "models.py").read_text(encoding="utf-8")
        seeder_source = (ROOT / "seed_database.py").read_text(encoding="utf-8")
        self.assertIn("institution_id = Column(Integer, ForeignKey(\"institutions.id\")", model_source)
        self.assertIn("def get_or_create_course", seeder_source)
        self.assertIn('f"{institution.code}::{catalog_code}"', seeder_source)


if __name__ == "__main__":
    unittest.main()
