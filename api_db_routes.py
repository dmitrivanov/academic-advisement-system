from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
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
    RequirementGroup,
    RequirementGroupCourse,
    ChoiceGroup,
    ChoiceGroupCourse,
)


router = APIRouter(prefix="/api/db", tags=["database"])


class InstitutionPayload(BaseModel):
    code: str
    name: str
    system: str = "CUNY"
    borough: Optional[str] = None
    website: Optional[str] = None


@router.get("/health")
def db_health(db: Session = Depends(get_db)):
    return {
        "status": "ok",
        "institutions": db.query(Institution).count(),
        "departments": db.query(Department).count(),
        "programs": db.query(Program).count(),
        "courses": db.query(Course).count(),
        "choice_groups": db.query(ChoiceGroup).count(),
    }


@router.get("/institutions")
def get_institutions(db: Session = Depends(get_db)):
    institutions = db.query(Institution).order_by(Institution.name).all()

    return [
        {
            "id": i.id,
            "code": i.code,
            "name": i.name,
            "system": i.system,
            "borough": i.borough,
            "website": i.website,
        }
        for i in institutions
    ]


@router.post("/institutions")
def create_institution(payload: InstitutionPayload, db: Session = Depends(get_db)):
    code = payload.code.strip().upper()
    name = payload.name.strip()

    if db.query(Institution).filter_by(code=code).first():
        raise HTTPException(status_code=400, detail="Institution code already exists")

    if db.query(Institution).filter_by(name=name).first():
        raise HTTPException(status_code=400, detail="Institution name already exists")

    institution = Institution(
        code=code,
        name=name,
        system=payload.system.strip() if payload.system else "CUNY",
        borough=payload.borough,
        website=payload.website,
    )

    db.add(institution)
    db.commit()
    db.refresh(institution)

    return {"status": "created", "id": institution.id}


@router.put("/institutions/{institution_id}")
def update_institution(
    institution_id: int,
    payload: InstitutionPayload,
    db: Session = Depends(get_db),
):
    institution = db.query(Institution).filter_by(id=institution_id).first()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    code = payload.code.strip().upper()
    name = payload.name.strip()

    duplicate_code = (
        db.query(Institution)
        .filter(Institution.code == code, Institution.id != institution_id)
        .first()
    )
    if duplicate_code:
        raise HTTPException(status_code=400, detail="Institution code already exists")

    duplicate_name = (
        db.query(Institution)
        .filter(Institution.name == name, Institution.id != institution_id)
        .first()
    )
    if duplicate_name:
        raise HTTPException(status_code=400, detail="Institution name already exists")

    institution.code = code
    institution.name = name
    institution.system = payload.system.strip() if payload.system else "CUNY"
    institution.borough = payload.borough
    institution.website = payload.website

    db.commit()
    db.refresh(institution)

    return {"status": "updated", "id": institution.id}


@router.delete("/institutions/{institution_id}")
def delete_institution(institution_id: int, db: Session = Depends(get_db)):
    institution = db.query(Institution).filter_by(id=institution_id).first()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    department_count = db.query(Department).filter_by(
        institution_id=institution.id
    ).count()

    if department_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete institution with departments attached",
        )

    db.delete(institution)
    db.commit()

    return {"status": "deleted", "id": institution_id}


@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    departments = db.query(Department).order_by(Department.name).all()

    return [
        {
            "id": d.id,
            "code": d.code,
            "name": d.name,
            "institution": d.institution.name,
            "institution_code": d.institution.code,
        }
        for d in departments
    ]


@router.get("/programs")
def get_programs(db: Session = Depends(get_db)):
    programs = db.query(Program).order_by(Program.name).all()

    # Calculate curriculum availability in two aggregate queries instead of
    # making one requirements request for every program in the frontend.
    requirement_course_counts = dict(
        db.query(
            RequirementGroup.program_id,
            func.count(RequirementGroupCourse.id),
        )
        .outerjoin(
            RequirementGroupCourse,
            RequirementGroupCourse.requirement_group_id == RequirementGroup.id,
        )
        .group_by(RequirementGroup.program_id)
        .all()
    )

    legacy_program_course_counts = dict(
        db.query(
            ProgramCourse.program_id,
            func.count(ProgramCourse.id),
        )
        .group_by(ProgramCourse.program_id)
        .all()
    )

    result = []

    for program in programs:
        requirement_count = int(requirement_course_counts.get(program.id, 0) or 0)
        legacy_count = int(legacy_program_course_counts.get(program.id, 0) or 0)

        # New-format curricula use requirement groups. The legacy count is a
        # fallback for older curriculum CSVs that still populate ProgramCourse.
        course_count = requirement_count if requirement_count > 0 else legacy_count

        result.append({
            "id": program.id,
            "code": program.code,
            "name": program.name,
            "degree_type": program.degree_type,
            "catalog_year": program.catalog_year,
            "department": program.department.name,
            "department_code": program.department.code,
            "institution": program.department.institution.name,
            "institution_code": program.department.institution.code,
            "course_count": course_count,
            "has_curriculum": course_count > 0,
        })

    return result


@router.get("/courses")
def get_all_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).order_by(Course.code).all()

    return [
        {
            "id": c.id,
            "code": c.code,
            "title": c.title,
            "credits": c.credits,
            "choice_group_code": c.choice_group_code,
        }
        for c in courses
    ]


