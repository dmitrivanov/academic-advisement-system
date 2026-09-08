from contextlib import asynccontextmanager
import threading

from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
import json
import time
import smtplib
import re
import uuid
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Optional, Dict, Any

load_dotenv()

from api_db_routes import router as db_router
import career_routes
from career_routes import router as career_router
from auth import authenticate, is_admin, is_logged_in, require_admin
from cuny_beyond import is_cuny_beyond_enabled, public_config
from database import Base, engine
import models  # noqa: F401 - registers all SQLAlchemy tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-fetch O*NET details for the curated career list in the background
    # so the first real user click doesn't pay the cold-cache latency.
    # Runs only when the ASGI app actually starts (not on a bare import),
    # so it never fires during tests.
    threading.Thread(target=career_routes.warm_cache, daemon=True, name="onet-cache-warmup").start()
    yield


app = FastAPI(lifespan=lifespan)
Base.metadata.create_all(bind=engine)
app.include_router(db_router)
app.include_router(career_router)

SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-secret-change-this")

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_AGENT_PROMPT = """
You are an academic advising assistant embedded inside a webpage.

Use ONLY the page context provided by the webpage. Do not invent official degree requirements, course policies, prerequisites, transfer rules, or exceptions.

If the context does not contain enough information, say that clearly and suggest what information is missing.

Be concise, practical, and student-friendly. Explain locked courses, completed courses, not-needed alternatives, elective completion, and recommendations when relevant.
""".strip()

CONFIG_DIR = Path(os.environ.get("AI_CONFIG_DIR", "config"))
AI_SETTINGS_FILE = CONFIG_DIR / "ai_settings.json"
LOG_DIR = Path(os.environ.get("ADVISOR_LOG_DIR", "logs"))
LOG_FILE = LOG_DIR / "advisor_chat_logs.jsonl"
REFERRAL_LOG_FILE = LOG_DIR / "cuny_beyond_referral_delivery.jsonl"
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def default_ai_settings():
    return {
        "agent_id": "advisor_progress",
        "agent_name": "AI Academic Advisor",
        "page_name": "Degree Progress",
        "page_url": "/db-progress",
        "model": DEFAULT_MODEL,
        "system_prompt": DEFAULT_AGENT_PROMPT,
        "show_metrics": True,
        "log_enabled": True,
        "api_key": "",
    }


def load_ai_settings():
    settings = default_ai_settings()

    if AI_SETTINGS_FILE.exists():
        try:
            saved = json.loads(AI_SETTINGS_FILE.read_text(encoding="utf-8"))
            settings.update(saved)
        except Exception as exc:
            print(f"Could not read AI settings: {exc}")

    return settings


def save_ai_settings(settings: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    AI_SETTINGS_FILE.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")


def public_ai_settings(settings: dict):
    data = dict(settings)
    api_key = data.get("api_key") or os.environ.get("GEMINI_API_KEY")
    data["api_key_configured"] = bool(api_key)
    data["api_key"] = ""  # never return the actual key
    return data


def get_gemini_api_key():
    settings = load_ai_settings()
    return settings.get("api_key") or os.environ.get("GEMINI_API_KEY")


def make_gemini_client():
    api_key = get_gemini_api_key()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Gemini API key is not configured. Set GEMINI_API_KEY or save it in AI Settings."
        )
    return genai.Client(api_key=api_key)


def get_client_ip(request: Request):
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def extract_usage_metadata(response):
    usage = getattr(response, "usage_metadata", None)

    if not usage:
        return {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}

    return {
        "prompt_tokens": getattr(usage, "prompt_token_count", None),
        "completion_tokens": getattr(usage, "candidates_token_count", None),
        "total_tokens": getattr(usage, "total_token_count", None),
    }


def write_advisor_log(log_record: dict):
    try:
        settings = load_ai_settings()
        if not settings.get("log_enabled", True):
            return

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log_record, ensure_ascii=False) + "\n")
    except Exception as exc:
        print(f"Advisor log write failed: {exc}")


class Candidate(BaseModel):
    question: str
    answer: str
    score: float


