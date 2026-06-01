from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Institution,
    Department,
    Program,
    Course,
    ProgramCourse,
    CoursePrerequisite,
    CourseAlternative,
)

router = APIRouter(prefix="/api/db", tags=["database"])


@router.get("/health")
def db_health(db: Session = Depends(get_db)):
    programs = db.query(Program).count()
    courses = db.query(Course).count()

    return {
        "status": "ok",
        "programs": programs,
        "courses": courses,
    }


@router.get("/programs")
def get_programs(db: Session = Depends(get_db)):
    programs = db.query(Program).all()

    return [
        {
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "degree_type": p.degree_type,
            "catalog_year": p.catalog_year,
            "department": p.department.name,
        }
        for p in programs
    ]


@router.get("/programs/{program_code}/courses")
def get_program_courses(program_code: str, db: Session = Depends(get_db)):
    program = db.query(Program).filter_by(code=program_code).first()

    if not program:
        return {"error": "Program not found"}

    links = db.query(ProgramCourse).filter_by(program_id=program.id).all()

    return {
        "program": {
            "code": program.code,
            "name": program.name,
            "catalog_year": program.catalog_year,
        },
        "courses": [
            {
                "code": link.course.code,
                "title": link.course.title,
                "credits": link.course.credits,
                "requirement_type": link.requirement_type,
            }
            for link in links
        ]
    }


@router.get("/programs/{program_code}/graph")
def get_program_graph(program_code: str, db: Session = Depends(get_db)):
    program = db.query(Program).filter_by(code=program_code).first()

    if not program:
        return {"error": "Program not found"}

    links = db.query(ProgramCourse).filter_by(program_id=program.id).all()

    courses = {}

    for link in links:
        c = link.course

        prereq_rows = (
            db.query(CoursePrerequisite)
            .filter_by(program_id=program.id, course_id=c.id)
            .all()
        )

        alt_rows = (
            db.query(CourseAlternative)
            .filter_by(program_id=program.id, course_id=c.id)
            .all()
        )

        groups = {}

        for row in prereq_rows:
            prereq_course = db.query(Course).filter_by(id=row.prereq_course_id).first()
            groups.setdefault(row.group_id, []).append(prereq_course.code)

        prereqs = []

        for _, codes in sorted(groups.items()):
            if len(codes) == 1:
                prereqs.append(codes[0])
            else:
                prereqs.append(codes)

        alternatives = []

        for row in alt_rows:
            alt_course = db.query(Course).filter_by(id=row.alternative_course_id).first()
            alternatives.append(alt_course.code)

        courses[c.code] = {
            "title": c.title,
            "credits": c.credits,
            "prereqs": prereqs,
            "alternatives": alternatives,
        }

    return {
        "program": {
            "code": program.code,
            "name": program.name,
            "catalog_year": program.catalog_year,
        },
        "courses": courses,
    }


@router.get("/institutions")
def get_institutions(db: Session = Depends(get_db)):
    institutions = db.query(Institution).all()

    return [
        {
            "id": i.id,
            "name": i.name,
        }
        for i in institutions
    ]


@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    departments = db.query(Department).all()

    return [
        {
            "id": d.id,
            "code": d.code,
            "name": d.name,
            "institution": d.institution.name,
        }
        for d in departments
    ]
