import csv
import tempfile
import unittest
from pathlib import Path

from scripts.validate_curriculum_csv import CANONICAL_COLUMNS, validate_file


def valid_rows():
    base = {
        "institution_code": "BMCC",
        "department": "Example Department",
        "department_code": "EX",
        "program_code": "EX_AS",
        "program_name": "Example",
        "degree_type": "AS",
        "catalog_year": "2026-2027",
        "group_name": "Program Requirements",
        "group_type": "program_required",
        "required_credits": "60",
        "display_order": "30",
        "course_code": "EX 101",
        "title": "Example Course I",
        "credits": "30",
        "prerequisites": "",
        "alternatives": "",
        "choice_group_code": "",
        "source": "https://www.bmcc.cuny.edu/example",
    }
    second = dict(base)
    second.update({
        "course_code": "EX 201",
        "title": "Example Course II",
        "prerequisites": "EX 101",
    })
    return [base, second]


class CurriculumValidatorTests(unittest.TestCase):
    def write_csv(self, directory: Path, rows, headers=CANONICAL_COLUMNS, name="ex_as_courses.csv"):
        path = directory / name
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_valid_canonical_file_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = validate_file(self.write_csv(root, valid_rows()), docs_dir=root)
            self.assertEqual([], result.errors)
            self.assertEqual([], result.warnings)

    def test_missing_required_column_is_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            headers = [column for column in CANONICAL_COLUMNS if column != "course_code"]
            rows = [{key: value for key, value in row.items() if key in headers} for row in valid_rows()]
            result = validate_file(self.write_csv(root, rows, headers), docs_dir=root)
            self.assertTrue(any("Missing required column" in item.message for item in result.errors))

    def test_duplicate_course_is_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = valid_rows()
            rows[1]["course_code"] = rows[0]["course_code"]
            result = validate_file(self.write_csv(root, rows), docs_dir=root)
            self.assertTrue(any("Duplicate course" in item.message for item in result.errors))

    def test_inconsistent_program_metadata_is_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = valid_rows()
            rows[1]["catalog_year"] = "2025-2026"
            result = validate_file(self.write_csv(root, rows), docs_dir=root)
            self.assertTrue(any("catalog_year" in item.message and "multiple values" in item.message for item in result.errors))

    def test_external_prerequisite_is_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = valid_rows()
            rows[1]["prerequisites"] = "MAT 999"
            result = validate_file(self.write_csv(root, rows), docs_dir=root)
            self.assertTrue(any("MAT 999" in item.message for item in result.warnings))

    def test_group_credit_shortfall_is_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = valid_rows()
            rows[0]["credits"] = "10"
            rows[1]["credits"] = "10"
            result = validate_file(self.write_csv(root, rows), docs_dir=root)
            self.assertTrue(any("lists 20 credits but requires 60" in item.message for item in result.errors))

    def test_malformed_relationship_is_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = valid_rows()
            rows[1]["prerequisites"] = "EX 101||MAT 100"
            result = validate_file(self.write_csv(root, rows), docs_dir=root)
            self.assertTrue(any("Malformed `prerequisites`" in item.message for item in result.errors))


if __name__ == "__main__":
    unittest.main()
