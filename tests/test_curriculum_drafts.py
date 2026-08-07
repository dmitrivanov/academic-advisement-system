import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import Course, CurriculumDraft, Department, Institution

try:
    from api_db_routes import curriculum_validation
except ModuleNotFoundError as exc:
    if exc.name != "fastapi":
        raise
    curriculum_validation = None


@unittest.skipUnless(curriculum_validation, "FastAPI application dependencies are not installed")
class CurriculumDraftValidationTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        institution = Institution(code="TEST", name="Test College")
        self.db.add(institution)
        self.db.flush()
        department = Department(institution_id=institution.id, code="SCI", name="Science")
        course = Course(code="SCI 100", title="Test Science", credits=3)
        self.db.add_all([department, course])
        self.db.commit()
        self.institution_id = institution.id
        self.department_id = department.id
        self.course_id = course.id

    def tearDown(self):
        self.db.close()

    def make_draft(self, document):
        return CurriculumDraft(
            name="Science",
            institution_id=self.institution_id,
            department_id=self.department_id,
            document_json=json.dumps(document),
        )

    def test_complete_draft_is_valid(self):
        draft = self.make_draft({
            "metadata": {"code": "SCI-AS", "degree_type": "A.S.", "catalog_year": "2026-2027", "source_url": "https://example.edu"},
            "concentrations": [{"name": "General", "bins": {"major_required": [self.course_id], "major_electives": [], "common_core": [], "flex_core": []}}],
            "rules": {},
        })
        result = curriculum_validation(draft, self.db)
        self.assertTrue(result["valid"])
        self.assertEqual([], result["errors"])

    def test_missing_metadata_and_courses_are_rejected(self):
        draft = self.make_draft({"metadata": {}, "concentrations": [{"name": "General", "bins": {}}]})
        result = curriculum_validation(draft, self.db)
        self.assertFalse(result["valid"])
        self.assertTrue(any("program code" in error for error in result["errors"]))
        self.assertTrue(any("no curriculum courses" in error for error in result["errors"]))

    def test_cross_bin_course_is_allowed_with_warning(self):
        draft = self.make_draft({
            "metadata": {"code": "SCI-AS", "degree_type": "A.S.", "catalog_year": "2026-2027", "source_url": "https://example.edu"},
            "concentrations": [{"name": "General", "bins": {"major_required": [self.course_id], "major_electives": [], "common_core": [self.course_id], "flex_core": []}}],
        })
        result = curriculum_validation(draft, self.db)
        self.assertTrue(result["valid"])
        self.assertTrue(any("synchronized" in warning for warning in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
