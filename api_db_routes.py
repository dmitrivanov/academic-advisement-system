import csv
import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database import get_db
from auth import require_admin
from program_selector_logic import canonical_selector_programs
from cuny_beyond_matching import rank_program_matches, resolve_career
from schedule_link_service import build_global_search_handoff
from schedule_provider_service import build_section_fallback, validate_provider_config, provider_readiness
from models import (
    Institution,
    Department,
    Program,
    Course,
    ProgramCourse,
    CoursePrerequisite,
    CourseRequirementGroupPrerequisite,
    CourseAlternative,
    RequirementGroup,
    RequirementGroupCourse,
    ChoiceGroup,
    ChoiceGroupCourse,
    CourseEquivalency,
    CurriculumDraft,
    CurriculumDraftVersion,
    Career,
    CareerSkill,
    Skill,
    ProgramCareer,
    CplType,
    ProgramCplGuidance,
    AcademicTerm,
    ScheduleProviderConfig,
    TransferOption,
    GovernanceDraft,
    GovernanceDraftVersion,
    CurriculumGraphEdgeOverride,
)
from curriculum_graph_service import (
    ALLOWED_OVERRIDE_ACTIONS,
    ALLOWED_RELATION_TYPES,
    build_curriculum_graph,
    is_graph_program,
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


class CurriculumGraphEdgePayload(BaseModel):
    source_course_id: int
    target_course_id: int
    relation_type: str = "prerequisite"
    action: str = "add"
    group_id: int = Field(default=1, ge=1, le=99)
    note: Optional[str] = Field(default=None, max_length=500)


class CunyBeyondRecommendationPayload(BaseModel):
    career_goal: str = Field(min_length=2, max_length=240)
    skills: list[str] = Field(default_factory=list, max_length=5)


class CunyBeyondCplPayload(BaseModel):
    selections: list[str] = Field(default_factory=list, max_length=9)
    program_codes: list[str] = Field(default_factory=list, max_length=3)


class CunyBeyondApPayload(BaseModel):
    exams: list[dict[str, Any]] = Field(default_factory=list, max_length=20)


@lru_cache(maxsize=1)
def load_ap_equivalencies():
    path = Path("docs/bmcc_ap_equivalencies.csv")
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


@lru_cache(maxsize=1)
def load_degree_map_sources():
    sources = {}
    for path in Path("docs").glob("*.json"):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        code = document.get("program_code")
        if code and (document.get("source_pdf") or document.get("source_pdfs")):
            sources[code] = {
                "source_pdf": document.get("source_pdf"),
                "source_pdfs": document.get("source_pdfs") or [],
                "catalog_year": document.get("catalog_year"),
            }
    return sources


class ScheduleHandoffPayload(BaseModel):
    institution_code: str = Field(min_length=2, max_length=12)
    term_code: str = Field(min_length=1, max_length=20)
    course_code: str = Field(min_length=3, max_length=30)
    modality: Optional[str] = Field(default=None, max_length=80)
    time_preference: Optional[str] = Field(default=None, max_length=80)


class AcademicTermPayload(BaseModel):
    name: str = Field(min_length=3, max_length=80)
    provider_code: str = Field(min_length=1, max_length=20)
    verified_at: datetime
    source_url: str = Field(min_length=10, max_length=500)
    active: bool


class ScheduleProviderPayload(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    enabled: bool = False
    approval_status: str
    api_base_url: Optional[str] = Field(default=None, max_length=500)
    data_owner: Optional[str] = Field(default=None, max_length=200)
    permission_reference: Optional[str] = Field(default=None, max_length=500)
    attribution: Optional[str] = Field(default=None, max_length=500)
    support_contact: Optional[str] = Field(default=None, max_length=200)
    refresh_seconds: int = 300
    retention_seconds: int = 900
    last_verified_at: Optional[datetime] = None


class GovernanceDraftPayload(BaseModel):
    entity_type: str
    entity_id: Optional[int] = None
    source_url: str = Field(min_length=10, max_length=500)
    document: dict[str, Any] = Field(default_factory=dict)


class GovernanceTransitionPayload(BaseModel):
    action: str


GOVERNED_ENTITY_TYPES = {"career", "skill", "program_career", "cpl_guidance", "transfer_option"}


def governance_version(db, draft, changed_by):
    number = (db.query(func.max(GovernanceDraftVersion.version_number)).filter_by(draft_id=draft.id).scalar() or 0) + 1
    db.add(GovernanceDraftVersion(
        draft_id=draft.id, version_number=number, document_json=draft.document_json,
        status=draft.status, changed_by=changed_by,
    ))


def serialize_governance_draft(draft):
    return {"id": draft.id, "entity_type": draft.entity_type, "entity_id": draft.entity_id,
            "status": draft.status, "source_url": draft.source_url,
            "document": json.loads(draft.document_json or "{}"),
            "created_by": draft.created_by, "updated_at": draft.updated_at.isoformat()}


def governed_program(db, document):
    return (db.query(Program).join(Department).join(Institution).filter(
        Institution.code == str(document.get("institution_code", "")).strip(),
        Program.code == str(document.get("program_code", "")).strip(),
    ).order_by(Program.catalog_year.desc()).first())


def publish_governance_draft(db, draft):
    document = json.loads(draft.document_json or "{}")
    reviewed_at = reviewed = datetime.fromisoformat(str(document.get("reviewed_at") or datetime.now(timezone.utc).date()))
    if reviewed.tzinfo is None:
        reviewed_at = reviewed.replace(tzinfo=timezone.utc)
    if not draft.source_url.startswith("https://"):
        raise HTTPException(status_code=422, detail="Published records require an HTTPS source URL")
    if draft.entity_type == "career":
        slug, name = str(document.get("slug", "")).strip(), str(document.get("name", "")).strip()
        if not slug or not name or not document.get("source_title"):
            raise HTTPException(status_code=422, detail="Career slug, name, and source title are required")
        entity = db.query(Career).filter_by(id=draft.entity_id).first() if draft.entity_id else db.query(Career).filter_by(slug=slug).first()
        if not entity:
            entity = Career(slug=slug); db.add(entity)
        entity.slug, entity.name = slug, name
        entity.aliases = str(document.get("aliases", "")).strip()
        entity.pathway_type = str(document.get("pathway_type", "career"))
        entity.source_title, entity.source_url = str(document["source_title"]), draft.source_url
        entity.reviewed_at, entity.active = reviewed_at, bool(document.get("active", True)); db.flush()
        db.query(CareerSkill).filter_by(career_id=entity.id).delete()
        for slug_value in document.get("skill_slugs", [])[:5]:
            skill = db.query(Skill).filter_by(slug=slug_value).first()
            if not skill: raise HTTPException(status_code=422, detail=f"Unknown skill: {slug_value}")
            db.add(CareerSkill(career_id=entity.id, skill_id=skill.id))
    elif draft.entity_type == "skill":
        slug, name = str(document.get("slug", "")).strip(), str(document.get("name", "")).strip()
        if not slug or not name: raise HTTPException(status_code=422, detail="Skill slug and name are required")
        entity = db.query(Skill).filter_by(id=draft.entity_id).first() if draft.entity_id else db.query(Skill).filter_by(slug=slug).first()
        if not entity: entity = Skill(slug=slug); db.add(entity)
        entity.slug, entity.name, entity.active = slug, name, bool(document.get("active", True))
    elif draft.entity_type == "program_career":
        program = governed_program(db, document); career = db.query(Career).filter_by(slug=document.get("career_slug")).first()
        if not program or not career or not document.get("explanation") or not document.get("source_title"):
            raise HTTPException(status_code=422, detail="Valid program, career, explanation, and source title are required")
        entity = db.query(ProgramCareer).filter_by(id=draft.entity_id).first() if draft.entity_id else db.query(ProgramCareer).filter_by(program_id=program.id, career_id=career.id).first()
        if not entity: entity = ProgramCareer(program_id=program.id, career_id=career.id); db.add(entity)
        entity.career_points = int(document.get("career_points", 50)); entity.evidence_level = str(document.get("evidence_level", "strong"))
        entity.explanation = str(document["explanation"]); entity.source_title = str(document["source_title"]); entity.source_url = draft.source_url
        entity.official_program_url = str(document.get("official_program_url") or draft.source_url); entity.reviewed_at = reviewed_at; entity.active = bool(document.get("active", True))
    elif draft.entity_type == "cpl_guidance":
        program = governed_program(db, document); cpl = db.query(CplType).filter_by(code=document.get("cpl_type_code")).first()
        if not program or not cpl or not document.get("guidance") or not document.get("evidence_requested"):
            raise HTTPException(status_code=422, detail="Valid program, CPL type, guidance, and evidence are required")
        entity = db.query(ProgramCplGuidance).filter_by(id=draft.entity_id).first() if draft.entity_id else db.query(ProgramCplGuidance).filter_by(program_id=program.id, cpl_type_id=cpl.id).first()
        if not entity: entity = ProgramCplGuidance(program_id=program.id, cpl_type_id=cpl.id); db.add(entity)
        entity.guidance = str(document["guidance"]); entity.evidence_requested = str(document["evidence_requested"])
        entity.source_url = draft.source_url; entity.reviewed_at = reviewed_at; entity.status = "published"
    else:
        program = governed_program(db, document)
        if not program or not document.get("target_institution") or not document.get("target_program") or not document.get("explanation"):
            raise HTTPException(status_code=422, detail="Valid source program and target transfer details are required")
        entity = db.query(TransferOption).filter_by(id=draft.entity_id).first() if draft.entity_id else None
        if not entity: entity = TransferOption(source_program_id=program.id); db.add(entity)
        entity.target_institution = str(document["target_institution"]); entity.target_program = str(document["target_program"])
        entity.target_degree = str(document.get("target_degree", "")); entity.target_url = str(document.get("target_url") or draft.source_url)
        entity.explanation = str(document["explanation"]); entity.source_url = draft.source_url; entity.reviewed_at = reviewed_at; entity.active = bool(document.get("active", True))
    db.flush(); draft.entity_id = entity.id


def archive_governed_entity(db, draft):
    models_by_type = {"career": Career, "skill": Skill, "program_career": ProgramCareer,
                      "cpl_guidance": ProgramCplGuidance, "transfer_option": TransferOption}
    model = models_by_type.get(draft.entity_type)
    entity = db.query(model).filter_by(id=draft.entity_id).first() if model and draft.entity_id else None
    if not entity: raise HTTPException(status_code=404, detail="Published entity not found for archival")
    if draft.entity_type == "cpl_guidance": entity.status = "archived"
    else: entity.active = False


@router.get("/admin/governance/dashboard")
def governance_dashboard(_admin=Depends(require_admin), db: Session = Depends(get_db)):
    active_careers = db.query(Career).filter_by(active=True).all()
    unmapped = [career.name for career in active_careers if not any(link.active for link in career.program_links)]
    stale_before = datetime.now(timezone.utc).replace(tzinfo=None).timestamp() - 365 * 86400
    stale = [career.name for career in active_careers if career.reviewed_at.timestamp() < stale_before]
    empty_programs = []
    for link in db.query(ProgramCareer).filter_by(active=True).all():
        count = db.query(func.count(RequirementGroup.id)).filter_by(program_id=link.program_id).scalar() or 0
        if not count: empty_programs.append(link.program.code)
    return {"counts": {"careers": len(active_careers), "skills": db.query(Skill).filter_by(active=True).count(),
                       "program_mappings": db.query(ProgramCareer).filter_by(active=True).count(), "drafts": db.query(GovernanceDraft).filter(GovernanceDraft.status != "published").count()},
            "issues": {"unmapped_careers": unmapped, "stale_careers": stale, "mapped_programs_without_curriculum": sorted(set(empty_programs)),
                       "active_terms_without_code": [term.name for term in db.query(AcademicTerm).filter_by(active=True).all() if not term.provider_code]},
            "stale_after_days": 365}


@router.get("/admin/governance/catalog")
def governance_catalog(_admin=Depends(require_admin), db: Session = Depends(get_db)):
    return {"careers": [{"id": c.id, "slug": c.slug, "name": c.name, "active": c.active, "reviewed_at": c.reviewed_at.date().isoformat(), "source_url": c.source_url} for c in db.query(Career).order_by(Career.name)],
            "skills": [{"id": s.id, "slug": s.slug, "name": s.name, "active": s.active} for s in db.query(Skill).order_by(Skill.name)],
            "program_mappings": [{"id": m.id, "career": m.career.name, "program": m.program.code, "active": m.active, "reviewed_at": m.reviewed_at.date().isoformat()} for m in db.query(ProgramCareer).options(joinedload(ProgramCareer.career), joinedload(ProgramCareer.program)).all()]}


@router.get("/admin/governance/drafts")
def list_governance_drafts(_admin=Depends(require_admin), db: Session = Depends(get_db)):
    return [serialize_governance_draft(item) for item in db.query(GovernanceDraft).order_by(GovernanceDraft.updated_at.desc()).all()]


@router.post("/admin/governance/drafts")
def create_governance_draft(payload: GovernanceDraftPayload, admin=Depends(require_admin), db: Session = Depends(get_db)):
    if payload.entity_type not in GOVERNED_ENTITY_TYPES: raise HTTPException(status_code=422, detail="Unsupported governed entity type")
    draft = GovernanceDraft(entity_type=payload.entity_type, entity_id=payload.entity_id, source_url=payload.source_url, document_json=json.dumps(payload.document), created_by=admin)
    db.add(draft); db.flush(); governance_version(db, draft, admin); db.commit(); db.refresh(draft); return serialize_governance_draft(draft)


@router.put("/admin/governance/drafts/{draft_id}")
def update_governance_draft(draft_id: int, payload: GovernanceDraftPayload, admin=Depends(require_admin), db: Session = Depends(get_db)):
    draft = db.query(GovernanceDraft).filter_by(id=draft_id).first()
    if not draft or draft.status not in {"draft", "review"}: raise HTTPException(status_code=409, detail="Only draft or review records can be edited")
    draft.entity_type, draft.entity_id, draft.source_url, draft.document_json = payload.entity_type, payload.entity_id, payload.source_url, json.dumps(payload.document)
    draft.updated_at = datetime.now(timezone.utc); governance_version(db, draft, admin); db.commit(); db.refresh(draft); return serialize_governance_draft(draft)


@router.post("/admin/governance/drafts/{draft_id}/transition")
def transition_governance_draft(draft_id: int, payload: GovernanceTransitionPayload, admin=Depends(require_admin), db: Session = Depends(get_db)):
    draft = db.query(GovernanceDraft).filter_by(id=draft_id).first()
    if not draft: raise HTTPException(status_code=404, detail="Governance draft not found")
    allowed = {"draft": {"review"}, "review": {"draft", "approved"}, "approved": {"published", "draft"}, "published": {"archived"}, "archived": {"draft"}}
    if payload.action not in allowed.get(draft.status, set()): raise HTTPException(status_code=409, detail=f"Cannot move {draft.status} to {payload.action}")
    if payload.action == "published": publish_governance_draft(db, draft)
    if payload.action == "archived": archive_governed_entity(db, draft)
    draft.status = payload.action; draft.updated_at = datetime.now(timezone.utc); governance_version(db, draft, admin); db.commit(); db.refresh(draft); return serialize_governance_draft(draft)


@router.post("/admin/governance/drafts/{draft_id}/rollback/{version_number}")
def rollback_governance_draft(draft_id: int, version_number: int, admin=Depends(require_admin), db: Session = Depends(get_db)):
    draft = db.query(GovernanceDraft).filter_by(id=draft_id).first(); version = db.query(GovernanceDraftVersion).filter_by(draft_id=draft_id, version_number=version_number).first()
    if not draft or not version: raise HTTPException(status_code=404, detail="Draft or version not found")
    draft.document_json, draft.status = version.document_json, "draft"; draft.updated_at = datetime.now(timezone.utc); governance_version(db, draft, admin); db.commit(); db.refresh(draft); return serialize_governance_draft(draft)


@router.get("/admin/governance/drafts/{draft_id}/versions")
def list_governance_versions(draft_id: int, _admin=Depends(require_admin), db: Session = Depends(get_db)):
    if not db.query(GovernanceDraft).filter_by(id=draft_id).first(): raise HTTPException(status_code=404, detail="Governance draft not found")
    return [{"version_number": item.version_number, "status": item.status, "changed_by": item.changed_by,
             "created_at": item.created_at.isoformat()} for item in db.query(GovernanceDraftVersion).filter_by(draft_id=draft_id).order_by(GovernanceDraftVersion.version_number.desc()).all()]


def serialize_term(term):
    return {
        "id": term.id, "name": term.name, "provider": term.provider,
        "provider_code": term.provider_code, "verified_at": term.verified_at.isoformat(),
        "source_url": term.source_url, "active": term.active,
    }


@router.get("/cuny-beyond/schedule/terms")
def get_active_schedule_terms(db: Session = Depends(get_db)):
    return [serialize_term(term) for term in db.query(AcademicTerm).filter_by(active=True).order_by(AcademicTerm.provider_code.desc()).all()]


@router.post("/cuny-beyond/schedule/handoff")
def get_schedule_handoff(payload: ScheduleHandoffPayload, db: Session = Depends(get_db)):
    term = db.query(AcademicTerm).filter_by(provider_code=payload.term_code, active=True).first()
    if not term:
        raise HTTPException(status_code=400, detail="Select an active, administrator-verified term")
    try:
        return build_global_search_handoff(
            payload.institution_code, term, payload.course_code,
            modality=payload.modality, time_preference=payload.time_preference,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/cuny-beyond/schedule/sections")
def get_schedule_sections(payload: ScheduleHandoffPayload, db: Session = Depends(get_db)):
    term = db.query(AcademicTerm).filter_by(provider_code=payload.term_code, active=True).first()
    if not term:
        raise HTTPException(status_code=400, detail="Select an active, administrator-verified term")
    try:
        handoff = build_global_search_handoff(payload.institution_code, term, payload.course_code,
            modality=payload.modality, time_preference=payload.time_preference)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    config = db.query(ScheduleProviderConfig).filter_by(code="cuny_official_sections").first()
    return build_section_fallback(config, handoff)


@router.get("/admin/schedule/terms")
def get_admin_schedule_terms(_admin=Depends(require_admin), db: Session = Depends(get_db)):
    return [serialize_term(term) for term in db.query(AcademicTerm).order_by(AcademicTerm.provider_code.desc()).all()]


@router.put("/admin/schedule/terms/{term_id}")
def update_admin_schedule_term(term_id: int, payload: AcademicTermPayload, _admin=Depends(require_admin), db: Session = Depends(get_db)):
    term = db.query(AcademicTerm).filter_by(id=term_id).first()
    if not term:
        raise HTTPException(status_code=404, detail="Academic term not found")
    term.name = payload.name.strip()
    term.provider_code = payload.provider_code.strip()
    term.verified_at = payload.verified_at
    term.source_url = payload.source_url.strip()
    term.active = payload.active
    db.commit()
    db.refresh(term)
    return serialize_term(term)


def serialize_schedule_provider(config):
    return {"id": config.id, "code": config.code, "name": config.name, "enabled": config.enabled,
        "approval_status": config.approval_status, "api_base_url": config.api_base_url,
        "data_owner": config.data_owner, "permission_reference": config.permission_reference,
        "attribution": config.attribution, "support_contact": config.support_contact,
        "refresh_seconds": config.refresh_seconds, "retention_seconds": config.retention_seconds,
        "last_verified_at": config.last_verified_at.isoformat() if config.last_verified_at else None,
        "updated_at": config.updated_at.isoformat(), "readiness": provider_readiness(config)}


@router.get("/admin/schedule/provider")
def get_admin_schedule_provider(_admin=Depends(require_admin), db: Session = Depends(get_db)):
    config = db.query(ScheduleProviderConfig).filter_by(code="cuny_official_sections").first()
    if not config:
        config = ScheduleProviderConfig(code="cuny_official_sections", name="CUNY official live sections")
        db.add(config); db.commit(); db.refresh(config)
    return serialize_schedule_provider(config)


@router.put("/admin/schedule/provider")
def update_admin_schedule_provider(payload: ScheduleProviderPayload, admin=Depends(require_admin), db: Session = Depends(get_db)):
    config = db.query(ScheduleProviderConfig).filter_by(code="cuny_official_sections").first()
    if not config:
        config = ScheduleProviderConfig(code="cuny_official_sections"); db.add(config)
    for field, value in payload.model_dump().items():
        if isinstance(value, str): value = value.strip() or None
        setattr(config, field, value)
    config.updated_by = str(admin); config.updated_at = datetime.now(timezone.utc)
    errors = validate_provider_config(config)
    if errors:
        raise HTTPException(status_code=422, detail={"message": "Provider configuration is not safe to enable", "errors": errors})
    db.commit(); db.refresh(config)
    return serialize_schedule_provider(config)


@router.get("/cuny-beyond/careers")
def get_cuny_beyond_careers(db: Session = Depends(get_db)):
    careers = db.query(Career).filter(Career.active.is_(True)).order_by(Career.name).all()
    return [
        {
            "slug": career.slug,
            "name": career.name,
            "aliases": [part.strip() for part in (career.aliases or "").split("|") if part.strip()],
            "reviewed_at": career.reviewed_at.date().isoformat(),
            "program_count": sum(1 for link in career.program_links if link.active),
        }
        for career in careers
    ]


@router.get("/cuny-beyond/ap-equivalencies")
def get_cuny_beyond_ap_equivalencies():
    return [{"exam": row["exam"]} for row in load_ap_equivalencies()]


@router.post("/cuny-beyond/ap-equivalencies")
def calculate_cuny_beyond_ap_equivalencies(payload: CunyBeyondApPayload, db: Session = Depends(get_db)):
    rows = {row["exam"]: row for row in load_ap_equivalencies()}
    bmcc = db.query(Institution).filter(Institution.code == "BMCC").first()
    results = []
    total = 0
    for selected in payload.exams:
        exam = str(selected.get("exam") or "").strip()
        try:
            score = int(selected.get("score"))
        except (TypeError, ValueError):
            raise HTTPException(status_code=422, detail="AP scores must be 3, 4, or 5")
        if exam not in rows or score not in {3, 4, 5}:
            raise HTTPException(status_code=422, detail="Unknown AP exam or score")
        equivalency = rows[exam][f"score_{score}"]
        alternatives = [item.strip() for item in equivalency.split(" or ")]
        course = None
        if bmcc:
            course = db.query(Course).filter(
                Course.institution_id == bmcc.id,
                func.upper(Course.catalog_code) == alternatives[0].upper(),
            ).first()
        credits = int(course.credits) if course else None
        if credits is not None:
            total += credits
        results.append({"exam": exam, "score": score, "bmcc_equivalency": equivalency,
                        "estimated_credits": credits, "source_url": rows[exam]["source_url"]})
    return {"results": results, "estimated_total_credits": total,
            "disclaimer": "Planning estimate only. BMCC awards credit after receiving and evaluating an official score report; degree applicability can vary."}


def optional_text(value):
    return value.strip() if value and value.strip() else None


def normalize_course_code(value: str):
    return " ".join(value.strip().upper().split())


def normalize_equivalency_source(value: str, equivalency_type: str):
    codes = [normalize_course_code(code) for code in value.split("+") if code.strip()]
    if equivalency_type == "direct" and len(codes) != 1:
        raise HTTPException(status_code=400, detail="A direct equivalency requires one source course")
    if equivalency_type == "combination" and len(codes) < 2:
        raise HTTPException(status_code=400, detail="A combination equivalency requires at least two source courses")
    return " + ".join(codes)


@router.post("/cuny-beyond/recommendations")
def get_cuny_beyond_recommendations(
    payload: CunyBeyondRecommendationPayload,
    db: Session = Depends(get_db),
):
    careers = db.query(Career).filter(Career.active.is_(True)).order_by(Career.name).all()
    career_records = [
        {
            "id": career.id,
            "slug": career.slug,
            "name": career.name,
            "aliases": [part.strip() for part in (career.aliases or "").split("|") if part.strip()],
        }
        for career in careers
    ]
    matched = resolve_career(payload.career_goal, career_records)
    if not matched:
        return {
            "matched_career": None,
            "recommendations": [],
            "message": "That wording does not match a reviewed career yet. Browse the supported careers below or explore your goal with an advisor.",
            "supported_careers": [item["name"] for item in career_records[:12]],
        }

    career = next(item for item in careers if item.id == matched["id"])
    career_skills = [link.skill.name for link in career.skills if link.skill.active]
    links = (
        db.query(ProgramCareer)
        .options(
            joinedload(ProgramCareer.program)
            .joinedload(Program.department)
            .joinedload(Department.institution),
        )
        .filter(
            ProgramCareer.career_id == career.id,
            ProgramCareer.active.is_(True),
        )
        .all()
    )

    mappings = []
    for link in links:
        program = link.program
        curriculum_count = (
            db.query(func.count(RequirementGroupCourse.id))
            .join(RequirementGroup, RequirementGroupCourse.requirement_group_id == RequirementGroup.id)
            .filter(RequirementGroup.program_id == program.id)
            .scalar()
        ) or db.query(func.count(ProgramCourse.id)).filter(ProgramCourse.program_id == program.id).scalar()
        mappings.append({
            "program_id": program.id,
            "program_code": program.code,
            "program_name": program.name,
            "degree_type": program.degree_type,
            "catalog_year": program.catalog_year,
            "institution_code": program.department.institution.code,
            "institution_name": program.department.institution.name,
            "department_name": program.department.name,
            "career_points": link.career_points,
            "career_skills": career_skills,
            "evidence_level": link.evidence_level,
            "explanation": link.explanation,
            "source_title": link.source_title,
            "source_url": link.source_url,
            "official_program_url": link.official_program_url,
            "reviewed_at": link.reviewed_at.date().isoformat(),
            "has_curriculum": int(curriculum_count or 0) > 0,
        })

    recommendations = rank_program_matches(mappings, payload.skills)
    for recommendation in recommendations:
        program = next((link.program for link in links if link.program.code == recommendation["program_code"]), None)
        options = db.query(TransferOption).filter_by(source_program_id=program.id, active=True).all() if program else []
        recommendation["transfer_options"] = [{"target_institution": option.target_institution, "target_program": option.target_program,
                                                "target_degree": option.target_degree, "target_url": option.target_url,
                                                "explanation": option.explanation, "source_url": option.source_url,
                                                "reviewed_at": option.reviewed_at.date().isoformat()} for option in options]
        recommendation["degree_map"] = load_degree_map_sources().get(recommendation["program_code"])
    return {
        "matched_career": {
            "slug": career.slug,
            "name": career.name,
            "source_title": career.source_title,
            "source_url": career.source_url,
            "reviewed_at": career.reviewed_at.date().isoformat(),
        },
        "recommendations": recommendations,
        "message": None if recommendations else "No populated BMCC curriculum currently meets the evidence threshold for this career.",
    }


@router.post("/cuny-beyond/cpl-screening")
def get_cuny_beyond_cpl_screening(
    payload: CunyBeyondCplPayload,
    db: Session = Depends(get_db),
):
    selected_codes = list(dict.fromkeys(code.strip() for code in payload.selections if code.strip()))
    if "none" in selected_codes:
        return {
            "opportunities": [],
            "document_checklist": [],
            "message": "No possible prior-learning pathway was selected. You can still ask BMCC CPL staff if your circumstances change.",
            "disclaimer": "This screening does not evaluate or award credit and does not change any degree total.",
        }

    published_types = db.query(CplType).filter(
        CplType.active.is_(True), CplType.status == "published"
    ).all()
    types_by_code = {item.code: item for item in published_types}
    recognized_codes = set(types_by_code) | {"not-sure"}
    unknown_codes = sorted(set(selected_codes) - recognized_codes)
    if unknown_codes:
        raise HTTPException(status_code=400, detail=f"Unknown CPL selection: {unknown_codes[0]}")

    requested_types = [types_by_code[code] for code in selected_codes if code in types_by_code]
    program_codes = list(dict.fromkeys(code.strip() for code in payload.program_codes if code.strip()))
    guidance_rows = []
    if requested_types and program_codes:
        guidance_rows = (
            db.query(ProgramCplGuidance)
            .options(joinedload(ProgramCplGuidance.program))
            .join(Program, ProgramCplGuidance.program_id == Program.id)
            .filter(
                Program.code.in_(program_codes),
                ProgramCplGuidance.cpl_type_id.in_([item.id for item in requested_types]),
                ProgramCplGuidance.status == "published",
            )
            .all()
        )
    guidance_by_type = {}
    for row in guidance_rows:
        guidance_by_type.setdefault(row.cpl_type_id, []).append({
            "program_code": row.program.code,
            "program_name": row.program.name,
            "guidance": row.guidance,
            "evidence_requested": row.evidence_requested,
            "source_url": row.source_url,
            "reviewed_at": row.reviewed_at.date().isoformat(),
        })

    opportunities = []
    checklist = []
    for item in requested_types:
        checklist.append(item.evidence_requested)
        opportunities.append({
            "code": item.code,
            "name": item.name,
            "status_label": "Possible CPL opportunity - evaluation required",
            "description": item.description,
            "evidence_requested": item.evidence_requested,
            "next_step": item.next_step,
            "official_url": item.official_url,
            "source_title": item.source_title,
            "reviewed_at": item.reviewed_at.date().isoformat(),
            "program_guidance": guidance_by_type.get(item.id, []),
        })

    if "not-sure" in selected_codes:
        opportunities.append({
            "code": "not-sure",
            "name": "Prior learning review conversation",
            "status_label": "Possible CPL opportunity - evaluation required",
            "description": "You do not need to identify the correct CPL mechanism before contacting BMCC. CPL staff can help determine whether documentation or an official evaluation route exists.",
            "evidence_requested": "A short list of previous education, examinations, credentials, training, military learning, languages, or substantial work-based learning.",
            "next_step": "Review the official BMCC CPL page and contact CPL staff with a concise description of the learning you want evaluated.",
            "official_url": "https://www.bmcc.cuny.edu/admissions/apply-now/credit-for-prior-learning-cpl/",
            "source_title": "BMCC Credit for Prior Learning",
            "reviewed_at": "2026-08-21",
            "program_guidance": [],
        })
        checklist.append("A short list of prior education, examinations, credentials, training, military learning, languages, or substantial work-based learning.")

    return {
        "opportunities": opportunities,
        "document_checklist": list(dict.fromkeys(checklist)),
        "message": None if opportunities else "Choose at least one prior-learning response to receive preparation guidance.",
        "disclaimer": "These are possible CPL opportunities only. BMCC must evaluate official evidence, determine course equivalency and degree applicability, and award any credit. Nothing here changes remaining credits or degree totals.",
    }


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
    selected_by_concentration = []
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
            group_option_count = sum(1 for item in concentration.get("core_groups") or [] if item.get("bin") == key)
            if requirement.get("required_course_count") and requirement["required_course_count"] > len(values) + group_option_count:
                errors.append(f"{name or f'Concentration {index}'} requires more courses in {key} than it provides.")
        core_groups = concentration.get("core_groups") or []
        selected_group_codes = {item.get("code") for item in core_groups if item.get("code")}
        campus_group_codes = {
            row[0] for row in db.query(ChoiceGroup.code).filter_by(institution_id=draft.institution_id).all()
        } if draft.institution_id else set()
        missing_groups = sorted(selected_group_codes - campus_group_codes)
        if missing_groups:
            errors.append(f"{name or f'Concentration {index}'} references missing Core groups: {missing_groups}.")
        if not selected and not core_groups:
            errors.append(f"{name or f'Concentration {index}'} has no curriculum courses.")
        duplicates = sorted({course_id for course_id in selected if selected.count(course_id) > 1})
        selected_by_concentration.append(set(selected))
        if duplicates:
            warnings.append(f"{name or f'Concentration {index}'} uses {len(duplicates)} course(s) in multiple bins; completion will be synchronized.")
    rules = document.get("rules") or {}
    for rule_type in ("alternatives", "prerequisites"):
        for rule in rules.get(rule_type) or []:
            ids = [rule.get("course_id"), rule.get("alternative_course_id" if rule_type == "alternatives" else "prerequisite_course_id")]
            if any(course_id not in known_ids for course_id in ids):
                errors.append(f"A {rule_type[:-1]} rule references a missing course.")
            selected_ids = set().union(*selected_by_concentration) if selected_by_concentration else set()
            if any(course_id not in selected_ids for course_id in ids):
                errors.append(f"A {rule_type[:-1]} rule references a course outside the curriculum bins.")
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
        concentration_index = pool.get("concentration_index", 0)
        selected_ids = selected_by_concentration[concentration_index] if 0 <= concentration_index < len(selected_by_concentration) else set()
        if any(course_id not in selected_ids for course_id in pool.get("course_ids") or []):
            errors.append(f"Elective pool {pool.get('name') or ''} references a course outside its concentration bins.")
    for adjustment in rules.get("core_adjustments") or []:
        placeholder_id = adjustment.get("placeholder_course_id")
        placeholder_group_code = adjustment.get("placeholder_group_code")
        placeholder_ids.append(placeholder_id or f"group:{placeholder_group_code}")
        if not placeholder_group_code and placeholder_id not in known_ids:
            errors.append("A Core adjustment references a missing placeholder course.")
        concentration_index = adjustment.get("concentration_index", 0)
        if concentration_index < 0 or concentration_index >= len(concentrations):
            errors.append("A Core adjustment references a missing concentration.")
        elif placeholder_group_code:
            placed_groups = {item.get("code") for item in concentrations[concentration_index].get("core_groups") or []}
            if placeholder_group_code not in placed_groups:
                errors.append("A Core adjustment group must also be placed in a curriculum bin.")
        elif placeholder_id not in [course_id for values in (concentrations[concentration_index].get("bins") or {}).values() for course_id in values]:
            errors.append("A Core adjustment placeholder must also be placed in a curriculum bin.")
        adjusted_ids = (adjustment.get("include_course_ids") or []) + (adjustment.get("exclude_course_ids") or [])
        if any(course_id not in known_ids for course_id in adjusted_ids):
            errors.append("A Core adjustment references a missing included or excluded course.")
        selected_ids = selected_by_concentration[concentration_index] if 0 <= concentration_index < len(selected_by_concentration) else set()
        if any(course_id not in selected_ids for course_id in adjusted_ids):
            errors.append("A Core adjustment references a course outside its concentration bins.")
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
    source_course_codes = [
        code.strip() for code in rule.source_course_code.split("+") if code.strip()
    ]
    return {
        "id": rule.id,
        "source_institution_id": rule.source_institution_id,
        "source_institution": rule.source_institution.name,
        "source_institution_code": rule.source_institution.code,
        "source_course_code": rule.source_course_code,
        "source_course_codes": source_course_codes,
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

    target_code = normalize_course_code(payload.target_course_code)
    if not payload.source_course_code.strip() or not target_code:
        raise HTTPException(status_code=400, detail="Source and target course codes are required")

    status = payload.status.strip().lower()
    if status not in {"draft", "approved", "inactive"}:
        raise HTTPException(status_code=400, detail="Status must be draft, approved, or inactive")

    equivalency_type = payload.equivalency_type.strip().lower()
    if equivalency_type not in {"direct", "combination"}:
        raise HTTPException(
            status_code=400,
            detail="Equivalency type must be direct or combination",
        )
    source_code = normalize_equivalency_source(payload.source_course_code, equivalency_type)

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


@router.get("/curriculum-drafts/{draft_id}/preview")
def preview_curriculum_draft(
    draft_id: int,
    concentration: int = 0,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    draft = db.query(CurriculumDraft).filter_by(id=draft_id).first()
    if not draft:
        raise HTTPException(status_code=404, detail="Curriculum draft not found")
    document = json.loads(draft.document_json or "{}")
    concentrations = document.get("concentrations") or []
    if concentration < 0 or concentration >= len(concentrations):
        raise HTTPException(status_code=404, detail="Draft concentration not found")
    selected = concentrations[concentration]
    rules = document.get("rules") or {}
    metadata = document.get("metadata") or {}
    course_cache = {course.id: course for course in db.query(Course).all()}
    choice_group_cache = {
        group.code: group
        for group in db.query(ChoiceGroup).filter_by(institution_id=draft.institution_id).all()
    }

    def preview_course(course_id: int):
        course = course_cache.get(course_id)
        if not course:
            return None
        prereq_groups = {}
        for rule in rules.get("prerequisites") or []:
            if rule.get("course_id") == course_id:
                prereq = course_cache.get(rule.get("prerequisite_course_id"))
                if prereq:
                    prereq_groups.setdefault(rule.get("group_id", 1), []).append(prereq.display_code)
        alternatives = []
        for rule in rules.get("alternatives") or []:
            if rule.get("course_id") == course_id:
                alternative = course_cache.get(rule.get("alternative_course_id"))
                if alternative:
                    alternatives.append(alternative.display_code)
        adjustment = next(
            (
                item for item in rules.get("core_adjustments") or []
                if item.get("concentration_index", 0) == concentration
                and item.get("placeholder_course_id") == course_id
            ),
            None,
        )
        return {
            "code": course.display_code,
            "title": course.title,
            "credits": course.credits,
            "choice_group_code": adjustment.get("base_group_code") if adjustment else course.choice_group_code,
            "prereqs": [values[0] if len(values) == 1 else values for _, values in sorted(prereq_groups.items())],
            "alternatives": alternatives,
        }

    groups = []
    bin_labels = (
        ("major_required", "Major Requirements", "program_required"),
        ("major_electives", "Major Electives", "program_elective"),
        ("common_core", "Common Core", "common_core"),
        ("flex_core", "Flexible Core", "flexible_core"),
    )
    for order, (key, label, group_type) in enumerate(bin_labels):
        course_payloads = [preview_course(course_id) for course_id in (selected.get("bins") or {}).get(key, [])]
        course_payloads = [course for course in course_payloads if course]
        for core_item in selected.get("core_groups") or []:
            if core_item.get("bin") != key:
                continue
            choice_group = choice_group_cache.get(core_item.get("code"))
            if choice_group:
                course_payloads.append({
                    "code": f"CORE-{choice_group.code}",
                    "title": choice_group.name,
                    "credits": core_item.get("required_credits") or choice_group.required_credits or 0,
                    "choice_group_code": choice_group.code,
                    "prereqs": [],
                    "alternatives": [],
                })
        requirement = (selected.get("bin_requirements") or {}).get(key) or {}
        if course_payloads:
            groups.append({
                "id": f"draft-bin-{order}",
                "name": label,
                "group_type": group_type,
                "required_credits": requirement.get("required_credits"),
                "required_course_count": requirement.get("required_course_count"),
                "display_order": order,
                "courses": course_payloads,
            })
    for pool_index, pool in enumerate(rules.get("elective_pools") or []):
        if pool.get("concentration_index", 0) != concentration:
            continue
        course_payloads = [preview_course(course_id) for course_id in pool.get("course_ids") or []]
        groups.append({
            "id": f"draft-pool-{pool_index}",
            "name": pool.get("name") or "Elective Pool",
            "group_type": {
                "major_required": "program_required",
                "major_electives": "program_elective",
                "common_core": "common_core",
                "flex_core": "flexible_core",
            }.get(pool.get("bin"), "program_elective"),
            "required_credits": pool.get("required_credits"),
            "required_course_count": pool.get("required_course_count"),
            "display_order": 10 + pool_index,
            "courses": [course for course in course_payloads if course],
        })
    institution = db.query(Institution).filter_by(id=draft.institution_id).first()
    department = db.query(Department).filter_by(id=draft.department_id).first()
    return {
        "preview": True,
        "draft_id": draft.id,
        "concentration_index": concentration,
        "program": {
            "code": metadata.get("code") or f"DRAFT-{draft.id}",
            "name": draft.name if len(concentrations) == 1 else f"{draft.name} - {selected.get('name', 'Concentration')}",
            "catalog_year": metadata.get("catalog_year"),
            "degree_type": metadata.get("degree_type"),
            "department": department.name if department else "Draft department",
            "institution": institution.name if institution else "Draft campus",
            "institution_code": institution.code if institution else "DRAFT",
        },
        "groups": groups,
    }


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
            core_placeholders = {}
            for order, (key, label, group_type) in enumerate((
                ("major_required", "Major Requirements", "program_required"),
                ("major_electives", "Major Electives", "program_elective"),
                ("common_core", "Common Core", "common_core"),
                ("flex_core", "Flexible Core", "flexible_core"),
            )):
                course_ids = list(concentration.get("bins", {}).get(key) or [])
                for core_item in concentration.get("core_groups") or []:
                    if core_item.get("bin") != key:
                        continue
                    choice_group = db.query(ChoiceGroup).filter_by(
                        institution_id=draft.institution_id,
                        code=core_item.get("code"),
                    ).first()
                    if not choice_group:
                        continue
                    placeholder_code = f"{code}-{choice_group.code}".upper()
                    placeholder = Course(
                        code=placeholder_code,
                        title=choice_group.name,
                        credits=core_item.get("required_credits") or choice_group.required_credits or 0,
                        choice_group_code=choice_group.code,
                    )
                    db.add(placeholder)
                    db.flush()
                    course_ids.append(placeholder.id)
                    core_placeholders[choice_group.code] = placeholder
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
                    group_type={
                        "major_required": "program_required",
                        "major_electives": "program_elective",
                        "common_core": "common_core",
                        "flex_core": "flexible_core",
                    }.get(pool.get("bin"), "program_elective"),
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
                        if course.display_code.split()[0].upper() in allowed_subjects
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
                placeholder = core_placeholders.get(adjustment.get("placeholder_group_code"))
                if not placeholder:
                    placeholder = db.query(Course).filter_by(id=adjustment.get("placeholder_course_id")).first()
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
def get_programs(selector_only: bool = False, db: Session = Depends(get_db)):
    programs = (
        db.query(Program)
        .options(joinedload(Program.department).joinedload(Department.institution))
        .order_by(Program.name, Program.id)
        .all()
    )

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

    return canonical_selector_programs(result) if selector_only else result


@router.get("/courses")
def get_all_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).order_by(Course.catalog_code, Course.code).all()

    institution_codes: dict[int, set[str]] = {course.id: set() for course in courses}
    department_ids: dict[int, set[int]] = {course.id: set() for course in courses}
    for course_id, institution_code in (
        db.query(ChoiceGroupCourse.course_id, Institution.code)
        .join(ChoiceGroup, ChoiceGroupCourse.choice_group_id == ChoiceGroup.id)
        .join(Institution, ChoiceGroup.institution_id == Institution.id)
        .all()
    ):
        institution_codes.setdefault(course_id, set()).add(institution_code)
    for course_id, department_id, institution_code in (
        db.query(RequirementGroupCourse.course_id, Department.id, Institution.code)
        .join(RequirementGroup, RequirementGroupCourse.requirement_group_id == RequirementGroup.id)
        .join(Program, RequirementGroup.program_id == Program.id)
        .join(Department, Program.department_id == Department.id)
        .join(Institution, Department.institution_id == Institution.id)
        .all()
    ):
        institution_codes.setdefault(course_id, set()).add(institution_code)
        department_ids.setdefault(course_id, set()).add(department_id)
    for course_id, department_id, institution_code in (
        db.query(ProgramCourse.course_id, Department.id, Institution.code)
        .join(Program, ProgramCourse.program_id == Program.id)
        .join(Department, Program.department_id == Department.id)
        .join(Institution, Department.institution_id == Institution.id)
        .all()
    ):
        institution_codes.setdefault(course_id, set()).add(institution_code)
        department_ids.setdefault(course_id, set()).add(department_id)

    return [
        {
            "id": c.id,
            "code": c.display_code,
            "title": c.title,
            "credits": c.credits,
            "choice_group_code": c.choice_group_code,
            "institution_codes": sorted(institution_codes.get(c.id, set())),
            "department_ids": sorted(department_ids.get(c.id, set())),
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
    request: Request,
    institution_code: str = "BMCC",
    program_code: str | None = None,
    draft_preview: int | None = None,
    concentration: int = 0,
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
    advising_note = group.advising_note
    required_credits = group.required_credits
    required_course_count = group.required_course_count
    if draft_preview is not None:
        require_admin(request)
        draft = db.query(CurriculumDraft).filter_by(id=draft_preview).first()
        if not draft:
            raise HTTPException(status_code=404, detail="Curriculum draft not found")
        document = json.loads(draft.document_json or "{}")
        adjustment = next((
            item for item in (document.get("rules") or {}).get("core_adjustments") or []
            if item.get("concentration_index", 0) == concentration
            and item.get("base_group_code") == group.code
        ), None)
        if adjustment:
            allowed_ids = set(adjustment.get("include_course_ids") or [])
            allowed_subjects = set(adjustment.get("include_subject_codes") or [])
            excluded_ids = set(adjustment.get("exclude_course_ids") or [])
            if allowed_ids or allowed_subjects:
                links = [
                    link for link in links
                    if link.course_id in allowed_ids
                    or (
                        link.course
                        and link.course.display_code.split()[0].upper() in allowed_subjects
                    )
                ]
            links = [link for link in links if link.course_id not in excluded_ids]
            advising_note = adjustment.get("note") or advising_note
            required_credits = adjustment.get("required_credits") if adjustment.get("required_credits") is not None else required_credits
            required_course_count = adjustment.get("required_course_count") if adjustment.get("required_course_count") is not None else required_course_count

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
            "code": course.display_code,
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
            "required_credits": required_credits,
            "required_course_count": required_course_count,
            "advising_note": advising_note,
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
    group_prereq_rows = (
        db.query(CourseRequirementGroupPrerequisite)
        .filter_by(program_id=program_id, course_id=course.id)
        .all()
    )

    prereq_groups = {}

    for row in prereq_rows:
        prereq_course = db.query(Course).filter_by(id=row.prereq_course_id).first()
        if prereq_course:
            prereq_groups.setdefault(row.group_id, []).append(prereq_course.display_code)

    prereqs = []
    for _, codes in sorted(prereq_groups.items()):
        prereqs.append(codes[0] if len(codes) == 1 else codes)

    alternatives = []
    for row in alt_rows:
        alt_course = db.query(Course).filter_by(id=row.alternative_course_id).first()
        if alt_course:
            alternatives.append(alt_course.display_code)

    prerequisite_groups = []
    for row in group_prereq_rows:
        group = db.query(RequirementGroup).filter_by(id=row.requirement_group_id).first()
        if group:
            prerequisite_groups.append(group.name)

    return {
        "code": course.display_code,
        "title": course.title,
        "credits": course.credits,
        "choice_group_code": course.choice_group_code,
        "prereqs": prereqs,
        "alternatives": alternatives,
        "prerequisite_groups": prerequisite_groups,
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
                "code": link.course.display_code,
                "title": link.course.title,
                "credits": link.course.credits,
                "choice_group_code": link.course.choice_group_code,
                "requirement_type": link.requirement_type,
            }
            for link in links
        ],
    }


def _curriculum_graph_program_list(db):
    programs = (
        db.query(Program)
        .options(joinedload(Program.department).joinedload(Department.institution))
        .order_by(Program.name, Program.catalog_year)
        .all()
    )
    return canonical_selector_programs([{
        "id": program.id,
        "code": program.code,
        "name": program.name,
        "degree_type": program.degree_type,
        "catalog_year": program.catalog_year,
        "institution": program.department.institution.name,
        "institution_code": program.department.institution.code,
        "has_curriculum": True,
    } for program in programs if is_graph_program(db, program)])


@router.get("/programs/{program_code}/graph")
def get_program_graph(program_code: str, db: Session = Depends(get_db)):
    program = db.query(Program).filter_by(code=program_code).first()

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    if not is_graph_program(db, program):
        raise HTTPException(status_code=404, detail="This program has no populated curriculum to graph")
    return build_curriculum_graph(db, program)


@router.get("/admin/curriculum-graphs/programs")
def get_curriculum_graph_programs(_admin=Depends(require_admin), db: Session = Depends(get_db)):
    return _curriculum_graph_program_list(db)


@router.put("/admin/curriculum-graphs/{program_code}/edges")
def set_curriculum_graph_edge(
    program_code: str,
    payload: CurriculumGraphEdgePayload,
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    program = db.query(Program).filter_by(code=program_code).first()
    if not program or not is_graph_program(db, program):
        raise HTTPException(status_code=404, detail="Curriculum graph program not found")
    relation_type = payload.relation_type.strip().lower()
    action = payload.action.strip().lower()
    if relation_type not in ALLOWED_RELATION_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported relationship type")
    if action not in ALLOWED_OVERRIDE_ACTIONS:
        raise HTTPException(status_code=400, detail="Action must be add or remove")
    if payload.source_course_id == payload.target_course_id:
        raise HTTPException(status_code=400, detail="A course cannot depend on itself")

    institution_id = program.department.institution_id
    source = db.query(Course).filter_by(id=payload.source_course_id, institution_id=institution_id).first()
    target = db.query(Course).filter_by(id=payload.target_course_id, institution_id=institution_id).first()
    if not source or not target:
        raise HTTPException(status_code=400, detail="Both courses must belong to the program campus")

    row = db.query(CurriculumGraphEdgeOverride).filter_by(
        program_id=program.id,
        source_course_id=source.id,
        target_course_id=target.id,
        relation_type=relation_type,
        group_id=payload.group_id,
    ).first()
    if not row:
        row = CurriculumGraphEdgeOverride(
            program_id=program.id,
            source_course_id=source.id,
            target_course_id=target.id,
            relation_type=relation_type,
            group_id=payload.group_id,
        )
        db.add(row)
    row.action = action
    row.note = payload.note.strip() if payload.note else None
    row.updated_by = str(admin)
    row.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return {"status": "saved", "override_id": row.id, "graph": build_curriculum_graph(db, program)}


@router.delete("/admin/curriculum-graphs/{program_code}/overrides/{override_id}")
def delete_curriculum_graph_override(
    program_code: str,
    override_id: int,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    program = db.query(Program).filter_by(code=program_code).first()
    if not program or not is_graph_program(db, program):
        raise HTTPException(status_code=404, detail="Curriculum graph program not found")
    row = db.query(CurriculumGraphEdgeOverride).filter_by(id=override_id, program_id=program.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Graph override not found")
    db.delete(row)
    db.commit()
    return {"status": "deleted", "graph": build_curriculum_graph(db, program)}


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
    curriculum_course_ids = set()

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

            curriculum_course_ids.add(course.id)

            courses.append(build_course_payload(db, program.id, course))

        result_groups.append({
            "id": group.id,
            "name": group.name,
            "group_type": group.group_type,
            "required_credits": group.required_credits,
            "required_course_count": group.required_course_count,
            "display_order": group.display_order,
            "completion_options": json.loads(group.completion_options) if group.completion_options else [],
            "required_course_sets": json.loads(group.required_course_sets) if group.required_course_sets else [],
            "required_course_set_count": group.required_course_set_count,
            "courses": courses,
        })

    prerequisite_target_ids = set(curriculum_course_ids)
    choice_group_codes = {
        course.choice_group_code
        for course_id in curriculum_course_ids
        for course in [db.query(Course).filter_by(id=course_id).first()]
        if course and course.choice_group_code
    }
    if choice_group_codes:
        choice_groups = db.query(ChoiceGroup).filter(
            ChoiceGroup.institution_id == program.department.institution_id,
            ChoiceGroup.code.in_(choice_group_codes),
        ).all()
        choice_group_ids = [group.id for group in choice_groups]
        if choice_group_ids:
            prerequisite_target_ids.update(
                row.course_id
                for row in db.query(ChoiceGroupCourse).filter(
                    ChoiceGroupCourse.choice_group_id.in_(choice_group_ids)
                ).all()
            )

    support_course_ids = {
        row.prereq_course_id
        for row in db.query(CoursePrerequisite).filter(
            CoursePrerequisite.program_id == program.id,
            CoursePrerequisite.course_id.in_(prerequisite_target_ids),
        ).all()
        if row.prereq_course_id not in curriculum_course_ids
    } if prerequisite_target_ids else set()
    prerequisite_support_courses = []
    for course_id in sorted(support_course_ids):
        course = db.query(Course).filter_by(id=course_id).first()
        if course:
            prerequisite_support_courses.append(build_course_payload(db, program.id, course))

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
        "prerequisite_support_courses": prerequisite_support_courses,
    }
