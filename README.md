# MaSoVa Voice Support Demo

Browser-based voice support demo using Voicebox MCP (STT+TTS), Groq LLM, Qdrant RAG, and n8n orchestration.

## Prerequisites

1. **Voicebox** running locally — download from https://voicebox.sh/download/windows, start it. API available at http://localhost:17493
2. **masova-support** running — `uvicorn src.masova_agent.main:app --host 0.0.0.0 --port 8000` from the masova-support repo
3. **Docker Desktop** installed and running
4. **Python 3.11+** installed
5. **Groq API key** (free at https://console.groq.com) — set in `.env`

## Setup

```bash
# 1. Start n8n + Qdrant
docker compose up -d

# 2. Create .env with your Groq key
echo "GROQ_API_KEY=your_key_here" > .env

# 3. Install Python deps
pip install -r requirements.txt

# 4. Ingest knowledge base into Qdrant
python qdrant/ingest.py

# 5. Import n8n workflow
# Open http://localhost:5678 → Settings → Import from file → select n8n/workflow.json

# 6. Open demo UI
# Open ui/index.html in your browser (Chrome/Edge recommended)
```

## Services

| Service | URL |
|---|---|
| Demo UI | Open `ui/index.html` directly in browser |
| n8n | http://localhost:5678 |
| Qdrant | http://localhost:6333 |
| Voicebox API | http://localhost:17493/docs |
| masova-support | http://localhost:8000 |

## Usage

1. Make sure all 4 services are running (Voicebox, masova-support, n8n, Qdrant)
2. Open `ui/index.html` in Chrome or Edge
3. Click **Start Call** and allow mic access
4. Speak a question — e.g. "What's on the menu?" or "Where is order SEED-ORD-OFD-1?"
5. Wait for the agent to respond — you'll hear the answer spoken back
6. Keep talking — conversation history is preserved per session