class FallbackRequest(BaseModel):
    user_question: str
    major: str
    detected_courses: list[str]
    detected_intent: str
    candidates: list[Candidate]


class ProgressAdvisorRequest(BaseModel):
    user_question: str
    page_context: dict


class GenericAgentRequest(BaseModel):
    agent_id: Optional[str] = "advisor_progress"
    page_name: Optional[str] = None
    page_url: Optional[str] = None
    user_question: str
    page_context: Dict[str, Any]


class AISettingsPayload(BaseModel):
    agent_id: str = "advisor_progress"
    agent_name: str = "AI Academic Advisor"
    page_name: str = "Degree Progress"
    page_url: str = "/db-progress"
    model: str = DEFAULT_MODEL
    system_prompt: str = DEFAULT_AGENT_PROMPT
    show_metrics: bool = True
    log_enabled: bool = True
    api_key: Optional[str] = ""


class AdvisingReferralPayload(BaseModel):
    name: str
    email: str
    id_last_four: Optional[str] = ""
    consent: bool
    website: Optional[str] = ""  # Honeypot; real users never see or fill it.
    summary: Dict[str, Any]


class BeyondInterpretPayload(BaseModel):
    step: str
    answer: str
    career_goal: Optional[str] = ""
    allowed_values: list[str] = Field(default_factory=list)


def parse_model_json(text: str):
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="The AI response could not be safely interpreted") from exc


@app.post("/api/cuny-beyond/interpret")
def interpret_cuny_beyond_answer(payload: BeyondInterpretPayload):
    """Interpret public free text into reviewed UI values without creating policy."""
    if payload.step not in {"profile", "employment", "skills", "cpl"}:
        raise HTTPException(status_code=400, detail="Unknown intake step")
    prompt = f"""You interpret one answer for a college intake form. Return JSON only.
Step: {payload.step}
Career goal context: {payload.career_goal or 'not supplied'}
Allowed values: {json.dumps(payload.allowed_values)}
Student answer: {payload.answer[:800]}

For profile or employment return {{"selected_values":[one allowed value]}}.
For cpl return {{"selected_values":[zero or more allowed values]}}.
For skills return {{"skills":[exactly five short, concrete skills relevant to the career goal and answer]}}.
Never infer official credit, eligibility, or admission status. Use only allowed values except skill text."""
    client = make_gemini_client()
    response = client.models.generate_content(model=load_ai_settings().get("model", DEFAULT_MODEL), contents=prompt)
    result = parse_model_json(response.text or "")
    if payload.step == "skills":
        skills = [str(item).strip()[:80] for item in result.get("skills", []) if str(item).strip()][:5]
        return {"skills": skills}
    allowed = set(payload.allowed_values)
    selected = [item for item in result.get("selected_values", []) if item in allowed]
    return {"selected_values": selected[:9]}


@app.post("/api/cuny-beyond/transcript-extract")
async def extract_cuny_beyond_transcript(document: UploadFile = File(...)):
    """Extract a reviewable draft; never persist the uploaded document or award credit."""
    allowed_types = {"application/pdf", "image/jpeg", "image/png"}
    if document.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail="Upload a PDF, JPG, or PNG document")
    content = await document.read(8 * 1024 * 1024 + 1)
    if not content or len(content) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="The document must be between 1 byte and 8 MB")
    prompt = """Extract completed college courses and AP exams visible in this document.
Return JSON only: {"courses":[{"institution":"","code":"ABC 123","title":"","credits":3,"grade":"","status":"completed"}],"ap_exams":[{"exam":"AP Biology","score":4}],"warnings":[]}.
Include only clearly visible records. Exclude courses marked in progress, withdrawn, failed, or planned. Never infer equivalency or official credit. Use null for unreadable credits and explain uncertainty in warnings."""
    client = make_gemini_client()
    part = types.Part.from_bytes(data=content, mime_type=document.content_type)
    response = client.models.generate_content(
        model=load_ai_settings().get("model", DEFAULT_MODEL),
        contents=[prompt, part],
    )
    result = parse_model_json(response.text or "")
    courses = []
    for item in (result.get("courses") or [])[:80]:
        if not isinstance(item, dict):
            continue
        code = " ".join(str(item.get("code") or "").upper().split())[:30]
        if not code:
            continue
        courses.append({
            "institution": str(item.get("institution") or "")[:120], "code": code,
            "title": str(item.get("title") or "")[:180], "credits": item.get("credits"),
            "grade": str(item.get("grade") or "")[:20], "include": True,
        })
    ap_exams = [item for item in (result.get("ap_exams") or [])[:20] if isinstance(item, dict)]
    warnings = [str(item)[:300] for item in (result.get("warnings") or [])[:10]]
    return {"courses": courses, "ap_exams": ap_exams, "warnings": warnings,
            "disclaimer": "Draft extraction only. Review every row; BMCC must evaluate official records and award applicable credit."}


