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


class SociologyCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("soc_aa_courses.csv")
        cls.adjustments = [
            row for row in read_csv("program_choice_group_adjustments.csv")
            if row["program_code"] == "SOC_AA"
        ]
        cls.pathways_groups = read_csv("pathways_groups.csv")
        cls.pathways_courses = read_csv("pathways_courses.csv")
        cls.degree_map = json.loads(
            (DOCS / "bmcc_soc_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "soc_aa_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_sixty_credit_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("SSH", row["department_code"])
            self.assertEqual("SOC_AA", row["program_code"])
            self.assertEqual("Sociology", row["program_name"])
            self.assertEqual("AA", row["degree_type"])
            self.assertEqual("2025-2026", row["catalog_year"])

        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(60, sum(group_credits.values()))

    def test_common_and_flexible_core_totals(self):
        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(12, group_credits["Required Common Core"])
        self.assertEqual(18, group_credits["Flexible Core"])

    def test_soc_100_and_soc_350_are_individually_required(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertIn("SOC 100", by_code)
        self.assertIn("SOC 350", by_code)
        self.assertEqual("Program Requirements", by_code["SOC 100"]["group_name"])
        self.assertEqual("Program Requirements", by_code["SOC 350"]["group_name"])
        self.assertEqual("3", by_code["SOC 100"]["credits"])
        self.assertEqual("4", by_code["SOC 350"]["credits"])

    def test_speech_alternatives_are_visible_and_reciprocal(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("SPE 102", by_code["SPE 100"]["alternatives"])
        self.assertEqual("SPE 100", by_code["SPE 102"]["alternatives"])
        self.assertEqual("Flexible Core", by_code["SPE 100"]["group_name"])
        self.assertEqual("Flexible Core", by_code["SPE 102"]["group_name"])

    def test_sociology_elective_selector_requires_nine_credits_excludes_soc_100(self):
        rows = [row for row in self.rows if row["group_name"] == "Sociology Electives"]
        codes = {row["course_code"] for row in rows}

        self.assertEqual({"program_required"}, {row["group_type"] for row in rows})
        self.assertEqual({"9"}, {row["required_credits"] for row in rows})
        self.assertNotIn("SOC 100", codes)
        self.assertNotIn("SOC 350", codes)
        self.assertGreater(sum(int(row["credits"]) for row in rows), 9)

    def test_two_hundred_level_constraint_is_machine_enforced(self):
        rows = [row for row in self.rows if row["group_name"] == "Sociology Electives"]
        two_hundred_level = [row for row in rows if row["course_code"].split()[1].startswith("2")]
        self.assertGreaterEqual(len(two_hundred_level), 2, "at least two 200-level SOC electives must be offered")

        encoded = [row["required_course_sets"] for row in rows if row["required_course_sets"]]
        self.assertEqual(1, len(encoded))
        sets = encoded[0].split("||")
        self.assertEqual(
            {"SOC 200", "SOC 210", "SOC 220", "SOC 230", "SOC 234", "SOC 240", "SOC 250", "SOC 256", "SOC 260"},
            set(sets),
        )
        self.assertTrue(all("+" not in code_set for code_set in sets), "each 200-level course must be its own set")

        count_rows = [row["required_course_set_count"] for row in rows if row["required_course_set_count"]]
        self.assertEqual(["2"], count_rows)

        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        self.assertIn("group.required_course_sets?.length", page)
        self.assertIn("courseSet.some", page)

    def test_social_science_selector_requires_six_credits_and_correct_pool(self):
        rows = [row for row in self.rows if row["group_name"] == "Social Science Electives"]
        self.assertEqual({"program_required"}, {row["group_type"] for row in rows})
        self.assertEqual({"6"}, {row["required_credits"] for row in rows})

        placeholder = next(row for row in rows if row["course_code"] == "SOC-AA-SOCSCI")
        self.assertEqual("SOC_AA_SOCIAL_SCIENCE", placeholder["choice_group_code"])

        literal_codes = {row["course_code"] for row in rows if row["course_code"] != "SOC-AA-SOCSCI"}
        self.assertEqual({"CRJ 102", "CRJ 202", "CRJ 204", "HUM 101"}, literal_codes)

        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "SOC_AA_SOCIAL_SCIENCE")
        self.assertEqual(
            {"ANT", "ECO", "GEO", "GWS", "HIS", "PHI", "POL", "PSY"},
            set(adjustment["include_subject_codes"].split("|")),
        )

    def test_ethnic_and_race_studies_selector_requires_three_credits_and_correct_pool(self):
        rows = [row for row in self.rows if row["group_name"] == "Ethnic and Race Studies Elective"]
        self.assertEqual(1, len(rows))
        self.assertEqual("program_required", rows[0]["group_type"])
        self.assertEqual("3", rows[0]["required_credits"])
        self.assertEqual("SOC_AA_ETHNIC_RACE", rows[0]["choice_group_code"])

        adjustment = next(row for row in self.adjustments if row["derived_group_code"] == "SOC_AA_ETHNIC_RACE")
        self.assertEqual({"AFN", "ASN", "ETH", "LAT"}, set(adjustment["include_subject_codes"].split("|")))

    def test_liberal_arts_selector_requires_five_credits_and_is_populated(self):
        rows = [row for row in self.rows if row["group_name"] == "Liberal Arts Elective"]
        self.assertEqual(1, len(rows))
        self.assertEqual("5", rows[0]["required_credits"])
        self.assertEqual("5", rows[0]["credits"])
        self.assertEqual("BMCC_LIBERAL_ARTS_ELECTIVE", rows[0]["choice_group_code"])

        group_codes = {row["group_code"] for row in self.pathways_groups}
        self.assertIn("BMCC_LIBERAL_ARTS_ELECTIVE", group_codes)

    def test_every_placeholder_has_a_populated_choice_group_reference(self):
        placeholders = [row for row in self.rows if "-" in row["course_code"]]
        self.assertTrue(placeholders)
        for row in placeholders:
            self.assertTrue(row["choice_group_code"], row["course_code"])

    def test_every_referenced_choice_group_is_defined_and_has_candidates(self):
        base_codes = {row["group_code"] for row in self.pathways_groups}
        adjustments = {row["derived_group_code"]: row for row in self.adjustments}
        referenced = {row["choice_group_code"] for row in self.rows if row["choice_group_code"]}
        self.assertTrue(referenced)

        pathway_members = {}
        for row in self.pathways_courses:
            pathway_members.setdefault(row["group_code"], set()).add(row["course_code"])

        curriculum_codes = set()
        for path in DOCS.glob("*_courses.csv"):
            for row in read_csv(path.name):
                code = (row.get("course_code") or "").strip()
                if code and "-" not in code:
                    curriculum_codes.add(code)

        for code in referenced:
            self.assertIn(code, base_codes | set(adjustments), f"undefined choice group: {code}")
            if code in adjustments:
                adjustment = adjustments[code]
                candidates = set(pathway_members.get(adjustment["base_group_code"], set()))
                if adjustment["base_group_code"] in {
                    "BMCC_GENERAL_ELECTIVE", "BMCC_LIBERAL_ARTS_ELECTIVE"
                }:
                    candidates |= curriculum_codes
                subjects = {item for item in adjustment["include_subject_codes"].split("|") if item}
                if subjects:
                    candidates = {item for item in candidates if item.split()[0] in subjects}
                included = {item for item in adjustment["include_course_codes"].split("|") if item}
                if included:
                    candidates &= included
                excluded = {item for item in adjustment["exclude_course_codes"].split("|") if item}
                candidates -= excluded
            elif code in {"BMCC_GENERAL_ELECTIVE", "BMCC_LIBERAL_ARTS_ELECTIVE"}:
                candidates = curriculum_codes
            else:
                candidates = pathway_members.get(code, set())
            self.assertTrue(candidates, f"choice group has no candidate courses: {code}")

    def test_flexible_core_two_per_discipline_limit_is_documented_as_unsupported(self):
        sources_text = (DOCS / "soc_aa_sources.md").read_text(encoding="utf-8")
        self.assertIn("No more than two courses", sources_text)
        self.assertIn("KNOWN LIMITATION", sources_text)

    def test_soc_350_enforces_only_the_exactly_representable_prerequisites(self):
        by_code = {row["course_code"]: row for row in self.rows}
        soc_350 = by_code["SOC 350"]
        self.assertEqual("SOC 100|ENG 100.5 or ENG 101", soc_350["prerequisites"])
        self.assertFalse(soc_350["prerequisite_groups"])

        sources_text = (DOCS / "soc_aa_sources.md").read_text(encoding="utf-8")
        self.assertIn("cannot be represented exactly", sources_text)
        self.assertIn("not enforced", sources_text)

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
        self.assertEqual([15, 15, 15, 15], default_targets)
        self.assertEqual(60, sum(default_targets))

        alternate = self.degree_map["alternate_pathways"][0]["semester_credit_targets"]
        self.assertEqual([12, 12, 12, 12, 12], alternate)
        self.assertEqual(60, sum(alternate))

    def test_both_official_pdfs_are_retained_and_registered(self):
        self.assertEqual(2, len(self.degree_map["source_pdfs"]))
        for filename in (
            "bmcc_sociology_2_year_2025_2026.pdf",
            "bmcc_sociology_5_semester_2025_2026.pdf",
        ):
            self.assertTrue((DOCS / "degree_maps" / filename).is_file())
            self.assertTrue(
                any(filename in source["url"] for source in self.degree_map["source_pdfs"]),
                f"{filename} is not referenced in source_pdfs",
            )

    def test_progress_page_registers_sociology_map_exactly_once(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        occurrences = page.count('SOC_AA: "/docs/bmcc_soc_degree_map_2025_2026.json"')
        self.assertEqual(1, occurrences)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)


if __name__ == "__main__":
    unittest.main()
