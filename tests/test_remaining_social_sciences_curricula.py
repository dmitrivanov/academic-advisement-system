import csv
import json
import unittest
from pathlib import Path

from scripts.validate_curriculum_csv import validate_file


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PROGRAMS = {
    "GWS_AA": ("gws_aa_courses.csv", "AA"),
    "GER_AS": ("ger_as_courses.csv", "AS"),
    "POL_AA": ("pol_aa_courses.csv", "AA"),
    "PHI_AA": ("phi_aa_courses.csv", "AA"),
    "HMS_AS": ("hms_as_courses.csv", "AS"),
    "URB_AA": ("urb_aa_courses.csv", "AA"),
}


def rows(name):
    with (DOCS / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


class RemainingSocialSciencesCurriculaTests(unittest.TestCase):
    def test_each_curriculum_validates_and_totals_sixty(self):
        for code, (filename, degree) in PROGRAMS.items():
            data = rows(filename)
            self.assertEqual([], validate_file(DOCS / filename, docs_dir=DOCS).errors, code)
            self.assertEqual({code}, {row["program_code"] for row in data})
            self.assertEqual({degree}, {row["degree_type"] for row in data})
            self.assertEqual({"2025-2026"}, {row["catalog_year"] for row in data})
            groups = {row["group_name"]: int(row["required_credits"]) for row in data}
            self.assertEqual(60, sum(groups.values()), code)

    def test_every_placeholder_has_a_choice_group(self):
        for code, (filename, _) in PROGRAMS.items():
            for row in rows(filename):
                if "-" in row["course_code"]:
                    self.assertTrue(row["choice_group_code"], (code, row["course_code"]))

    def test_exact_major_specific_pools_are_declared(self):
        adjustments = {row["derived_group_code"]: row for row in rows("program_choice_group_adjustments.csv")}
        expected = {
            "GWS_AA_ELECTIVES": ("9", "3"),
            "GER_AS_ELECTIVES": ("6", "2"),
            "POL_AA_100_200": ("6", "2"),
            "POL_AA_200_LEVEL": ("6", "2"),
            "PHI_AA_LOGIC_CRT": ("3", "1"),
            "PHI_AA_100_LEVEL": ("3", "1"),
            "PHI_AA_200_LEVEL": ("6", "2"),
            "HMS_AS_HUM_OPTION": ("3", "1"),
            "HMS_AS_PSY_SOC_OPTION": ("3", "1"),
            "URB_AA_ELECTIVES": ("6", "2"),
            "URB_AA_SOCIAL_SCIENCE": ("9", "3"),
        }
        for code, targets in expected.items():
            self.assertIn(code, adjustments)
            self.assertEqual(targets, (adjustments[code]["required_credits"], adjustments[code]["required_course_count"]))

    def test_five_published_map_pairs_are_valid_and_registered(self):
        specs = {
            "GWS_AA": ("bmcc_gws_degree_map_2025_2026.json", "gender_womens_studies"),
            "GER_AS": ("bmcc_ger_degree_map_2025_2026.json", "gerontology"),
            "POL_AA": ("bmcc_pol_degree_map_2025_2026.json", "political_science"),
            "HMS_AS": ("bmcc_hms_degree_map_2025_2026.json", "human_services"),
            "URB_AA": ("bmcc_urb_degree_map_2025_2026.json", "urban_studies"),
        }
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        for code, (map_name, stem) in specs.items():
            metadata = json.loads((DOCS / map_name).read_text(encoding="utf-8"))
            self.assertEqual(60, metadata["total_credits"])
            self.assertEqual(2, len(metadata["source_pdfs"]))
            self.assertEqual(1, page.count(f'{code}: "/docs/{map_name}"'))
            for layout in ("2_year", "5_semester"):
                pdf = DOCS / "degree_maps" / f"bmcc_{stem}_{layout}_2025_2026.pdf"
                self.assertEqual(b"%PDF-", pdf.read_bytes()[:5])

    def test_philosophy_official_page_has_no_published_map_link(self):
        notes = (DOCS / "phi_aa_sources.md").read_text(encoding="utf-8")
        self.assertIn("currently exposes no Philosophy degree-map links", notes)

    def test_history_is_reused_not_duplicated(self):
        program_rows = [row for row in rows("programs.csv") if row["program_code"] == "HIS_AA"]
        self.assertEqual(1, len(program_rows))
        self.assertTrue((DOCS / "his_aa_courses.csv").is_file())


if __name__ == "__main__":
    unittest.main()
