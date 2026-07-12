"""
Ingests docs/kb/*.md into Qdrant collection 'masova_kb'.
Chunks at ~1800 chars with 200-char overlap.
Embeds via Groq nomic-embed-text-v1.5 (free tier).
Run: python qdrant/ingest.py
"""

import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    sys.exit("ERROR: GROQ_API_KEY not set. Add it to .env or set the environment variable.")

QDRANT_URL = "http://localhost:6333"
COLLECTION = "masova_kb"
EMBED_MODEL = "nomic-embed-text-v1.5"
VECTOR_SIZE = 768
CHUNK_CHARS = 1800
OVERLAP_CHARS = 200

assert CHUNK_CHARS > OVERLAP_CHARS

groq_client = Groq(api_key=GROQ_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL)


def embed(text: str) -> list[float]:
    response = groq_client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding


def chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + CHUNK_CHARS].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_CHARS - OVERLAP_CHARS
    return chunks


def _chunk_id(filename: str, index: int) -> str:
    """Deterministic UUID — re-running upserts instead of duplicating."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{filename}:{index}"))


def ensure_collection():
    existing = {c.name for c in qdrant.get_collections().collections}
    if COLLECTION in existing:
        info = qdrant.get_collection(COLLECTION)
        actual_size = info.config.params.vectors.size
        if actual_size != VECTOR_SIZE:
            print(
                f"WARNING: existing collection has size {actual_size}, "
                f"expected {VECTOR_SIZE}. Recreating."
            )
            qdrant.delete_collection(COLLECTION)
        else:
            print(f"Collection '{COLLECTION}' exists (size={actual_size}) — upserting")
            return
    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Created collection '{COLLECTION}' (size={VECTOR_SIZE})")


def ingest_file(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  SKIP {path.name}: cannot read — {e}")
        return 0

    chunks = chunk_text(text)
    points = []
    for i, chunk in enumerate(chunks):
        try:
            vector = embed(chunk)
        except Exception as e:
            print(f"  SKIP {path.name} chunk {i}: embed failed — {e}")
            continue
        points.append(
            PointStruct(
                id=_chunk_id(path.name, i),
                vector=vector,
                payload={"source": path.name, "chunk_index": i, "text": chunk},
            )
        )

    if points:
        qdrant.upsert(collection_name=COLLECTION, points=points)
    return len(points)


def main():
    kb_dir = Path(__file__).parent.parent / "docs" / "kb"
    md_files = sorted(kb_dir.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {kb_dir}", file=sys.stderr)
        sys.exit(1)

    ensure_collection()

    total = 0
    for f in md_files:
        count = ingest_file(f)
        print(f"  {f.name}: {count} chunks ingested")
        total += count

    print(f"\nDone. {total} total chunks in '{COLLECTION}'")
    info = qdrant.get_collection(COLLECTION)
    points_count = info.points_count if info.points_count is not None else info.vectors_count
    print(f"Qdrant collection points count: {points_count}")


if __name__ == "__main__":
    main()
