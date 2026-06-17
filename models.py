from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
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
    code = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)

    program_links = relationship("ProgramCourse", back_populates="course")


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