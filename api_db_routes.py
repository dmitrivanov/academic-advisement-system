import json
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
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
    CurriculumDraft,
    CurriculumDraftVersion,
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


class CurriculumDraftPayload(BaseModel):
    name: str = "Untitled program"
    institution_id: Optional[int] = None
    department_id: Optional[int] = None
    document: dict[str, Any] = Field(default_factory=dict)


class DraftStatusPayload(BaseModel):
    status: str
    note: Optional[str] = None


def require_admin(request: Request):
    if request.session.get("logged_in") is not True:
        raise HTTPException(status_code=401, detail="Admin login required")


def optional_text(value):
    return value.strip() if value and value.strip() else None


def normalize_course_code(value: str):
    return " ".join(value.strip().upper().split())


def serialize_draft(draft: CurriculumDraft, include_document: bool = True):
    result = {
        "id": draft.id,
        "name": draft.name,
        "institution_id": draft.institution_id,
        "department_id": draft.department_id,
        "status": draft.status,
        "created_by": draft.created_by,
        "created_at": draft.created_at.isoformat() if draft.created_at else None,
        "updated_at": draft.updated_at.isoformat() if draft.updated_at else None,
        "published_program_id": draft.published_program_id,
        "version_count": len(draft.versions),
    }
    if include_document:
        result["document"] = json.loads(draft.document_json or "{}")
    return result


def validate_draft_references(payload: CurriculumDraftPayload, db: Session):
    if payload.institution_id and not db.query(Institution).filter_by(id=payload.institution_id).first():
        raise HTTPException(status_code=400, detail="Institution not found")
    if payload.department_id:
        department = db.query(Department).filter_by(id=payload.department_id).first()
        if not department:
            raise HTTPException(status_code=400, detail="Department not found")
        if payload.institution_id and department.institution_id != payload.institution_id:
            raise HTTPException(status_code=400, detail="Department does not belong to the selected institution")


def curriculum_validation(draft: CurriculumDraft, db: Session):
    document = json.loads(draft.document_json or "{}")
    metadata = document.get("metadata") or {}
    concentrations = document.get("concentrations") or []
    errors, warnings = [], []
    if not draft.institution_id:
        errors.append("Select a campus.")
    if not draft.department_id:
        errors.append("Select a department.")
    if not draft.name.strip() or draft.name == "Untitled program":
        errors.append("Enter a program name.")
    for field, label in (("code", "program code"), ("degree_type", "degree type"), ("catalog_year", "catalog year"), ("source_url", "official source URL")):
        if not str(metadata.get(field) or "").strip():
            errors.append(f"Enter the {label}.")
    if not concentrations:
        errors.append("Add at least one concentration.")
    known_ids = {row[0] for row in db.query(Course.id).all()}
    for index, concentration in enumerate(concentrations, 1):
        name = str(concentration.get("name") or "").strip()
        if not name:
            errors.append(f"Concentration {index} needs a name.")
        bins = concentration.get("bins") or {}
        selected = []
        for key in ("major_required", "major_electives", "common_core", "flex_core"):
            values = bins.get(key) or []
            selected.extend(values)
            missing = [course_id for course_id in values if course_id not in known_ids]
            if missing:
                errors.append(f"{name or f'Concentration {index}'} references missing course IDs: {missing}.")
            requirement = (concentration.get("bin_requirements") or {}).get(key) or {}
            if requirement.get("required_course_count") and requirement["required_course_count"] > len(values):
                errors.append(f"{name or f'Concentration {index}'} requires more courses in {key} than it provides.")
        if not selected:
            errors.append(f"{name or f'Concentration {index}'} has no curriculum courses.")
        duplicates = sorted({course_id for course_id in selected if selected.count(course_id) > 1})
        if duplicates:
            warnings.append(f"{name or f'Concentration {index}'} uses {len(duplicates)} course(s) in multiple bins; completion will be synchronized.")
    rules = document.get("rules") or {}
    for rule_type in ("alternatives", "prerequisites"):
        for rule in rules.get(rule_type) or []:
            ids = [value for value in rule.values() if isinstance(value, int)]
            if any(course_id not in known_ids for course_id in ids):
                errors.append(f"A {rule_type[:-1]} rule references a missing course.")
    placeholder_ids = []
    for pool in rules.get("elective_pools") or []:
        if not str(pool.get("name") or "").strip():
            errors.append("An elective pool is missing its name.")
        if not (pool.get("required_credits") or pool.get("required_course_count")):
            errors.append(f"Elective pool {pool.get('name') or ''} needs a credit or course requirement.")
        if not pool.get("course_ids"):
            errors.append(f"Elective pool {pool.get('name') or ''} has no course options.")
        if any(course_id not in known_ids for course_id in pool.get("course_ids") or []):
            errors.append(f"Elective pool {pool.get('name') or ''} references a missing course.")
    for adjustment in rules.get("core_adjustments") or []:
        placeholder_id = adjustment.get("placeholder_course_id")
        placeholder_ids.append(placeholder_id)
        if placeholder_id not in known_ids:
            errors.append("A Core adjustment references a missing placeholder course.")
        concentration_index = adjustment.get("concentration_index", 0)
        if concentration_index < 0 or concentration_index >= len(concentrations):
            errors.append("A Core adjustment references a missing concentration.")
        elif placeholder_id not in [course_id for values in (concentrations[concentration_index].get("bins") or {}).values() for course_id in values]:
            errors.append("A Core adjustment placeholder must also be placed in a curriculum bin.")
        adjusted_ids = (adjustment.get("include_course_ids") or []) + (adjustment.get("exclude_course_ids") or [])
        if any(course_id not in known_ids for course_id in adjusted_ids):
            errors.append("A Core adjustment references a missing included or excluded course.")
        institution = db.query(Institution).filter_by(id=draft.institution_id).first() if draft.institution_id else None
        base_group = db.query(ChoiceGroup).filter_by(
            institution_id=institution.id if institution else None,
            code=adjustment.get("base_group_code"),
        ).first() if institution else None
        if not base_group:
            errors.append(f"Core adjustment base group {adjustment.get('base_group_code') or '(missing)'} does not exist for this campus.")
        if not str(adjustment.get("note") or "").strip():
            errors.append("A Core adjustment is missing its student-facing note.")
    repeated_placeholders = {course_id for course_id in placeholder_ids if course_id and placeholder_ids.count(course_id) > 1}
    if repeated_placeholders:
        errors.append("Each Core adjustment must use a unique placeholder course.")
    return {"valid": not errors, "errors": errors, "warnings": warnings}


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
        "curriculum_drafts": db.query(CurriculumDraft).count(),
    }


