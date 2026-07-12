# MaSoVa Voice Support Demo

Browser-based voice support demo: speak into your mic, the MaSoVa AI agent answers using RAG over real platform data, and Voicebox speaks the reply back.

**Stack:** Voicebox (STT + TTS) · Groq llama-3.1-8b-instant (LLM) · nomic-embed-text-v1.5 local (embeddings) · Qdrant (vector DB) · n8n (orchestration)

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

---

## Setup

### 1. Create `.env`

```
GROQ_API_KEY=your_groq_key_here
```

### 2. Start n8n + Qdrant

```bash
docker compose up -d
```

### 3. Install Python deps

```bash
pip install -r requirements.txt
```

> First run downloads the embedding model (~400MB). Cached after that.

### 4. Start the local embed server (keep this terminal open)

```bash
python qdrant/embed_server.py
```

Wait for: `Model loaded. Listening on http://localhost:17494`

### 5. Ingest the knowledge base (one-time)

```bash
python qdrant/ingest.py
```

Expected output:
```
Collection 'masova_kb' created (size=768)
  contact.md: 1 chunks ingested
  demo-users.md: 2 chunks ingested
  ...
Done. ~20 total chunks in 'masova_kb'
```

### 6. Import the n8n workflow

1. Open http://localhost:5678
2. Click **+** → **...** → **Import from file** → select `n8n/workflow.json`
3. Click the **Activate** toggle (top right)

### 7. Serve the UI

```bash
cd ui
python -m http.server 8080
```

Open http://localhost:8080 in Chrome or Edge.

---

## Services at a glance

| Service | URL | How to start |
|---|---|---|
| Demo UI | http://localhost:8080 | `cd ui && python -m http.server 8080` |
| Embed server | http://localhost:17494 | `python qdrant/embed_server.py` |
| n8n | http://localhost:5678 | `docker compose up -d` |
| Qdrant | http://localhost:6333 | `docker compose up -d` |
| Voicebox | http://localhost:17493 | Start Voicebox app |
| masova-support | http://localhost:8000 | `uvicorn ...` in masova-support repo |

---

## Usage

1. Make sure all 5 services are running
2. Open http://localhost:8080 in Chrome or Edge
3. Click **Start Call** and allow mic access
4. Speak — e.g. *"What's on the menu?"* or *"Where is order SEED-ORD-OFD-1?"*
5. Wait for the agent to speak the answer back
6. Keep talking — conversation history is preserved per session

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Mic access denied" | Must serve via `python -m http.server`, not open as `file://` |
| n8n errors at Embed step | Make sure `python qdrant/embed_server.py` is running |
| n8n errors at Agent step | Start masova-support on port 8000 |
| No audio playback | Voicebox must be running at http://localhost:17493 |
| Qdrant empty | Run `python qdrant/ingest.py` after starting Qdrant |
