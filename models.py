from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, unique=True, nullable=False)
    system = Column(String, default="CUNY")
    borough = Column(String, nullable=True)
    website = Column(String, nullable=True)

    departments = relationship("Department", back_populates="institution")
    choice_groups = relationship("ChoiceGroup", back_populates="institution")
    courses = relationship("Course", back_populates="institution")
    outgoing_equivalencies = relationship(
        "CourseEquivalency",
        foreign_keys="CourseEquivalency.source_institution_id",
        back_populates="source_institution",
    )
    incoming_equivalencies = relationship(
        "CourseEquivalency",
        foreign_keys="CourseEquivalency.target_institution_id",
        back_populates="target_institution",
    )


class CourseEquivalency(Base):
    """A directional, institution-scoped transfer rule.

    Course codes are stored on the rule for now because the legacy Course table
    is globally keyed by code. This lets equivalencies be institution-aware
    without a risky course-table migration.
    """

    __tablename__ = "course_equivalencies"

    id = Column(Integer, primary_key=True, index=True)
    source_institution_id = Column(
        Integer, ForeignKey("institutions.id"), nullable=False, index=True
    )
    target_institution_id = Column(
        Integer, ForeignKey("institutions.id"), nullable=False, index=True
    )
    source_course_code = Column(String, nullable=False, index=True)
    source_course_title = Column(String, nullable=True)
    source_credits = Column(Integer, nullable=True)
    target_course_code = Column(String, nullable=False, index=True)
    target_course_title = Column(String, nullable=True)
    target_credits = Column(Integer, nullable=True)
    equivalency_type = Column(String, nullable=False, default="direct")
    minimum_grade = Column(String, nullable=True)
    catalog_year_start = Column(String, nullable=True)
    catalog_year_end = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft", index=True)
    source_reference = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    source_institution = relationship(
        "Institution",
        foreign_keys=[source_institution_id],
        back_populates="outgoing_equivalencies",
    )
    target_institution = relationship(
        "Institution",
        foreign_keys=[target_institution_id],
        back_populates="incoming_equivalencies",
    )

    __table_args__ = (
        UniqueConstraint(
            "source_institution_id",
            "source_course_code",
            "target_institution_id",
            "target_course_code",
            name="uq_directional_course_equivalency",
        ),
    )


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)

    institution = relationship("Institution", back_populates="departments")
    programs = relationship("Program", back_populates="department")

    __table_args__ = (
        UniqueConstraint("institution_id", "code", name="uq_department_institution_code"),
    )


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    degree_type = Column(String, nullable=True)
    catalog_year = Column(String, nullable=True)

    department = relationship("Department", back_populates="programs")
    courses = relationship("ProgramCourse", back_populates="program")

    __table_args__ = (
        UniqueConstraint("department_id", "code", "catalog_year", name="uq_program_code_year"),
    )


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    # ``code`` remains the unique storage key for backwards compatibility.
    # When two campuses use the same catalog code, the later row is stored as
    # ``CAMPUS::CODE`` and ``catalog_code`` is the student-facing value.
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True, index=True)
    code = Column(String, nullable=False, unique=True)
    catalog_code = Column(String, nullable=True, index=True)
    title = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    choice_group_code = Column(String, nullable=True)

    program_links = relationship("ProgramCourse", back_populates="course")
    institution = relationship("Institution", back_populates="courses")

    @property
    def display_code(self):
        return self.catalog_code or self.code.split("::", 1)[-1]

    __table_args__ = (
        UniqueConstraint("institution_id", "catalog_code", name="uq_course_institution_catalog_code"),
    )


class ProgramCourse(Base):
    __tablename__ = "program_courses"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    requirement_type = Column(String, default="required")

    program = relationship("Program", back_populates="courses")
    course = relationship("Course", back_populates="program_links")

    __table_args__ = (
        UniqueConstraint("program_id", "course_id", name="uq_program_course"),
    )


class CoursePrerequisite(Base):
    __tablename__ = "course_prerequisites"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    prereq_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # AND group = separate requirements
    # OR group = alternatives inside same group
    group_id = Column(Integer, default=1)

    __table_args__ = (
        UniqueConstraint(
            "program_id",
            "course_id",
            "prereq_course_id",
            "group_id",
            name="uq_prereq"
        ),
    )


class CourseRequirementGroupPrerequisite(Base):
    __tablename__ = "course_requirement_group_prerequisites"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    requirement_group_id = Column(Integer, ForeignKey("requirement_groups.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "program_id",
            "course_id",
            "requirement_group_id",
            name="uq_course_requirement_group_prerequisite",
        ),
    )


class CourseAlternative(Base):
    __tablename__ = "course_alternatives"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    alternative_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "program_id",
            "course_id",
            "alternative_course_id",
            name="uq_alternative"
        ),
    )


class FAQEntry(Base):
    __tablename__ = "faq_entries"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    intent = Column(String, nullable=True)

class RequirementGroup(Base):
    __tablename__ = "requirement_groups"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)

    name = Column(String, nullable=False)
    group_type = Column(String, nullable=False)

    required_credits = Column(Integer, nullable=True)
    required_course_count = Column(Integer, nullable=True)
    display_order = Column(Integer, default=0)
    completion_options = Column(Text, nullable=True)
    required_course_sets = Column(Text, nullable=True)
    required_course_set_count = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("program_id", "name", name="uq_program_requirement_group"),
    )


class RequirementGroupCourse(Base):
    __tablename__ = "requirement_group_courses"

    id = Column(Integer, primary_key=True, index=True)
    requirement_group_id = Column(Integer, ForeignKey("requirement_groups.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("requirement_group_id", "course_id", name="uq_group_course"),
    )


class ChoiceGroup(Base):
    __tablename__ = "choice_groups"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    group_type = Column(String, nullable=False)
    required_credits = Column(Integer, nullable=True)
    required_course_count = Column(Integer, nullable=True)
    advising_note = Column(String, nullable=True)
    source = Column(String, nullable=True)

    institution = relationship("Institution", back_populates="choice_groups")
    course_links = relationship("ChoiceGroupCourse", back_populates="choice_group")

    __table_args__ = (
        UniqueConstraint("institution_id", "code", name="uq_choice_group_institution_code"),
    )


class ChoiceGroupCourse(Base):
    __tablename__ = "choice_group_courses"

    id = Column(Integer, primary_key=True, index=True)
    choice_group_id = Column(Integer, ForeignKey("choice_groups.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    choice_group = relationship("ChoiceGroup", back_populates="course_links")
    course = relationship("Course")

    __table_args__ = (
        UniqueConstraint("choice_group_id", "course_id", name="uq_choice_group_course"),
    )


class CurriculumDraft(Base):
    """Editable major-constructor document, kept separate from published curricula."""

    __tablename__ = "curriculum_drafts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, default="Untitled program")
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    status = Column(String, nullable=False, default="draft", index=True)
    document_json = Column(Text, nullable=False, default="{}")
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    published_program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)

    versions = relationship(
        "CurriculumDraftVersion",
        back_populates="draft",
        cascade="all, delete-orphan",
        order_by="CurriculumDraftVersion.version_number",
    )


class CurriculumDraftVersion(Base):
    """Immutable snapshot used for review, publication, and rollback."""

    __tablename__ = "curriculum_draft_versions"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("curriculum_drafts.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    document_json = Column(Text, nullable=False)
    note = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    draft = relationship("CurriculumDraft", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("draft_id", "version_number", name="uq_curriculum_draft_version"),
    )