@router.get("/curriculum-drafts")
def list_curriculum_drafts(_admin=Depends(require_admin), db: Session = Depends(get_db)):
    drafts = db.query(CurriculumDraft).order_by(CurriculumDraft.updated_at.desc()).all()
    return [serialize_draft(draft, include_document=False) for draft in drafts]


@router.post("/curriculum-drafts")
def create_curriculum_draft(
    payload: CurriculumDraftPayload,
    request: Request,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    validate_draft_references(payload, db)
    now = datetime.now(timezone.utc)
    draft = CurriculumDraft(
        name=payload.name.strip() or "Untitled program",
        institution_id=payload.institution_id,
        department_id=payload.department_id,
        document_json=json.dumps(payload.document),
        created_by=request.session.get("username"),
        created_at=now,
        updated_at=now,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return serialize_draft(draft)


@router.get("/curriculum-drafts/{draft_id}")
def get_curriculum_draft(draft_id: int, _admin=Depends(require_admin), db: Session = Depends(get_db)):
    draft = db.query(CurriculumDraft).filter_by(id=draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Curriculum draft not found")
    result = serialize_draft(draft)
    result["versions"] = [
        {
            "id": version.id,
            "version_number": version.version_number,
            "note": version.note,
            "created_by": version.created_by,
            "created_at": version.created_at.isoformat() if version.created_at else None,
        }
        for version in draft.versions
    ]
    return result


@router.put("/curriculum-drafts/{draft_id}")
def update_curriculum_draft(
    draft_id: int,
    payload: CurriculumDraftPayload,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    draft = db.query(CurriculumDraft).filter_by(id=draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Curriculum draft not found")
    if draft.status not in {"draft", "changes_requested"}:
        raise HTTPException(status_code=409, detail="Only editable drafts can be changed")
    validate_draft_references(payload, db)
    draft.name = payload.name.strip() or "Untitled program"
    draft.institution_id = payload.institution_id
    draft.department_id = payload.department_id
    draft.document_json = json.dumps(payload.document)
    draft.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(draft)
    return serialize_draft(draft)


@router.delete("/curriculum-drafts/{draft_id}")
def delete_curriculum_draft(
    draft_id: int,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    draft = db.query(CurriculumDraft).filter_by(id=draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Curriculum draft not found")
    if draft.status == "published":
        raise HTTPException(status_code=409, detail="Published curriculum history cannot be deleted")
    db.delete(draft)
    db.commit()
    return {"status": "deleted", "id": draft_id}


@router.post("/curriculum-drafts/{draft_id}/versions")
def snapshot_curriculum_draft(
    draft_id: int,
    request: Request,
    note: Optional[str] = None,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    draft = db.query(CurriculumDraft).filter_by(id=draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Curriculum draft not found")
    latest = db.query(func.max(CurriculumDraftVersion.version_number)).filter_by(draft_id=draft_id).scalar() or 0
    version = CurriculumDraftVersion(
        draft_id=draft.id,
        version_number=latest + 1,
        document_json=draft.document_json,
        note=optional_text(note),
        created_by=request.session.get("username"),
    )
    db.add(version)
    db.commit()
    return {"id": version.id, "version_number": version.version_number}


@router.post("/curriculum-drafts/{draft_id}/status")
def transition_curriculum_draft(
    draft_id: int,
    payload: DraftStatusPayload,
    request: Request,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    draft = db.query(CurriculumDraft).filter_by(id=draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Curriculum draft not found")
    allowed = {
        "draft": {"in_review"},
        "changes_requested": {"in_review"},
        "in_review": {"approved", "changes_requested"},
        "approved": {"draft"},
    }
    target = payload.status.strip().lower()
    if target not in allowed.get(draft.status, set()):
        raise HTTPException(status_code=409, detail=f"Cannot move {draft.status} to {target}")
    latest = db.query(func.max(CurriculumDraftVersion.version_number)).filter_by(draft_id=draft_id).scalar() or 0
    db.add(CurriculumDraftVersion(
        draft_id=draft.id,
        version_number=latest + 1,
        document_json=draft.document_json,
        note=optional_text(payload.note) or f"Status changed to {target}",
        created_by=request.session.get("username"),
    ))
    draft.status = target
    draft.updated_at = datetime.now(timezone.utc)
    db.commit()
    return serialize_draft(draft, include_document=False)


@router.get("/curriculum-drafts/{draft_id}/validate")
def validate_curriculum_draft(draft_id: int, _admin=Depends(require_admin), db: Session = Depends(get_db)):
    draft = db.query(CurriculumDraft).filter_by(id=draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Curriculum draft not found")
    return curriculum_validation(draft, db)


@router.post("/curriculum-drafts/{draft_id}/versions/{version_number}/restore")
def restore_curriculum_version(
    draft_id: int,
    version_number: int,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    draft = db.query(CurriculumDraft).filter_by(id=draft_id).first()
    version = db.query(CurriculumDraftVersion).filter_by(draft_id=draft_id, version_number=version_number).first()
    if not draft or not version:
        raise HTTPException(status_code=404, detail="Draft version not found")
    if draft.status == "published":
        raise HTTPException(status_code=409, detail="Published records are immutable; create a new draft to revise them")
    draft.document_json = version.document_json
    draft.status = "draft"
    draft.updated_at = datetime.now(timezone.utc)
    db.commit()
    return serialize_draft(draft)


@router.post("/curriculum-drafts/{draft_id}/publish")
def publish_curriculum_draft(
    draft_id: int,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    draft = db.query(CurriculumDraft).filter_by(id=draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Curriculum draft not found")
    if draft.status != "approved":
        raise HTTPException(status_code=409, detail="Only an approved curriculum can be published")
    validation = curriculum_validation(draft, db)
    if not validation["valid"]:
        raise HTTPException(status_code=422, detail={"message": "Validation failed", **validation})
    document = json.loads(draft.document_json)
    metadata = document["metadata"]
    concentrations = document["concentrations"]
    created_ids = []
    try:
        for index, concentration in enumerate(concentrations):
            suffix = "" if len(concentrations) == 1 else f"-{index + 1}"
            code = f"{metadata['code']}{suffix}"
            duplicate = db.query(Program).filter_by(
                department_id=draft.department_id,
                code=code,
                catalog_year=metadata["catalog_year"],
            ).first()
            if duplicate:
                raise HTTPException(status_code=409, detail=f"Program {code} for this catalog year already exists")
            program_name = draft.name if len(concentrations) == 1 else f"{draft.name} - {concentration['name']}"
            program = Program(department_id=draft.department_id, code=code, name=program_name, degree_type=metadata["degree_type"], catalog_year=metadata["catalog_year"])
            db.add(program)
            db.flush()
            created_ids.append(program.id)
            for order, (key, label, group_type) in enumerate((
                ("major_required", "Major Requirements", "major_required"),
                ("major_electives", "Major Electives", "major_elective"),
                ("common_core", "Common Core", "common_core"),
                ("flex_core", "Flexible Core", "flex_core"),
            )):
                course_ids = concentration.get("bins", {}).get(key) or []
                if not course_ids:
                    continue
                requirement = concentration.get("bin_requirements", {}).get(key, {})
                group = RequirementGroup(
                    program_id=program.id,
                    name=label,
                    group_type=group_type,
                    required_credits=requirement.get("required_credits"),
                    required_course_count=requirement.get("required_course_count"),
                    display_order=order,
                )
                db.add(group)
                db.flush()
                for course_id in course_ids:
                    db.add(RequirementGroupCourse(requirement_group_id=group.id, course_id=course_id))
            rules = document.get("rules") or {}
            for rule in rules.get("alternatives") or []:
                db.add(CourseAlternative(
                    program_id=program.id,
                    course_id=rule["course_id"],
                    alternative_course_id=rule["alternative_course_id"],
                ))
            for rule in rules.get("prerequisites") or []:
                db.add(CoursePrerequisite(
                    program_id=program.id,
                    course_id=rule["course_id"],
                    prereq_course_id=rule["prerequisite_course_id"],
                    group_id=rule.get("group_id", 1),
                ))
            for pool_index, pool in enumerate(rules.get("elective_pools") or []):
                if pool.get("concentration_index", 0) != index:
                    continue
                pool_group = RequirementGroup(
                    program_id=program.id,
                    name=pool["name"],
                    group_type=pool.get("bin", "major_electives"),
                    required_credits=pool.get("required_credits"),
                    required_course_count=pool.get("required_course_count"),
                    display_order=10 + pool_index,
                )
                db.add(pool_group)
                db.flush()
                for course_id in pool["course_ids"]:
                    db.add(RequirementGroupCourse(requirement_group_id=pool_group.id, course_id=course_id))
            for adjustment_index, adjustment in enumerate(rules.get("core_adjustments") or []):
                if adjustment.get("concentration_index", 0) != index:
                    continue
                base_group = db.query(ChoiceGroup).filter_by(
                    institution_id=draft.institution_id,
                    code=adjustment["base_group_code"],
                ).first()
                base_ids = {
                    link.course_id
                    for link in db.query(ChoiceGroupCourse).filter_by(choice_group_id=base_group.id).all()
                }
                allowed_ids = set(adjustment.get("include_course_ids") or [])
                allowed_subjects = set(adjustment.get("include_subject_codes") or [])
                if allowed_ids or allowed_subjects:
                    subject_ids = {
                        course.id for course in db.query(Course).filter(Course.id.in_(base_ids)).all()
                        if course.code.split()[0].upper() in allowed_subjects
                    }
                    selected_ids = base_ids & (allowed_ids | subject_ids)
                else:
                    selected_ids = set(base_ids)
                selected_ids -= set(adjustment.get("exclude_course_ids") or [])
                if not selected_ids:
                    raise HTTPException(status_code=422, detail=f"Core adjustment {adjustment['base_group_code']} produces an empty course pool")
                derived_code = f"{code}-{adjustment['base_group_code']}".upper()
                derived = ChoiceGroup(
                    institution_id=draft.institution_id,
                    code=derived_code,
                    name=f"{base_group.name} - {program_name}",
                    group_type=base_group.group_type,
                    required_credits=adjustment.get("required_credits") if adjustment.get("required_credits") is not None else base_group.required_credits,
                    required_course_count=adjustment.get("required_course_count") if adjustment.get("required_course_count") is not None else base_group.required_course_count,
                    advising_note=adjustment["note"],
                    source=metadata["source_url"],
                )
                db.add(derived)
                db.flush()
                for course_id in sorted(selected_ids):
                    db.add(ChoiceGroupCourse(choice_group_id=derived.id, course_id=course_id))
                placeholder = db.query(Course).filter_by(id=adjustment["placeholder_course_id"]).first()
                placeholder.choice_group_code = derived_code
        draft.status = "published"
        draft.published_program_id = created_ids[0]
        draft.updated_at = datetime.now(timezone.utc)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
    return {"status": "published", "program_ids": created_ids}


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
    program_code: str | None = None,
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

    program = None
    if program_code:
        program = (
            db.query(Program)
            .join(Department, Program.department_id == Department.id)
            .filter(
                Department.institution_id == institution.id,
                Program.code == program_code.strip().upper(),
            )
            .first()
        )

    courses = []
    for link in links:
        course = db.query(Course).filter_by(id=link.course_id).first()
        if not course:
            continue

        payload = build_course_payload(db, program.id, course) if program else {
            "code": course.code,
            "title": course.title,
            "credits": course.credits,
            "choice_group_code": course.choice_group_code,
            "prereqs": [],
            "alternatives": [],
        }
        payload["id"] = course.id
        courses.append(payload)

    courses.sort(key=lambda c: c["code"])

    return {
        "group": {
            "id": group.id,
            "code": group.code,
            "name": group.name,
            "group_type": group.group_type,
            "required_credits": group.required_credits,
            "required_course_count": group.required_course_count,
            "advising_note": group.advising_note,
            "source": group.source,
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
