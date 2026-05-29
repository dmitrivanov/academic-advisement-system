from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = "gemini-2.0-flash"

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


@app.get("/")
def root():
    return {"status": "Gemini fallback API is running"}


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
Do not invent prerequisites, degree requirements, course policies, or exceptions.
If none of the candidate answers clearly answer the user's question, respond exactly:
I don't have enough information in the FAQ to answer that.

Candidates:
{candidates_text}

Return the best answer only. Do not explain your reasoning.
""".strip()

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    return {"answer": "[GEMINI API ACTIVE]\n\n" + response.text}