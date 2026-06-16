
from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from google import genai
import os
import json

from api_db_routes import router as db_router


app = FastAPI()
app.include_router(db_router)

SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-secret-change-this")

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def is_logged_in(request: Request):
    return request.session.get("logged_in") is True


MODEL = "gemini-2.5-flash"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

client = genai.Client(api_key=GEMINI_API_KEY)


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


@app.get("/login")
def login_page():
    return FileResponse("frontend/login.html")


@app.post("/login")
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    app_username = os.environ.get("APP_USERNAME", "admin")
    app_password = os.environ.get("APP_PASSWORD", "admin")

    if username == app_username and password == app_password:
        request.session["logged_in"] = True
        request.session["username"] = username
        return RedirectResponse("/", status_code=303)

    return RedirectResponse("/login?error=1", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/")
def serve_home(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/faq_chat_hybrid.html")


@app.get("/progress")
def serve_progress(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=303)

    return RedirectResponse("/db-progress", status_code=303)


@app.get("/db-progress")
def serve_db_progress(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/db_progress_graph.html")


@app.get("/admin")
def serve_admin(request: Request):
    if not is_logged_in(request):
        return RedirectResponse("/login", status_code=303)
    return FileResponse("frontend/admin_dashboard.html")


app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.mount("/docs", StaticFiles(directory="docs"), name="docs")


@app.post("/fallback-ask")
def fallback_ask(payload: FallbackRequest):
    print("=== USING GEMINI FALLBACK ===")

    candidates_text = "\n\n".join(
        [
            f"Candidate {i + 1}\n"
            f"Question: {c.question}\n"
            f"Answer: {c.answer}\n"
            f"Score: {c.score:.3f}"
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

Do not invent:
- prerequisites
- degree requirements
- academic policies
- transfer rules
- course exceptions

If none of the candidate answers clearly answer the user's question, respond exactly:

I don't have enough information in the FAQ to answer that.

Candidates:
{candidates_text}

Return the best answer only.
Do not explain your reasoning.
""".strip()

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    return {
        "answer": "[GEMINI API ACTIVE]\n\n" + response.text
    }


@app.post("/progress-advisor-ask")
def progress_advisor_ask(payload: ProgressAdvisorRequest):
    print("=== USING PROGRESS PAGE ADVISOR ===")

    context_text = json.dumps(
        payload.page_context,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
You are an academic advising assistant inside a degree progress page.

Use ONLY the page context below. Do not invent official degree requirements, course policies, prerequisites, transfer rules, or exceptions.

If the page context does not contain enough information, say that clearly and suggest what information is missing.

Be practical and concise. Explain locked courses, completed courses, not-needed alternatives, elective completion, and next-semester recommendations when relevant.

The user asked:
{payload.user_question}

Current page context JSON:
{context_text}

Answer the user directly.
""".strip()

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    return {
        "answer": response.text
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": MODEL
    }