@app.get("/login")
def login_page():
    return FileResponse("frontend/login.html")


@app.get("/downloads/macos-launcher")
def download_macos_launcher(_admin=Depends(require_admin)):
    return FileResponse(
        "frontend/downloads/AI_Academic_Advisement_Mac.zip",
        media_type="application/zip",
        filename="AI_Academic_Advisement_Mac.zip",
    )


@app.get("/downloads/windows-launcher")
def download_windows_launcher(_admin=Depends(require_admin)):
    return FileResponse(
        "frontend/downloads/AI_Academic_Advisement_Windows.zip",
        media_type="application/zip",
        filename="AI_Academic_Advisement_Windows.zip",
    )


@app.get("/cuny-beyond")
def serve_cuny_beyond():
    if not is_cuny_beyond_enabled():
        raise HTTPException(status_code=404, detail="CUNY Beyond is not enabled")
    return FileResponse("frontend/cuny_beyond.html")


@app.get("/cuny-beyond/referral")
def serve_cuny_beyond_referral():
    if not is_cuny_beyond_enabled():
        raise HTTPException(status_code=404, detail="CUNY Beyond is not enabled")
    return FileResponse("frontend/cuny_beyond_referral.html")


@app.get("/api/cuny-beyond/config")
def get_cuny_beyond_config():
    if not is_cuny_beyond_enabled():
        raise HTTPException(status_code=404, detail="CUNY Beyond is not enabled")
    return public_config()


def clean_referral_summary(raw):
    """Keep only expected planning fields and bound every public-input collection."""
    def text_value(value, limit=500):
        return str(value or "").strip()[:limit]

    schedule = raw.get("schedule_checklist") or {}
    if not isinstance(schedule, dict):
        schedule = {}
    return {
        "pathway": text_value(raw.get("pathway"), 100),
        "career_goal": text_value(raw.get("career_goal"), 240),
        "matched_career": text_value(raw.get("matched_career"), 120),
        "skills": [text_value(item, 100) for item in (raw.get("skills") or [])[:5]],
        "recommended_programs": [
            {"code": text_value(item.get("code"), 30), "name": text_value(item.get("name"), 160), "explanation": text_value(item.get("explanation"), 700)}
            for item in (raw.get("recommended_programs") or [])[:3] if isinstance(item, dict)
        ],
        "cpl_possibilities": [
            {"name": text_value(item.get("name"), 160), "next_step": text_value(item.get("next_step"), 500)}
            for item in (raw.get("cpl_possibilities") or [])[:9] if isinstance(item, dict)
        ],
        "completed_courses": [text_value(item.get("code") if isinstance(item, dict) else item, 30) for item in (raw.get("completed_courses") or [])[:80]],
        "transfer_options": [text_value(item.get("next_step") if isinstance(item, dict) else item, 300) for item in (raw.get("transfer_options") or [])[:3]],
        "schedule_checklist": [text_value(item, 200) for item in (schedule.get("instructions") or [])[:8]],
    }


