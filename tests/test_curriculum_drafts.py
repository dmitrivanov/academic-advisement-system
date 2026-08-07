import json
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import ChoiceGroup, ChoiceGroupCourse, Course, CurriculumDraft, Department, Institution, Program, RequirementGroup

try:
    from api_db_routes import curriculum_validation, publish_curriculum_draft
except ModuleNotFoundError as exc:
    if exc.name != "fastapi":
        raise
    curriculum_validation = None
    publish_curriculum_draft = None


@unittest.skipUnless(curriculum_validation, "FastAPI application dependencies are not installed")
class CurriculumDraftValidationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        institution = Institution(code="TEST", name="Test College")
        self.db.add(institution)
        self.db.flush()
        department = Department(institution_id=institution.id, code="SCI", name="Science")
        course = Course(code="SCI 100", title="Test Science", credits=3)
        self.db.add_all([department, course])
        self.db.flush()
        core_group = ChoiceGroup(
            institution_id=institution.id,
            code="TEST-FLEX",
            name="Test Flexible Core",
            group_type="flex_core",
            required_credits=3,
        )
        self.db.add(core_group)
        self.db.flush()
        self.db.add(ChoiceGroupCourse(choice_group_id=core_group.id, course_id=course.id))
        self.db.commit()
        self.institution_id = institution.id
        self.department_id = department.id
        self.course_id = course.id

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

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

    def test_empty_elective_pool_is_rejected(self):
        draft = self.make_draft({
            "metadata": {"code": "SCI-AS", "degree_type": "A.S.", "catalog_year": "2026-2027", "source_url": "https://example.edu"},
            "concentrations": [{"name": "General", "bins": {"major_required": [self.course_id]}}],
            "rules": {"elective_pools": [{"name": "Science electives", "required_credits": 3, "course_ids": []}]},
        })
        result = curriculum_validation(draft, self.db)
        self.assertFalse(result["valid"])
        self.assertTrue(any("no course options" in error for error in result["errors"]))

    def test_core_adjustment_requires_placeholder_in_curriculum(self):
        draft = self.make_draft({
            "metadata": {"code": "SCI-AS", "degree_type": "A.S.", "catalog_year": "2026-2027", "source_url": "https://example.edu"},
            "concentrations": [{"name": "General", "bins": {"major_required": []}}],
            "rules": {"core_adjustments": [{"concentration_index": 0, "base_group_code": "TEST-FLEX", "placeholder_course_id": self.course_id, "note": "Choose this course."}]},
        })
        result = curriculum_validation(draft, self.db)
        self.assertFalse(result["valid"])
        self.assertTrue(any("placeholder must also be placed" in error for error in result["errors"]))

    def test_publish_materializes_targets_pools_and_core_adjustment(self):
        document = {
            "metadata": {"code": "SCI-NEW", "degree_type": "A.S.", "catalog_year": "2026-2027", "source_url": "https://example.edu"},
            "concentrations": [{
                "name": "General",
                "bins": {"major_required": [self.course_id], "major_electives": [], "common_core": [], "flex_core": []},
                "bin_requirements": {"major_required": {"required_credits": 3, "required_course_count": 1}},
            }],
            "rules": {
                "elective_pools": [{"name": "Science electives", "concentration_index": 0, "bin": "major_electives", "required_credits": 3, "course_ids": [self.course_id]}],
                "core_adjustments": [{"concentration_index": 0, "base_group_code": "TEST-FLEX", "placeholder_course_id": self.course_id, "note": "Choose the approved science course.", "include_course_ids": [self.course_id]}],
            },
        }
        draft = self.make_draft(document)
        draft.status = "approved"
        self.db.add(draft)
        self.db.commit()

        result = publish_curriculum_draft(draft.id, None, self.db)

        self.assertEqual("published", result["status"])
        program = self.db.query(Program).filter_by(code="SCI-NEW").one()
        major_group = self.db.query(RequirementGroup).filter_by(program_id=program.id, name="Major Requirements").one()
        pool_group = self.db.query(RequirementGroup).filter_by(program_id=program.id, name="Science electives").one()
        self.assertEqual(3, major_group.required_credits)
        self.assertEqual(3, pool_group.required_credits)
        self.assertTrue(self.db.query(ChoiceGroup).filter_by(code="SCI-NEW-TEST-FLEX").first())


if __name__ == "__main__":
    unittest.main()