@router.get("/requirement-groups")
def get_all_requirement_groups(db: Session = Depends(get_db)):
    groups = db.query(RequirementGroup).order_by(
        RequirementGroup.display_order
    ).all()

    result = []

    for g in groups:
        program = db.query(Program).filter_by(id=g.program_id).first()

        result.append({
            "id": g.id,
            "program": program.code if program else None,
            "program_name": program.name if program else None,
            "institution": program.department.institution.name if program else None,
            "institution_code": program.department.institution.code if program else None,
            "name": g.name,
            "group_type": g.group_type,
            "required_credits": g.required_credits,
            "required_course_count": g.required_course_count,
            "display_order": g.display_order,
        })

    return result


@router.get("/choice-groups")
def get_choice_groups(db: Session = Depends(get_db)):
    groups = db.query(ChoiceGroup).order_by(ChoiceGroup.code).all()

    return [
        {
            "id": g.id,
            "code": g.code,
            "name": g.name,
            "group_type": g.group_type,
            "required_credits": g.required_credits,
            "required_course_count": g.required_course_count,
            "institution": g.institution.name,
            "institution_code": g.institution.code,
        }
        for g in groups
    ]


@router.get("/choice-groups/{group_code}/courses")
def get_choice_group_courses(
    group_code: str,
    institution_code: str = "BMCC",
    db: Session = Depends(get_db),
):
    institution = db.query(Institution).filter_by(
        code=institution_code.strip().upper()
    ).first()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    group = db.query(ChoiceGroup).filter_by(
        institution_id=institution.id,
        code=group_code.strip().upper(),
    ).first()

    if not group:
        raise HTTPException(status_code=404, detail="Choice group not found")

    links = db.query(ChoiceGroupCourse).filter_by(choice_group_id=group.id).all()

    courses = []
    for link in links:
        course = db.query(Course).filter_by(id=link.course_id).first()
        if not course:
            continue

        courses.append({
            "id": course.id,
            "code": course.code,
            "title": course.title,
            "credits": course.credits,
        })

    courses.sort(key=lambda c: c["code"])

    return {
        "group": {
            "id": group.id,
            "code": group.code,
            "name": group.name,
            "group_type": group.group_type,
            "required_credits": group.required_credits,
            "required_course_count": group.required_course_count,
            "institution": institution.name,
            "institution_code": institution.code,
        },
        "courses": courses,
    }


def build_course_payload(db: Session, program_id: int, course: Course):
    prereq_rows = (
        db.query(CoursePrerequisite)
        .filter_by(program_id=program_id, course_id=course.id)
        .all()
    )

    alt_rows = (
        db.query(CourseAlternative)
        .filter_by(program_id=program_id, course_id=course.id)
        .all()
    )

    prereq_groups = {}

    for row in prereq_rows:
        prereq_course = db.query(Course).filter_by(id=row.prereq_course_id).first()
        if prereq_course:
            prereq_groups.setdefault(row.group_id, []).append(prereq_course.code)

    prereqs = []
    for _, codes in sorted(prereq_groups.items()):
        prereqs.append(codes[0] if len(codes) == 1 else codes)

    alternatives = []
    for row in alt_rows:
        alt_course = db.query(Course).filter_by(id=row.alternative_course_id).first()
        if alt_course:
            alternatives.append(alt_course.code)

    return {
        "code": course.code,
        "title": course.title,
        "credits": course.credits,
        "choice_group_code": course.choice_group_code,
        "prereqs": prereqs,
        "alternatives": alternatives,
    }


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
            "degree_type": program.degree_type,
            "department": program.department.name,
            "institution": program.department.institution.name,
            "institution_code": program.department.institution.code,
        },
        "courses": [
            {
                "code": link.course.code,
                "title": link.course.title,
                "credits": link.course.credits,
                "choice_group_code": link.course.choice_group_code,
                "requirement_type": link.requirement_type,
            }
            for link in links
        ],
    }


@router.get("/programs/{program_code}/graph")
def get_program_graph(program_code: str, db: Session = Depends(get_db)):
    program = db.query(Program).filter_by(code=program_code).first()

    if not program:
        return {"error": "Program not found"}

    links = db.query(ProgramCourse).filter_by(program_id=program.id).all()

    courses = {}
    for link in links:
        courses[link.course.code] = build_course_payload(db, program.id, link.course)

    return {
        "program": {
            "code": program.code,
            "name": program.name,
            "catalog_year": program.catalog_year,
            "degree_type": program.degree_type,
            "department": program.department.name,
            "institution": program.department.institution.name,
            "institution_code": program.department.institution.code,
        },
        "courses": courses,
    }


@router.get("/programs/{program_code}/requirements")
def get_program_requirements(program_code: str, db: Session = Depends(get_db)):
    program = db.query(Program).filter_by(code=program_code).first()

    if not program:
        return {"error": "Program not found"}

    groups = (
        db.query(RequirementGroup)
        .filter_by(program_id=program.id)
        .order_by(RequirementGroup.display_order)
        .all()
    )

    result_groups = []

    for group in groups:
        group_courses = (
            db.query(RequirementGroupCourse)
            .filter_by(requirement_group_id=group.id)
            .all()
        )

        courses = []
        for group_course in group_courses:
            course = db.query(Course).filter_by(id=group_course.course_id).first()
            if not course:
                continue

            courses.append(build_course_payload(db, program.id, course))

        result_groups.append({
            "id": group.id,
            "name": group.name,
            "group_type": group.group_type,
            "required_credits": group.required_credits,
            "required_course_count": group.required_course_count,
            "display_order": group.display_order,
            "courses": courses,
        })

    return {
        "program": {
            "code": program.code,
            "name": program.name,
            "catalog_year": program.catalog_year,
            "degree_type": program.degree_type,
            "department": program.department.name,
            "institution": program.department.institution.name,
            "institution_code": program.department.institution.code,
        },
        "groups": result_groups,
    }
