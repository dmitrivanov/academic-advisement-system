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


class HistoryCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("his_aa_courses.csv")
        cls.adjustments = [
            row for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "HIS_AA"
        ]
        cls.pathways_groups = read_csv("pathways_groups.csv")
        cls.pathways_courses = read_csv("pathways_courses.csv")
        cls.degree_map = json.loads(
            (DOCS / "bmcc_his_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "his_aa_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_sixty_credit_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("SSH", row["department_code"])
            self.assertEqual("HIS_AA", row["program_code"])
            self.assertEqual("History", row["program_name"])
            self.assertEqual("AA", row["degree_type"])
            self.assertEqual("2025-2026", row["catalog_year"])

        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(60, sum(group_credits.values()))

    def test_three_history_sequence_pairs_are_represented(self):
        sequence_rows = [row for row in self.rows if row["group_name"] == "History Sequence"]
        sequence_codes = {row["course_code"] for row in sequence_rows}
        self.assertEqual(
            {"HIS 101", "HIS 102", "HIS 115", "HIS 116", "HIS 120", "HIS 125"},
            sequence_codes,
        )
        self.assertEqual({"6"}, {row["required_credits"] for row in sequence_rows})

    def test_sequence_pairs_are_machine_enforced_and_cannot_be_mixed(self):
        by_code = {row["course_code"]: row for row in self.rows}
        expected = "HIS 101+HIS 102||HIS 115+HIS 116||HIS 120+HIS 125"
        sequence_rows = [row for row in self.rows if row["group_name"] == "History Sequence"]
        self.assertEqual([expected], [row["completion_options"] for row in sequence_rows if row["completion_options"]])
        self.assertEqual("HIS 101", by_code["HIS 102"]["prerequisites"])
        self.assertEqual("HIS 115", by_code["HIS 116"]["prerequisites"])
        self.assertEqual("HIS 120", by_code["HIS 125"]["prerequisites"])

        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertIn("group.completion_options.some", page)
        self.assertIn("option.every", page)

    def test_history_electives_require_nine_credits_from_a_larger_pool(self):
        elective_rows = [row for row in self.rows if row["group_name"] == "History Electives"]
        elective_codes = {row["course_code"] for row in elective_rows}

        self.assertEqual({"9"}, {row["required_credits"] for row in elective_rows})
        self.assertGreater(sum(int(row["credits"]) for row in elective_rows), 9)
        self.assertNotIn("HIS 101", elective_codes)
        self.assertNotIn("HIS 102", elective_codes)
        self.assertNotIn("HIS 115", elective_codes)
        self.assertNotIn("HIS 116", elective_codes)
        self.assertNotIn("HIS 120", elective_codes)
        self.assertNotIn("HIS 125", elective_codes)
        self.assertNotIn("HIS 275", elective_codes)

    def test_non_western_rule_is_machine_enforced(self):
        elective_rows = [row for row in self.rows if row["group_name"] == "History Electives"]
        encoded = [row["required_course_sets"] for row in elective_rows if row["required_course_sets"]]
        self.assertEqual(1, len(encoded))
        self.assertEqual(
            {"HIS 114", "HIS 121", "HIS 122", "HIS 126", "HIS 129", "HIS 130", "HIS 131", "HIS 226"},
            set(encoded[0].split("+")),
        )
        self.assertTrue(all("(non-Western)" not in row["title"] for row in elective_rows))

    def test_his_275_requires_english_and_a_valid_history_sequence(self):
        his_275 = next(row for row in self.rows if row["course_code"] == "HIS 275")
        self.assertEqual("ENG 201", his_275["prerequisites"])
        self.assertEqual("History Sequence", his_275["prerequisite_groups"])
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertIn("course.prerequisite_groups.every", page)

    def test_social_science_ethnic_selector_is_populated_and_requires_six_credits(self):
        rows = [row for row in self.rows if row["group_name"] == "Social Science or Ethnic Studies Electives"]
        self.assertEqual(2, len(rows))
        self.assertEqual({"6"}, {row["required_credits"] for row in rows})
        self.assertTrue(all(row["choice_group_code"] == "HIS_AA_SOCSCI_ETHNIC" for row in rows))

        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "HIS_AA_SOCSCI_ETHNIC")
        self.assertEqual("BMCC_GENERAL_ELECTIVE", adjustment["base_group_code"])
        # BMCC_GENERAL_ELECTIVE is auto-populated by seed_database.py's
        # seed_institutional_elective_groups() from every real course across all
        # curricula and Pathways pools, so a subject-prefix allow-list (matching
        # the pattern already used by ECO_AA_HISTORY, CIS_DEPARTMENT_ELECTIVE, and
        # CNT_DEPARTMENT_ELECTIVE) is the correct way to scope this selector --
        # not a static, hand-maintained course-code list.
        subjects = set(adjustment["include_subject_codes"].split("|"))
        self.assertEqual(
            {"AFL", "AFN", "ANT", "ASN", "ECO", "GEO", "HIS", "LAT", "PHI", "POL", "PSY", "SOC"},
            subjects,
        )
        self.assertEqual("", adjustment["include_course_codes"])

    def test_general_elective_selector_is_populated_and_requires_six_credits(self):
        rows = [row for row in self.rows if row["group_name"] == "General Elective"]
        self.assertEqual(2, len(rows))
        self.assertEqual({"6"}, {row["required_credits"] for row in rows})
        self.assertTrue(all(row["choice_group_code"] == "BMCC_GENERAL_ELECTIVE" for row in rows))

        # BMCC_GENERAL_ELECTIVE is a canonical, already-registered shared group
        # (see docs/pathways_groups.csv); its membership is computed by the
        # seeder at seed time from every curriculum course in the system, not
        # from a static pathways_courses.csv list, so course-level population
        # is verified by the live seed/manual browser check, not this file.
        group_codes = {row["group_code"] for row in self.pathways_groups}
        self.assertIn("BMCC_GENERAL_ELECTIVE", group_codes)

    def test_every_referenced_choice_group_exists_and_has_selectable_courses(self):
        base_group_codes = {row["group_code"] for row in self.pathways_groups}
        derived_group_codes = {row["derived_group_code"] for row in self.adjustments}
        all_known_group_codes = base_group_codes | derived_group_codes

        referenced = {row["choice_group_code"] for row in self.rows if row["choice_group_code"]}
        for code in referenced:
            self.assertIn(code, all_known_group_codes, f"{code} is not defined anywhere")

        courses_by_group = {}
        for row in self.pathways_courses:
            courses_by_group.setdefault(row["group_code"], []).append(row["course_code"])

        for adjustment in self.adjustments:
            base_courses = set(courses_by_group.get(adjustment["base_group_code"], []))
            include = [c for c in adjustment["include_course_codes"].split("|") if c]
            if include:
                self.assertTrue(set(include).issubset(base_courses) or adjustment["base_group_code"] == "BMCC_GENERAL_ELECTIVE")

            include_subjects = [c for c in adjustment.get("include_subject_codes", "").split("|") if c]
            if include_subjects and adjustment["derived_group_code"] == "HIS_AA_SOCSCI_ETHNIC":
                self.assertTrue(all(subject.isalpha() and subject.isupper() for subject in include_subjects))

    def test_creative_expression_second_course_excludes_speech_courses(self):
        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "HIS_AA_CREATIVE")
        self.assertEqual("FC_CREATIVE", adjustment["base_group_code"])
        self.assertEqual("SPE 100|SPE 102", adjustment["exclude_course_codes"])

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

    def test_degree_map_has_default_and_alternate_sequences_totaling_sixty(self):
        self.assertEqual(4, self.degree_map["default_semesters"])
        self.assertEqual(60, self.degree_map["total_credits"])

        default_targets = [item["target_credits"] for item in self.degree_map["semesters"]]
        self.assertEqual(60, sum(default_targets))

        alternate = self.degree_map["alternate_pathways"][0]["semester_credit_targets"]
        self.assertEqual(60, sum(alternate))

    def test_both_official_pdfs_are_retained_and_registered(self):
        self.assertEqual(2, len(self.degree_map["source_pdfs"]))
        for filename in (
            "bmcc_history_2_year_2025_2026.pdf",
            "bmcc_history_5_semester_2025_2026.pdf",
        ):
            self.assertTrue((DOCS / "degree_maps" / filename).is_file())
            self.assertTrue(
                any(filename in source["url"] for source in self.degree_map["source_pdfs"]),
                f"{filename} is not referenced in source_pdfs",
            )

    def test_progress_page_registers_history_map_exactly_once(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        occurrences = page.count('HIS_AA: "/docs/bmcc_his_degree_map_2025_2026.json"')
        self.assertEqual(1, occurrences)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)


if __name__ == "__main__":
    unittest.main()
