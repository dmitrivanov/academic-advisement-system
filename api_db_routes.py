from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
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
    CourseEquivalency,
)


router = APIRouter(prefix="/api/db", tags=["database"])


class InstitutionPayload(BaseModel):
    code: str
    name: str
    system: str = "CUNY"
    borough: Optional[str] = None
    website: Optional[str] = None


class CourseEquivalencyPayload(BaseModel):
    source_institution_id: int
    target_institution_id: int
    source_course_code: str
    source_course_title: Optional[str] = None
    source_credits: Optional[int] = None
    target_course_code: str
    target_course_title: Optional[str] = None
    target_credits: Optional[int] = None
    equivalency_type: str = "direct"
    minimum_grade: Optional[str] = None
    catalog_year_start: Optional[str] = None
    catalog_year_end: Optional[str] = None
    status: str = "draft"
    source_reference: Optional[str] = None
    notes: Optional[str] = None


def require_admin(request: Request):
    if request.session.get("logged_in") is not True:
        raise HTTPException(status_code=401, detail="Admin login required")


def optional_text(value):
    return value.strip() if value and value.strip() else None


def normalize_course_code(value: str):
    return " ".join(value.strip().upper().split())


def serialize_equivalency(rule: CourseEquivalency):
    return {
        "id": rule.id,
        "source_institution_id": rule.source_institution_id,
        "source_institution": rule.source_institution.name,
        "source_institution_code": rule.source_institution.code,
        "source_course_code": rule.source_course_code,
        "source_course_title": rule.source_course_title,
        "source_credits": rule.source_credits,
        "target_institution_id": rule.target_institution_id,
        "target_institution": rule.target_institution.name,
        "target_institution_code": rule.target_institution.code,
        "target_course_code": rule.target_course_code,
        "target_course_title": rule.target_course_title,
        "target_credits": rule.target_credits,
        "equivalency_type": rule.equivalency_type,
        "minimum_grade": rule.minimum_grade,
        "catalog_year_start": rule.catalog_year_start,
        "catalog_year_end": rule.catalog_year_end,
        "status": rule.status,
        "source_reference": rule.source_reference,
        "notes": rule.notes,
    }


def apply_equivalency_payload(
    rule: CourseEquivalency,
    payload: CourseEquivalencyPayload,
    db: Session,
    rule_id: Optional[int] = None,
):
    source = db.query(Institution).filter_by(id=payload.source_institution_id).first()
    target = db.query(Institution).filter_by(id=payload.target_institution_id).first()

    if not source or not target:
        raise HTTPException(status_code=400, detail="Source and target institutions are required")
    if source.id == target.id:
        raise HTTPException(status_code=400, detail="Source and target institutions must be different")

    source_code = normalize_course_code(payload.source_course_code)
    target_code = normalize_course_code(payload.target_course_code)
    if not source_code or not target_code:
        raise HTTPException(status_code=400, detail="Source and target course codes are required")

    status = payload.status.strip().lower()
    if status not in {"draft", "approved", "inactive"}:
        raise HTTPException(status_code=400, detail="Status must be draft, approved, or inactive")

    equivalency_type = payload.equivalency_type.strip().lower()
    if equivalency_type != "direct":
        raise HTTPException(
            status_code=400,
            detail="This version supports direct one-to-one equivalencies only",
        )

    duplicate_query = db.query(CourseEquivalency).filter_by(
        source_institution_id=source.id,
        source_course_code=source_code,
        target_institution_id=target.id,
        target_course_code=target_code,
    )
    if rule_id is not None:
        duplicate_query = duplicate_query.filter(CourseEquivalency.id != rule_id)
    if duplicate_query.first():
        raise HTTPException(status_code=400, detail="This directional equivalency already exists")

    rule.source_institution_id = source.id
    rule.target_institution_id = target.id
    rule.source_course_code = source_code
    rule.source_course_title = optional_text(payload.source_course_title)
    rule.source_credits = payload.source_credits
    rule.target_course_code = target_code
    rule.target_course_title = optional_text(payload.target_course_title)
    rule.target_credits = payload.target_credits
    rule.equivalency_type = equivalency_type
    rule.minimum_grade = optional_text(payload.minimum_grade)
    rule.catalog_year_start = optional_text(payload.catalog_year_start)
    rule.catalog_year_end = optional_text(payload.catalog_year_end)
    rule.status = status
    rule.source_reference = optional_text(payload.source_reference)
    rule.notes = optional_text(payload.notes)


@router.get("/health")
def db_health(db: Session = Depends(get_db)):
    return {
        "status": "ok",
        "institutions": db.query(Institution).count(),
        "departments": db.query(Department).count(),
        "programs": db.query(Program).count(),
        "courses": db.query(Course).count(),
        "choice_groups": db.query(ChoiceGroup).count(),
        "course_equivalencies": db.query(CourseEquivalency).count(),
    }


@router.get("/equivalencies")
def get_equivalencies(
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    rules = db.query(CourseEquivalency).order_by(
        CourseEquivalency.source_institution_id,
        CourseEquivalency.source_course_code,
        CourseEquivalency.target_institution_id,
        CourseEquivalency.target_course_code,
    ).all()
    return [serialize_equivalency(rule) for rule in rules]


@router.get("/equivalencies/matches")
def get_approved_equivalency_matches(
    source_institution_code: str,
    target_institution_code: str,
    db: Session = Depends(get_db),
):
    source_code = source_institution_code.strip().upper()
    target_code = target_institution_code.strip().upper()

    rules = (
        db.query(CourseEquivalency)
        .join(
            Institution,
            CourseEquivalency.source_institution_id == Institution.id,
        )
        .filter(
            Institution.code == source_code,
            CourseEquivalency.status == "approved",
        )
        .all()
    )

    return [
        serialize_equivalency(rule)
        for rule in rules
        if rule.target_institution.code == target_code
    ]


@router.post("/equivalencies")
def create_equivalency(
    payload: CourseEquivalencyPayload,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    rule = CourseEquivalency()
    apply_equivalency_payload(rule, payload, db)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return serialize_equivalency(rule)


@router.put("/equivalencies/{equivalency_id}")
def update_equivalency(
    equivalency_id: int,
    payload: CourseEquivalencyPayload,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    rule = db.query(CourseEquivalency).filter_by(id=equivalency_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Course equivalency not found")

    apply_equivalency_payload(rule, payload, db, rule_id=equivalency_id)
    db.commit()
    db.refresh(rule)
    return serialize_equivalency(rule)


@router.delete("/equivalencies/{equivalency_id}")
def deactivate_equivalency(
    equivalency_id: int,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    rule = db.query(CourseEquivalency).filter_by(id=equivalency_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Course equivalency not found")

    rule.status = "inactive"
    db.commit()
    return {"status": "inactive", "id": equivalency_id}


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
