"""
Ingests docs/kb/*.md into Qdrant collection 'masova_kb'.
Chunks at ~500 tokens with 50-token overlap.
Embeds via Groq llama-3.1-8b-instant (free tier).
Run: python qdrant/ingest.py
"""

import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct
)

load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
QDRANT_URL = "http://localhost:6333"
COLLECTION = "masova_kb"
EMBED_MODEL = "llama-3.1-8b-instant"
VECTOR_SIZE = 4096
CHUNK_CHARS = 1800
OVERLAP_CHARS = 200

groq_client = Groq(api_key=GROQ_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL)


def embed(text: str) -> list[float]:
    response = groq_client.embeddings.create(
        model=EMBED_MODEL,
        input=text,
    )
    return response.data[0].embedding


def chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_CHARS
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += CHUNK_CHARS - OVERLAP_CHARS
    return chunks


def ensure_collection():
    existing = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION in existing:
        print(f"Collection '{COLLECTION}' already exists — upserting")
        return
    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Created collection '{COLLECTION}'")


def ingest_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    chunks = chunk_text(text)
    points = []
    for i, chunk in enumerate(chunks):
        vector = embed(chunk)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "source": path.name,
                "chunk_index": i,
                "text": chunk,
            }
        ))
    qdrant.upsert(collection_name=COLLECTION, points=points)
    return len(points)


def main():
    kb_dir = Path(__file__).parent.parent / "docs" / "kb"
    md_files = sorted(kb_dir.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {kb_dir}")
        return

    ensure_collection()

    total = 0
    for f in md_files:
        count = ingest_file(f)
        print(f"  {f.name}: {count} chunks ingested")
        total += count

    print(f"\nDone. {total} total chunks in '{COLLECTION}'")
    info = qdrant.get_collection(COLLECTION)
    print(f"Qdrant collection vectors count: {info.vectors_count}")


if __name__ == "__main__":
    main()
