#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 16:57:34 2026

@author: dmitriiivanov
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"


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


@app.post("/fallback-ask")
def fallback_ask(payload: FallbackRequest):
    candidates_text = "\n\n".join(
        [
            f"Candidate {i+1}\nQuestion: {c.question}\nAnswer: {c.answer}\nScore: {c.score}"
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
Do not invent new prerequisites, requirements, policies, or course rules.
If none of the candidate answers clearly answer the user's question, respond exactly:
I don't have enough information in the FAQ to answer that.

Candidates:
{candidates_text}

Return the best answer only. Do not explain your reasoning.
""".strip()

    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120,
    )
    r.raise_for_status()

    return {
        "answer": r.json()["response"]
    }