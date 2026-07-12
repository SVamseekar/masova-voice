# MaSoVa Voice Support Demo

Browser-based voice support demo: speak into your mic, the MaSoVa AI agent answers using RAG over real platform data, and Voicebox speaks the reply back.

**Stack:** Voicebox (STT + TTS) · Groq llama-3.1-8b-instant (LLM) · Nomic nomic-embed-text-v1.5 (embeddings) · Qdrant (vector DB) · n8n (orchestration)

> **Demo only — localhost, no authentication. Do not expose to the internet.**

---

## Prerequisites

| What | How |
|---|---|
| **Voicebox** | Download from https://voicebox.sh/download/windows and start it — API at http://localhost:17493 |
| **masova-support** | `uvicorn src.masova_agent.main:app --host 0.0.0.0 --port 8000` in the masova-support repo |
| **Docker Desktop** | Installed and running |
| **Python 3.11+** | Installed |
| **Groq API key** | Free at https://console.groq.com |
| **Nomic API key** | Free at https://atlas.nomic.ai |

---

## Setup

### 1. Create `.env`

```
GROQ_API_KEY=your_groq_key_here
NOMIC_API_KEY=your_nomic_key_here
```

### 2. Start n8n + Qdrant

```bash
docker compose up -d
```

Docker Compose auto-loads `.env` and passes both keys into the n8n container.

### 3. Install Python deps and ingest KB

```bash
pip install -r requirements.txt
python qdrant/ingest.py
```

Expected output:
```
Created collection 'masova_kb' (size=768)
  contact.md: 1 chunks ingested
  demo-users.md: 2 chunks ingested
  ...
Done. ~20 total chunks in 'masova_kb'
```

### 4. Import the n8n workflow

1. Open http://localhost:5678
2. Click **+** → **...** → **Import from file** → select `n8n/workflow.json`
3. Click the **Activate** toggle (top right)

### 5. Serve the UI

Chrome requires a secure context for mic access. Serve the UI over HTTP instead of opening as `file://`:

```bash
cd ui
python -m http.server 8080
```

Then open http://localhost:8080 in Chrome or Edge.

---

## Services

| Service | URL |
|---|---|
| Demo UI | http://localhost:8080 (via `python -m http.server`) |
| n8n | http://localhost:5678 |
| Qdrant | http://localhost:6333 |
| Voicebox API | http://localhost:17493/docs |
| masova-support | http://localhost:8000 |

---

## Usage

1. Make sure all services are running (Voicebox, masova-support, n8n, Qdrant)
2. Open http://localhost:8080 in Chrome or Edge
3. Click **Start Call** and allow mic access
4. Speak — e.g. *"What's on the menu?"* or *"Where is order SEED-ORD-OFD-1?"*
5. Wait for the agent to speak the answer back
6. Keep talking — conversation history is preserved per session

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Mic access denied" | Serve via `python -m http.server`, not `file://` |
| n8n workflow errors at Embed step | Check `NOMIC_API_KEY` is in `.env` and `docker compose up -d` was re-run after creating `.env` |
| n8n workflow errors at Agent step | Start masova-support on port 8000 |
| No audio playback | Voicebox must be running at http://localhost:17493 |
| Qdrant empty | Run `python qdrant/ingest.py` after starting Qdrant |
