from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey, UniqueConstraint
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

    Course codes stay on the rule because transfer equivalencies are directional
    catalog assertions, while Course records are keyed naturally by campus and
    code and use a numeric ID for relational stability.
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
    career_links = relationship("ProgramCareer", back_populates="program")
    cpl_guidance = relationship("ProgramCplGuidance", back_populates="program")

    __table_args__ = (
        UniqueConstraint("department_id", "code", "catalog_year", name="uq_program_code_year"),
    )


class Career(Base):
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    aliases = Column(Text, nullable=True)
    pathway_type = Column(String, nullable=False, default="career")
    source_title = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    reviewed_at = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False, default=True, index=True)

    skills = relationship("CareerSkill", back_populates="career", cascade="all, delete-orphan")
    program_links = relationship("ProgramCareer", back_populates="career", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=True, index=True)

    careers = relationship("CareerSkill", back_populates="skill", cascade="all, delete-orphan")


class CareerSkill(Base):
    __tablename__ = "career_skills"

    id = Column(Integer, primary_key=True)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False, index=True)

    career = relationship("Career", back_populates="skills")
    skill = relationship("Skill", back_populates="careers")

    __table_args__ = (UniqueConstraint("career_id", "skill_id", name="uq_career_skill"),)


class ProgramCareer(Base):
    __tablename__ = "program_careers"

    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    career_id = Column(Integer, ForeignKey("careers.id"), nullable=False, index=True)
    career_points = Column(Integer, nullable=False, default=50)
    evidence_level = Column(String, nullable=False, default="strong")
    explanation = Column(Text, nullable=False)
    source_title = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    official_program_url = Column(String, nullable=False)
    reviewed_at = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False, default=True, index=True)

    program = relationship("Program", back_populates="career_links")
    career = relationship("Career", back_populates="program_links")

    __table_args__ = (
        UniqueConstraint("program_id", "career_id", name="uq_program_career"),
    )


class CplType(Base):
    __tablename__ = "cpl_types"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    evidence_requested = Column(Text, nullable=False)
    next_step = Column(Text, nullable=False)
    official_url = Column(String, nullable=False)
    source_title = Column(String, nullable=False)
    reviewed_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="published", index=True)
    active = Column(Boolean, nullable=False, default=True, index=True)

    program_guidance = relationship("ProgramCplGuidance", back_populates="cpl_type")


class ProgramCplGuidance(Base):
    __tablename__ = "program_cpl_guidance"

    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    cpl_type_id = Column(Integer, ForeignKey("cpl_types.id"), nullable=False, index=True)
    guidance = Column(Text, nullable=False)
    evidence_requested = Column(Text, nullable=False)
    source_url = Column(String, nullable=False)
    reviewed_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="published", index=True)

    program = relationship("Program", back_populates="cpl_guidance")
    cpl_type = relationship("CplType", back_populates="program_guidance")

    __table_args__ = (
        UniqueConstraint("program_id", "cpl_type_id", name="uq_program_cpl_guidance"),
    )


class AcademicTerm(Base):
    __tablename__ = "academic_terms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False, default="cuny_global_search")
    provider_code = Column(String, nullable=False, unique=True, index=True)
    verified_at = Column(DateTime, nullable=False)
    source_url = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=False, index=True)


class ScheduleProviderConfig(Base):
    """Governance record for an optional official live-section provider."""
    __tablename__ = "schedule_provider_configs"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    enabled = Column(Boolean, nullable=False, default=False)
    approval_status = Column(String, nullable=False, default="not_approved", index=True)
    api_base_url = Column(String, nullable=True)
    data_owner = Column(String, nullable=True)
    permission_reference = Column(String, nullable=True)
    attribution = Column(String, nullable=True)
    support_contact = Column(String, nullable=True)
    refresh_seconds = Column(Integer, nullable=False, default=300)
    retention_seconds = Column(Integer, nullable=False, default=900)
    last_verified_at = Column(DateTime, nullable=True)
    updated_by = Column(String, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class TransferOption(Base):
    __tablename__ = "transfer_options"

    id = Column(Integer, primary_key=True, index=True)
    source_program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    target_institution = Column(String, nullable=False)
    target_program = Column(String, nullable=False)
    target_degree = Column(String, nullable=True)
    target_url = Column(String, nullable=False)
    explanation = Column(Text, nullable=False)
    source_url = Column(String, nullable=False)
    reviewed_at = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False, default=True, index=True)

    __table_args__ = (UniqueConstraint("source_program_id", "target_institution", "target_program", name="uq_transfer_option"),)


class GovernanceDraft(Base):
    __tablename__ = "governance_drafts"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(Integer, nullable=True, index=True)
    status = Column(String, nullable=False, default="draft", index=True)
    document_json = Column(Text, nullable=False, default="{}")
    source_url = Column(String, nullable=False)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    versions = relationship("GovernanceDraftVersion", back_populates="draft", cascade="all, delete-orphan")


class GovernanceDraftVersion(Base):
    __tablename__ = "governance_draft_versions"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("governance_drafts.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    document_json = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    changed_by = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    draft = relationship("GovernanceDraft", back_populates="versions")
    __table_args__ = (UniqueConstraint("draft_id", "version_number", name="uq_governance_draft_version"),)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True, index=True)
    code = Column(String, nullable=False)
    # Retained only to migrate databases created before campus-scoped codes.
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
        UniqueConstraint("institution_id", "code", name="uq_course_institution_code"),
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


class CurriculumGraphEdgeOverride(Base):
    """Reversible admin edits layered over canonical curriculum relationships."""

    __tablename__ = "curriculum_graph_edge_overrides"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    source_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    target_course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    relation_type = Column(String, nullable=False, default="prerequisite")
    action = Column(String, nullable=False, default="add")
    group_id = Column(Integer, nullable=False, default=1)
    note = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint(
            "program_id",
            "source_course_id",
            "target_course_id",
            "relation_type",
            "group_id",
            name="uq_curriculum_graph_override",
        ),
    )


class CurriculumGraphNodePosition(Base):
    """Administrator-saved visual placement for a course in one program tree."""

    __tablename__ = "curriculum_graph_node_positions"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    x = Column(Integer, nullable=False, default=0)
    y = Column(Integer, nullable=False, default=0)
    updated_by = Column(String, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("program_id", "course_id", name="uq_curriculum_graph_node_position"),
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
