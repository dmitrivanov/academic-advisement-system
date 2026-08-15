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


class CybersecurityCertificateCurriculumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv("cyb_cert_courses.csv")
        cls.degree_map = json.loads(
            (DOCS / "bmcc_cyb_cert_degree_map_2025_2026.json").read_text(encoding="utf-8")
        )

    def test_curriculum_has_no_validation_errors(self):
        result = validate_file(DOCS / "cyb_cert_courses.csv", docs_dir=DOCS)
        self.assertEqual([], result.errors)

    def test_identity_and_thirty_credit_total(self):
        self.assertTrue(self.rows)
        for row in self.rows:
            self.assertEqual("BMCC", row["institution_code"])
            self.assertEqual("CIS", row["department_code"])
            self.assertEqual("CYB_CERT", row["program_code"])
            self.assertEqual("Cybersecurity Certificate", row["program_name"])
            self.assertEqual("CERT", row["degree_type"])
            self.assertEqual("2025-2026", row["catalog_year"])

        group_credits = {
            row["group_name"]: int(row["required_credits"])
            for row in self.rows
        }
        self.assertEqual(30, sum(group_credits.values()))
        self.assertEqual(["Curriculum Requirements"], list(group_credits.keys()))

    def test_ten_courses_all_three_credits_no_electives(self):
        self.assertEqual(10, len(self.rows))
        self.assertEqual({"3"}, {row["credits"] for row in self.rows})
        for row in self.rows:
            self.assertEqual("", row["choice_group_code"], row["course_code"])
            self.assertNotEqual("program_elective", row["group_type"], row["course_code"])

    def test_csc_101_to_cis_165_chain_is_machine_enforced(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("", by_code["CSC 101"]["prerequisites"])
        self.assertEqual("CSC 101", by_code["CIS 165"]["prerequisites"])

    def test_second_level_courses_share_identical_prerequisite(self):
        by_code = {row["course_code"]: row for row in self.rows}
        expected = "CIS 165 or CSC 110 or CSC 111"
        for code in ("CIS 345", "CIS 359", "CIS 440", "CIS 316", "CIS 362"):
            self.assertEqual(expected, by_code[code]["prerequisites"], code)

    def test_cis_459_requires_both_cis_345_and_cis_440(self):
        by_code = {row["course_code"]: row for row in self.rows}
        self.assertEqual("CIS 345|CIS 440", by_code["CIS 459"]["prerequisites"])
        self.assertEqual("CIS 345", by_code["CIS 455"]["prerequisites"])

    def test_cis_459_uses_current_official_title(self):
        by_code = {row["course_code"]: row for row in self.rows}
        # cis_courses.csv (a different program's file) currently lists an
        # older title ("Security Penetration Testing"); this certificate
        # uses the verified, current official title instead.
        self.assertEqual("Ethical Hacking and System Defense", by_code["CIS 459"]["title"])

    def test_degree_map_has_no_alternate_pathway(self):
        # Unlike the full AA/AS/AAS majors, only one official map is
        # published for this certificate.
        self.assertEqual(1, len(self.degree_map["source_pdfs"]))
        self.assertEqual([], self.degree_map["alternate_pathways"])

    def test_degree_map_pdf_is_retained_and_registered(self):
        filename = "bmcc_cybersecurity_certificate_2_year_2025_2026.pdf"
        self.assertTrue((DOCS / "degree_maps" / filename).is_file())
        self.assertTrue(
            any(filename in source["url"] for source in self.degree_map["source_pdfs"]),
            f"{filename} is not referenced in source_pdfs",
        )
        default_targets = [item["target_credits"] for item in self.degree_map["semesters"]]
        self.assertEqual(30, sum(default_targets))
        self.assertEqual(30, self.degree_map["total_credits"])

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

    def test_progress_page_registers_cyb_cert_map_exactly_once(self):
        page = (ROOT / "frontend" / "db_progress_graph.html").read_text(encoding="utf-8")
        occurrences = page.count('CYB_CERT: "/docs/bmcc_cyb_cert_degree_map_2025_2026.json"')
        self.assertEqual(1, occurrences)
        self.assertIn("OFFICIAL_DEGREE_MAP?.source_pdfs", page)


if __name__ == "__main__":
    unittest.main()
