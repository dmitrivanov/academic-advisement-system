from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import chromadb
import requests
import shutil
import sys
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = str(BASE_DIR / "chroma_db")
COLLECTION_NAME = "advisement_docs"

EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

GEN_URL = "http://localhost:11434/api/generate"
GEN_MODEL = "llama3.2"

DOCS_DIR.mkdir(exist_ok=True)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list


def get_embedding(text: str):
    r = requests.post(
        EMBED_URL,
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["embedding"]


def retrieve_context(question: str, top_k: int = 4):
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)

    q_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=top_k
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    return docs, metas


def generate_answer(question: str, docs: list):
    context = "\n\n---\n\n".join(docs)

    prompt = f"""
You are an academic advisement assistant.

Answer ONLY using the context below.
If the answer is not clearly contained in the context, say:
"I don't have enough information in the uploaded advisement documents."

Do not guess.
Do not invent prerequisites, policies, or degree requirements.

Context:
{context}

Question:
{question}

Answer:
""".strip()

    r = requests.post(
        GEN_URL,
        json={
            "model": GEN_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["response"]


@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):
    docs, metas = retrieve_context(payload.question)
    answer = generate_answer(payload.question, docs)

    sources = []
    for m in metas:
        sources.append({
            "source": m.get("source"),
            "chunk": m.get("chunk")
        })

    return AskResponse(answer=answer, sources=sources)


@app.get("/files")
def list_files():
    files = []
    for path in sorted(DOCS_DIR.iterdir()):
        if path.is_file():
            files.append({
                "name": path.name,
                "type": path.suffix.lower().lstrip("."),
                "size": f"{round(path.stat().st_size / 1024, 1)} KB"
            })
    return {"files": files}


@app.post("/upload-docs")
def upload_docs(files: list[UploadFile] = File(...)):
    saved = []

    for upload in files:
        suffix = Path(upload.filename).suffix.lower()
        if suffix not in [".pdf", ".txt"]:
            continue

        target = DOCS_DIR / Path(upload.filename).name
        with target.open("wb") as f:
            shutil.copyfileobj(upload.file, f)

        saved.append(target.name)

    return {
        "message": f"Saved {len(saved)} file(s).",
        "files": saved
    }


@app.post("/reindex")
def reindex_docs():
    try:
        result = subprocess.run(
            [sys.executable, "ingest.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            return {
                "message": "Reindex failed.",
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        return {
            "message": "Reindex complete.",
            "stdout": result.stdout.strip()
        }

    except Exception as e:
        return {
            "message": f"Reindex failed: {str(e)}"
        }