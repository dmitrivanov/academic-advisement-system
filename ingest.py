from pathlib import Path
from pypdf import PdfReader
import chromadb
import requests

DOCS_DIR = Path("docs")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "advisement_docs"
EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


def read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def get_embedding(text: str):
    r = requests.post(
        EMBED_URL,
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    return data["embedding"]


def main():
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(name=COLLECTION_NAME)

    doc_id = 1

    for path in DOCS_DIR.iterdir():
        if path.suffix.lower() == ".txt":
            text = read_txt(path)
        elif path.suffix.lower() == ".pdf":
            text = read_pdf(path)
        else:
            continue

        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if not chunk:
                continue

            embedding = get_embedding(chunk)

            collection.add(
                ids=[f"doc_{doc_id}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": path.name, "chunk": i}]
            )
            doc_id += 1

    print("Indexing complete.")


if __name__ == "__main__":
    main()