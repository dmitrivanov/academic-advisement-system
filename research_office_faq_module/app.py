from __future__ import annotations

import csv
import math
import os
import re
import sqlite3
from collections import Counter
from pathlib import Path

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DB_PATH = DATA / "research_faq.db"
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

app = FastAPI(title="BMCC Research Office FAQ Prototype")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class ChatRequest(BaseModel):
    message: str
    use_ai: bool = True


class FAQInput(BaseModel):
    category: str
    question: str
    answer: str
    keywords: str = ""
    source_url: str = ""
    active: bool = True


def db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    DATA.mkdir(exist_ok=True)
    with db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                keywords TEXT NOT NULL DEFAULT '',
                source_url TEXT NOT NULL DEFAULT '',
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
        if count == 0:
            with (DATA / "seed_faqs.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            conn.executemany(
                "INSERT INTO faqs(category,question,answer,keywords,source_url) VALUES(?,?,?,?,?)",
                [(r["category"], r["question"], r["answer"], r["keywords"], r["source_url"]) for r in rows],
            )


TOKEN_RE = re.compile(r"[a-z0-9]+")
STOP = {"a", "an", "and", "are", "can", "do", "for", "how", "i", "in", "is", "it", "me", "my", "of", "the", "to", "what", "when", "where", "will"}


def tokens(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOP and len(t) > 1]


def retrieve(message: str, limit: int = 4):
    with db() as conn:
        rows = [dict(r) for r in conn.execute("SELECT * FROM faqs WHERE active=1")]
    documents = [tokens(f'{r["question"]} {r["keywords"]} {r["category"]}') for r in rows]
    query = Counter(tokens(message))
    if not query:
        return []
    document_frequency = Counter(token for doc in documents for token in set(doc))
    scored = []
    for row, doc in zip(rows, documents):
        counts = Counter(doc)
        score = sum(query[t] * counts[t] * (1 + math.log((len(rows) + 1) / (document_frequency[t] + 1))) for t in query)
        phrase_bonus = 2.5 if message.lower().strip(" ?") in row["question"].lower() else 0
        scored.append((score + phrase_bonus, row))
    return [(round(score, 3), row) for score, row in sorted(scored, key=lambda item: item[0], reverse=True)[:limit] if score > 0]


def ai_answer(message: str, matches) -> str | None:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or not matches:
        return None
    try:
        from google import genai
        evidence = "\n\n".join(f'FAQ: {row["question"]}\nANSWER: {row["answer"]}' for _, row in matches)
        prompt = f"""You are the BMCC Research Office FAQ assistant.
Answer the student's question using ONLY the approved FAQ evidence below.
Do not add policies, dates, eligibility rules, links, or facts that are absent.
If the evidence does not answer the question, say you do not have a reviewed answer and suggest contacting the Research Office.
Keep the answer under 130 words and friendly.

STUDENT: {message}

APPROVED EVIDENCE:
{evidence}"""
        client = genai.Client(api_key=key)
        response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite"), contents=prompt)
        return (response.text or "").strip() or None
    except Exception:
        return None


def check_admin(password: str | None) -> None:
    expected = os.getenv("ADMIN_PASSWORD", "change-this-before-sharing")
    if not password or password != expected:
        raise HTTPException(401, "Incorrect admin password")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
def health():
    with db() as conn:
        faq_count = conn.execute("SELECT COUNT(*) FROM faqs WHERE active=1").fetchone()[0]
    return {"status": "ok", "active_faqs": faq_count}


@app.get("/admin")
def admin():
    return FileResponse(ROOT / "static" / "admin.html")


@app.get("/api/suggestions")
def suggestions():
    with db() as conn:
        rows = conn.execute("SELECT question,category FROM faqs WHERE active=1 ORDER BY category,id LIMIT 12").fetchall()
    return [dict(r) for r in rows]


@app.post("/api/chat")
def chat(payload: ChatRequest):
    message = payload.message.strip()
    if not message:
        raise HTTPException(400, "Please enter a question")
    matches = retrieve(message)
    best_score = matches[0][0] if matches else 0
    if not matches or best_score < 0.55:
        return {"answer": "I do not have a reviewed answer for that yet. Please try a question about CRSP, BFF, CSTEP, mentors, eligibility, stipends, applications, or presentations—or contact the BMCC Office of Research.", "confidence": "low", "sources": [], "mode": "reviewed-only"}
    generated = ai_answer(message, matches) if payload.use_ai else None
    selected = matches[0][1]
    answer = generated or selected["answer"]
    sources = [{"label": row["question"], "url": row["source_url"]} for _, row in matches[:2] if row["source_url"]]
    return {"answer": answer, "confidence": "high" if best_score >= 2 else "medium", "sources": sources, "mode": "AI grounded in reviewed FAQs" if generated else "deterministic FAQ match"}


@app.get("/api/admin/faqs")
def list_faqs(q: str = "", x_admin_password: str | None = Header(default=None)):
    check_admin(x_admin_password)
    with db() as conn:
        if q:
            term = f"%{q}%"
            rows = conn.execute("SELECT * FROM faqs WHERE question LIKE ? OR answer LIKE ? OR category LIKE ? ORDER BY category,question", (term, term, term)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM faqs ORDER BY category,question").fetchall()
    return [dict(r) for r in rows]


@app.post("/api/admin/faqs")
def add_faq(item: FAQInput, x_admin_password: str | None = Header(default=None)):
    check_admin(x_admin_password)
    with db() as conn:
        cursor = conn.execute("INSERT INTO faqs(category,question,answer,keywords,source_url,active) VALUES(?,?,?,?,?,?)", (item.category, item.question, item.answer, item.keywords, item.source_url, int(item.active)))
    return {"id": cursor.lastrowid}


@app.put("/api/admin/faqs/{faq_id}")
def update_faq(faq_id: int, item: FAQInput, x_admin_password: str | None = Header(default=None)):
    check_admin(x_admin_password)
    with db() as conn:
        cursor = conn.execute("UPDATE faqs SET category=?,question=?,answer=?,keywords=?,source_url=?,active=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (item.category, item.question, item.answer, item.keywords, item.source_url, int(item.active), faq_id))
    if not cursor.rowcount:
        raise HTTPException(404, "FAQ not found")
    return {"ok": True}


@app.delete("/api/admin/faqs/{faq_id}")
def delete_faq(faq_id: int, x_admin_password: str | None = Header(default=None)):
    check_admin(x_admin_password)
    with db() as conn:
        conn.execute("DELETE FROM faqs WHERE id=?", (faq_id,))
    return {"ok": True}


@app.post("/api/admin/import")
async def import_faqs(file: UploadFile = File(...), x_admin_password: str | None = Header(default=None)):
    check_admin(x_admin_password)
    text = (await file.read()).decode("utf-8-sig")
    rows = list(csv.DictReader(text.splitlines()))
    required = {"category", "question", "answer"}
    if not rows or not required.issubset(rows[0]):
        raise HTTPException(400, "CSV must contain category, question, and answer columns")
    values = [(r["category"].strip(), r["question"].strip(), r["answer"].strip(), r.get("keywords", "").strip(), r.get("source_url", "").strip()) for r in rows if r["question"].strip() and r["answer"].strip()]
    with db() as conn:
        conn.executemany("INSERT INTO faqs(category,question,answer,keywords,source_url) VALUES(?,?,?,?,?)", values)
    return {"imported": len(values)}


init_db()