def referral_email_body(name, last_four, summary):
    programs = "; ".join(f"{item['name']} ({item['code']})" for item in summary["recommended_programs"]) or "None recorded"
    cpl = "; ".join(item["name"] for item in summary["cpl_possibilities"]) or "None recorded"
    completed = ", ".join(summary["completed_courses"]) or "None supplied"
    schedule = "\n".join(f"- {item}" for item in summary["schedule_checklist"]) or "- No schedule checklist saved"
    return f"""Pre-advisement request from {name}

Student-entered last four ID digits: {last_four or 'Not provided'}
Pathway: {summary['pathway'] or 'Not provided'}
Career goal: {summary['career_goal'] or 'Not provided'}
Matched career: {summary['matched_career'] or 'Not available'}
Skills: {', '.join(summary['skills']) or 'None supplied'}
Recommended BMCC programs: {programs}
Possible CPL topics requiring evaluation: {cpl}
Completed coursework summary: {completed}

Schedule-search checklist:
{schedule}

Requested next step: Please review this planning summary with the student. This automated package is not an official degree audit, CPL award, transfer-credit evaluation, registration action, or major-change approval.
""".strip()


def log_referral_delivery(event_id, status, delivery_mode):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with REFERRAL_LOG_FILE.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"event_id": event_id, "timestamp": datetime.now(timezone.utc).isoformat(), "status": status, "delivery_mode": delivery_mode}) + "\n")


@app.post("/api/cuny-beyond/referral")
def submit_cuny_beyond_referral(payload: AdvisingReferralPayload):
    event_id = str(uuid.uuid4())
    if payload.website:
        log_referral_delivery(event_id, "rejected", "honeypot")
        raise HTTPException(status_code=400, detail="Referral could not be submitted")
    name = payload.name.strip()[:120]
    email = payload.email.strip()[:254]
    last_four = (payload.id_last_four or "").strip()
    if len(name) < 2 or not EMAIL_PATTERN.fullmatch(email):
        raise HTTPException(status_code=422, detail="Enter a valid name and email")
    if last_four and not re.fullmatch(r"\d{4}", last_four):
        raise HTTPException(status_code=422, detail="Last four ID digits must be four numbers or blank")
    if not payload.consent:
        raise HTTPException(status_code=422, detail="Consent is required before sending")

    summary = clean_referral_summary(payload.summary)
    subject = f"CUNY Beyond pre-advisement request - {summary['career_goal'] or 'program exploration'}"[:160]
    body = referral_email_body(name, last_four, summary)
    recipient = os.environ.get("BMCC_ADVISING_REFERRAL_EMAIL", "").strip()
    enabled = os.environ.get("BMCC_ADVISING_REFERRAL_ENABLED", "false").lower() == "true"
    host = os.environ.get("SMTP_HOST", "").strip()

    if enabled and recipient and host:
        try:
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = os.environ.get("SMTP_FROM", recipient)
            message["To"] = recipient
            message["Cc"] = email
            message.set_content(body)
            port = int(os.environ.get("SMTP_PORT", "587"))
            with smtplib.SMTP(host, port, timeout=20) as client:
                client.starttls()
                username = os.environ.get("SMTP_USERNAME", "")
                if username:
                    client.login(username, os.environ.get("SMTP_PASSWORD", ""))
                client.send_message(message)
            log_referral_delivery(event_id, "sent", "smtp")
            return {"sent": True, "event_id": event_id, "message": "Referral sent to advising and copied to the student."}
        except Exception:
            log_referral_delivery(event_id, "failed", "smtp")
    else:
        log_referral_delivery(event_id, "prepared", "manual_fallback")

    return {
        "sent": False, "event_id": event_id,
        "message": "Automatic delivery is unavailable. Download the summary or copy the prepared email below.",
        "subject": subject, "body": body,
        "advisor_contact_url": "https://www.bmcc.cuny.edu/academics/advisement/advisement/",
    }


