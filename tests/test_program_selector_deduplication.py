import csv
import glob
import unittest
from pathlib import Path

from program_selector_logic import (
    canonical_selector_programs,
    catalog_year_rank,
    normalized_program_identity,
)


ROOT = Path(__file__).resolve().parents[1]


def program(id, *, campus="BMCC", name="Computer Science", degree="AS", year="2026", populated=True):
    return {
        "id": id,
        "code": f"P{id}",
        "name": name,
        "degree_type": degree,
        "catalog_year": year,
        "institution": campus,
        "institution_code": campus,
        "has_curriculum": populated,
        "course_count": 10 if populated else 0,
    }


class ProgramSelectorDeduplicationTests(unittest.TestCase):
    def test_populated_older_record_beats_empty_newer_record(self):
        result = canonical_selector_programs([
            program(1, year="2025-2026", populated=True),
            program(2, year="2027", populated=False),
        ])
        self.assertEqual([1], [item["id"] for item in result])

    def test_newest_populated_catalog_wins(self):
        result = canonical_selector_programs([
            program(1, year="2024-2025"),
            program(2, year="2025-2026"),
        ])
        self.assertEqual([2], [item["id"] for item in result])

    def test_only_newest_empty_record_remains(self):
        result = canonical_selector_programs([
            program(1, year="2025", populated=False),
            program(2, year="2026", populated=False),
        ])
        self.assertEqual([2], [item["id"] for item in result])
        self.assertFalse(result[0]["has_curriculum"])

    def test_catalog_year_parser_handles_ranges_dashes_and_bad_values(self):
        self.assertGreater(catalog_year_rank("2025-2026"), catalog_year_rank("2024-2025"))
        self.assertEqual(catalog_year_rank("2025-2026")[:3], catalog_year_rank(" 2025–2026 ")[:3])
        self.assertGreater(catalog_year_rank("2026"), catalog_year_rank("2025-2026"))
        self.assertGreater(catalog_year_rank("2025-26"), catalog_year_rank("not-a-year"))
        self.assertGreater(catalog_year_rank("2025-26"), catalog_year_rank(None))

    def test_exact_tie_uses_highest_database_id(self):
        result = canonical_selector_programs([program(8), program(12)])
        self.assertEqual([12], [item["id"] for item in result])

    def test_identity_preserves_campus_degree_and_concentration(self):
        candidates = [
            program(1, campus="BMCC", degree="AA", name="Psychology - General Concentration"),
            program(2, campus="BMCC", degree="AS", name="Psychology - General Concentration"),
            program(3, campus="CCNY", degree="AA", name="Psychology - General Concentration"),
            program(4, campus="BMCC", degree="AA", name="Psychology - STEM Concentration"),
        ]
        self.assertEqual(4, len(canonical_selector_programs(candidates)))

    def test_identity_normalizes_case_and_whitespace_only(self):
        left = program(1, campus="BMCC", name="  Computer   Science ", degree="AS")
        right = program(2, campus="bmcc", name="computer science", degree="as")
        self.assertEqual(normalized_program_identity(left), normalized_program_identity(right))
        self.assertEqual([2], [item["id"] for item in canonical_selector_programs([left, right])])

    def test_repository_catalog_exposes_no_duplicate_selector_identities(self):
        with (ROOT / "docs" / "programs.csv").open(newline="", encoding="utf-8-sig") as handle:
            catalog = list(csv.DictReader(handle))
        curriculum_codes = set()
        for filename in glob.glob(str(ROOT / "docs" / "*_courses.csv")):
            with open(filename, newline="", encoding="utf-8-sig") as handle:
                first = next(csv.DictReader(handle), None)
                if first:
                    curriculum_codes.add((first.get("program_code") or "").strip())
        payloads = [
            {
                "id": index,
                "code": row["program_code"],
                "name": row["program_name"],
                "degree_type": row["degree_type"],
                "catalog_year": row["catalog_year"],
                "institution_code": row["institution_code"],
                "institution": row["institution_code"],
                "has_curriculum": row["program_code"] in curriculum_codes,
                "course_count": int(row["program_code"] in curriculum_codes),
            }
            for index, row in enumerate(catalog, start=1)
        ]
        selector = canonical_selector_programs(payloads)
        identities = [normalized_program_identity(item) for item in selector]
        self.assertEqual(len(identities), len(set(identities)))

    def test_all_student_surfaces_use_selector_endpoint_and_admin_does_not(self):
        for filename in ("program_selector.html", "db_progress_graph.html", "transfer_analysis.html"):
            source = (ROOT / "frontend" / filename).read_text(encoding="utf-8")
            self.assertIn('/api/db/programs?selector_only=true', source)
        admin = (ROOT / "frontend" / "admin_dashboard.html").read_text(encoding="utf-8")
        self.assertIn('fetchJson("/api/db/programs")', admin)
        self.assertNotIn('/api/db/programs?selector_only=true', admin)


try:
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import sessionmaker
    from database import Base
    from models import Department, Institution, Program
    from api_db_routes import get_programs
except ModuleNotFoundError:
    get_programs = None


@unittest.skipUnless(get_programs, "FastAPI application dependencies are not installed")
class ProgramSelectorQueryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        institution = Institution(code="TEST", name="Test College")
        self.db.add(institution)
        self.db.flush()
        department = Department(institution_id=institution.id, code="GEN", name="General")
        self.db.add(department)
        self.db.flush()
        self.department_id = department.id

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_normal_endpoint_returns_all_and_selector_collapses(self):
        self.db.add_all([
            Program(department_id=self.department_id, code="OLD", name="Example", degree_type="AA", catalog_year="2025"),
            Program(department_id=self.department_id, code="NEW", name="Example", degree_type="AA", catalog_year="2026"),
        ])
        self.db.commit()
        self.assertEqual(2, len(get_programs(selector_only=False, db=self.db)))
        self.assertEqual(1, len(get_programs(selector_only=True, db=self.db)))

    def test_query_count_remains_constant_as_program_count_grows(self):
        self.db.add_all([
            Program(department_id=self.department_id, code=f"P{i}", name=f"Program {i}", degree_type="AA", catalog_year="2026")
            for i in range(250)
        ])
        self.db.commit()
        statements = []
        event.listen(self.engine, "before_cursor_execute", lambda *args: statements.append(args[2]))
        get_programs(selector_only=True, db=self.db)
        self.assertLessEqual(len(statements), 3)


if __name__ == "__main__":
    unittest.main()