@app.post("/login")
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    account = authenticate(username, password)
    if account:
        request.session["logged_in"] = True
        request.session.update(account)
        return RedirectResponse("/program-selector", status_code=303)

    return RedirectResponse("/login?error=1", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/api/session")
def session_info(request: Request):
    if not is_logged_in(request):
        raise HTTPException(status_code=401, detail="Not logged in")
    return {
        "username": request.session.get("username"),
        "role": request.session.get("role", "tester"),
        "is_admin": is_admin(request),
    }


@app.get("/")
def serve_home():
    """Use the public chatbot as the application's primary entry point."""
    if not is_cuny_beyond_enabled():
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/cuny_beyond.html")


@app.get("/progress")
def serve_progress(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=303)
    return RedirectResponse("/program-selector", status_code=303)




@app.get("/program-selector")
def serve_program_selector(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/program_selector.html")

@app.get("/db-progress")
def serve_db_progress(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/db_progress_graph.html")




@app.get("/transfer-analysis")
def serve_transfer_analysis(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/transfer_analysis.html")


@app.get("/schedule-handoff")
def serve_schedule_handoff(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/schedule_handoff.html")


@app.get("/careers")
def serve_careers(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/careers.html")


@app.get("/admin")
def serve_admin(request: Request):
    if not is_admin(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/admin_dashboard.html")


@app.get("/admin/ai-settings")
def serve_ai_settings(request: Request):
    if not is_admin(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/ai_settings.html")


@app.get("/admin/major-constructor")
def serve_major_constructor(request: Request):
    if not is_admin(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/major_constructor.html")


@app.get("/admin/schedule-settings")
def serve_schedule_settings(request: Request):
    if not is_admin(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/schedule_settings.html")


@app.get("/admin/cuny-beyond-governance")
def serve_cuny_beyond_governance(request: Request):
    if not is_admin(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/governance_dashboard.html")


@app.get("/admin/curriculum-graph")
def serve_curriculum_graph_admin(request: Request):
    if not is_admin(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/curriculum_graph_admin.html")


app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.mount("/docs", StaticFiles(directory="docs"), name="docs")


@app.get("/api/admin/ai-settings")
def get_ai_settings(request: Request):
    require_admin(request)
    return public_ai_settings(load_ai_settings())


@app.put("/api/admin/ai-settings")
def update_ai_settings(request: Request, payload: AISettingsPayload):
    require_admin(request)

    current = load_ai_settings()
    new_settings = payload.model_dump()

    # Blank API key means keep the current saved key / env key.
    if not payload.api_key:
        new_settings["api_key"] = current.get("api_key", "")

    save_ai_settings(new_settings)
    return public_ai_settings(new_settings)


@app.get("/api/admin/ai-embed-snippet")
def get_ai_embed_snippet(request: Request):
    require_admin(request)

    settings = load_ai_settings()
    agent_id = settings.get("agent_id", "advisor_progress")

    snippet = f'''<link rel="stylesheet" href="/frontend/reusable_ai_advisor/ai_advisor_widget.css">
<script src="/frontend/reusable_ai_advisor/ai_advisor_widget.js"></script>

<button id="aiAdvisorButton">Ask AI Advisor</button>

<script>
initAIAdvisorWidget({{
  agentId: "{agent_id}",
  mountButtonSelector: "#aiAdvisorButton",
  endpoint: "/ai-agent-ask",
  pageName: document.title,
  pageUrl: window.location.pathname,
  contextProvider: function() {{
    // Replace this with page-specific context.
    return {{
      page_title: document.title,
      page_url: window.location.pathname,
      visible_text: document.body.innerText.slice(0, 5000)
    }};
  }}
}});
</script>'''

    return {"snippet": snippet}


@app.post("/fallback-ask")
def fallback_ask(payload: FallbackRequest):
    settings = load_ai_settings()
    client = make_gemini_client()
    model = settings.get("model", DEFAULT_MODEL)

    candidates_text = "\n\n".join(
        [
            f"Candidate {i + 1}\nQuestion: {c.question}\nAnswer: {c.answer}\nScore: {c.score:.3f}"
            for i, c in enumerate(payload.candidates)
        ]
    )

    prompt = f"""
You are a strict academic advising FAQ selector.

The user asked:
{payload.user_question}

Selected major:
{payload.major}

Detected courses:
{", ".join(payload.detected_courses) if payload.detected_courses else "none"}

Detected intent:
{payload.detected_intent}

You may ONLY answer using one of the candidate FAQ answers below.

Do not invent requirements, prerequisites, policies, transfer rules, or exceptions.

If none of the candidate answers clearly answer the user's question, respond exactly:
I don't have enough information in the FAQ to answer that.

Candidates:
{candidates_text}

Return the best answer only.
""".strip()

    response = client.models.generate_content(model=model, contents=prompt)
    return {"answer": "[GEMINI API ACTIVE]\n\n" + (response.text or "")}


def run_contextual_agent(request: Request, user_question: str, page_context: dict, page_name: Optional[str] = None, page_url: Optional[str] = None, agent_id: str = "advisor_progress"):
    settings = load_ai_settings()
    client = make_gemini_client()
    model = settings.get("model", DEFAULT_MODEL)
    system_prompt = settings.get("system_prompt", DEFAULT_AGENT_PROMPT)

    started_at = time.perf_counter()
    timestamp = datetime.now(timezone.utc).isoformat()
    client_ip = get_client_ip(request)

    context_text = json.dumps(page_context, ensure_ascii=False, indent=2)

    prompt = f"""
{system_prompt}

Agent ID: {agent_id}
Page name: {page_name or settings.get('page_name')}
Page URL: {page_url or settings.get('page_url')}

User question:
{user_question}

Current page context JSON:
{context_text}

Answer the user directly.
""".strip()

    response = client.models.generate_content(model=model, contents=prompt)
    response_time_ms = round((time.perf_counter() - started_at) * 1000)
    usage = extract_usage_metadata(response)
    usage["response_time_ms"] = response_time_ms
    usage["model"] = model

    answer = response.text or ""

    write_advisor_log({
        "timestamp": timestamp,
        "ip": client_ip,
        "agent_id": agent_id,
        "page_name": page_name or settings.get("page_name"),
        "page_url": page_url or settings.get("page_url"),
        "model": model,
        "question": user_question,
        "answer": answer,
        "usage": usage,
        "page_context_summary": {
            "program": page_context.get("program"),
            "completed_courses": page_context.get("completed_courses"),
            "recommended_courses": page_context.get("recommended_courses"),
            "recommended_total_credits": page_context.get("recommended_total_credits"),
        },
    })

    return {"answer": answer, "usage": usage if settings.get("show_metrics", True) else None}


@app.post("/progress-advisor-ask")
def progress_advisor_ask(request: Request, payload: ProgressAdvisorRequest):
    return run_contextual_agent(
        request=request,
        user_question=payload.user_question,
        page_context=payload.page_context,
        page_name="Degree Progress",
        page_url="/db-progress",
        agent_id="advisor_progress",
    )


@app.post("/ai-agent-ask")
def ai_agent_ask(request: Request, payload: GenericAgentRequest):
    return run_contextual_agent(
        request=request,
        user_question=payload.user_question,
        page_context=payload.page_context,
        page_name=payload.page_name,
        page_url=payload.page_url,
        agent_id=payload.agent_id or "advisor_progress",
    )


@app.get("/api/db/advisor-logs")
def get_advisor_logs(limit: int = 100):
    if not LOG_FILE.exists():
        return []

    try:
        lines = LOG_FILE.read_text(encoding="utf-8").splitlines()[-limit:]
        records = []

        for line in reversed(lines):
            try:
                record = json.loads(line)
                usage = record.get("usage", {})
                records.append({
                    "timestamp": record.get("timestamp"),
                    "ip": record.get("ip"),
                    "agent_id": record.get("agent_id"),
                    "page_name": record.get("page_name"),
                    "page_url": record.get("page_url"),
                    "model": record.get("model"),
                    "question": record.get("question"),
                    "answer": record.get("answer"),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                    "response_time_ms": usage.get("response_time_ms"),
                })
            except json.JSONDecodeError:
                continue

        return records
    except Exception as exc:
        return {"error": f"Could not read advisor logs: {exc}"}


@app.get("/health")
def health():
    settings = load_ai_settings()
    return {
        "status": "ok",
        "model": settings.get("model", DEFAULT_MODEL),
        "api_key_configured": bool(get_gemini_api_key()),
    }
