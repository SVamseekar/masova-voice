# MaSoVa Voice Support Demo — Design Spec

**Date:** 2026-07-12  
**Status:** Approved for implementation  
**Scope:** Standalone demo — does not modify masova-platform, masova-support, masova-mobile, or MaSoVaDriverApp

---

## 1. Problem Statement

`masova-support` already delivers a capable AI customer support agent (Google ADK + Gemini, 8 tools, Redis sessions). It is text-only. This project adds a voice layer on top — a browser-based "Call Support" experience that lets a user speak to the agent and hear responses spoken back. No phone number, no cloud TTS cost, no changes to any existing repo.

---

## 2. Goals

- Voice input (mic) → Whisper STT via Voicebox MCP
- AI response via Groq `llama-3.1-8b-instant` (free tier)
- Voice output → Voicebox MCP TTS (`/speak`)
- RAG context from real MaSoVa platform data (menu, policies, FAQs, order lifecycle)
- n8n orchestrates the full pipeline locally
- Single standalone HTML demo UI — bare minimum, no framework
- Zero cost, zero cloud dependencies, fully local via Docker

---

## 3. What Is NOT Touched

| Repo / Folder | Status |
|---|---|
| `masova-platform/` | Read-only — source of truth for RAG docs |
| `masova-support/` | Read-only — agent called as black box |
| `masova-mobile/` | Not involved |
| `MaSoVaDriverApp/` | Not involved |

All new code lives in `D:/projects/masova-voice-demo/` only.

---

## 4. Architecture

```
Browser (index.html)
  │
  │  1. User clicks "Start Call"
  │  2. WebRTC captures mic audio
  │  3. On silence → POST audio blob to n8n webhook
  │
  ▼
n8n Workflow (Docker :5678)
  │
  ├── Node 1: Webhook — receives multipart audio
  │
  ├── Node 2: HTTP Request → Voicebox MCP
  │           POST http://localhost:17493/transcribe
  │           Returns: { text: "Where is my order?" }
  │
  ├── Node 3: HTTP Request → Qdrant
  │           POST http://localhost:6333/collections/masova_kb/points/search
  │           Embed query via Groq, retrieve top-3 context chunks
  │
  ├── Node 4: HTTP Request → masova-support agent
  │           POST http://localhost:8000/chat
  │           Body: { message, context (RAG chunks), session_id }
  │           Returns: { reply: "Your order SEED-ORD-OFD-1 is out for delivery..." }
  │
  ├── Node 5: HTTP Request → Voicebox MCP
  │           POST http://localhost:17493/speak
  │           Body: { text: reply }
  │           Returns: audio/mpeg binary
  │
  └── Node 6: Respond to Webhook
              Returns: audio binary + transcript JSON header
              
Browser plays audio, updates transcript panel
```

---

## 5. Components

### 5.1 Demo UI (`ui/index.html`)

Single HTML file, no build step, no framework.

**Elements:**
- MaSoVa logo + "Voice Support" heading
- "Start Call" button (green) / "End Call" button (red)
- Mic status indicator: `● Listening` / `⏳ Processing` / `🔊 Speaking`
- Transcript panel — scrollable, alternating user/agent bubbles
- Mute toggle button

**Behaviour:**
- `getUserMedia()` → MediaRecorder captures audio as `audio/webm`
- Voice activity detection via audio level threshold — stops recording after 1.5s silence
- Sends `FormData` with audio blob to `http://localhost:5678/webhook/masova-voice`
- Receives response: plays audio via `Audio` API, adds transcript bubble
- Session ID stored in `sessionStorage` for conversation continuity

### 5.2 n8n Workflow (`n8n/workflow.json`)

Importable JSON. 6 nodes:

| # | Node | Type | Purpose |
|---|---|---|---|
| 1 | Webhook | Webhook | Entry point, receives audio file |
| 2 | Transcribe | HTTP Request | POST to Voicebox `/transcribe` |
| 3 | RAG Search | HTTP Request | POST to Qdrant vector search |
| 4 | Agent | HTTP Request | POST to masova-support `/chat` |
| 5 | Speak | HTTP Request | POST to Voicebox `/speak` |
| 6 | Respond | Respond to Webhook | Returns audio + transcript header |

### 5.3 Qdrant Knowledge Base

Docker container on port 6333. Collection: `masova_kb`.

Ingest script: `qdrant/ingest.py`
- Reads all `.md` files from `docs/kb/`
- Chunks at 500 tokens with 50-token overlap
- Embeds via Groq `llama-3.1-8b-instant` (or `nomic-embed-text` if available)
- Upserts into Qdrant

### 5.4 Knowledge Base Documents (`docs/kb/`)

All content sourced directly from the MaSoVa codebase — no invented data.

| File | Source |
|---|---|
| `menu.md` | `CommerceSeedService.java` — real seed menu items |
| `order-lifecycle.md` | `Order.java` enums — 11 real statuses |
| `faqs.md` | `constants.ts` `FAQS` array — 8 real Q&As |
| `refund-policy.md` | `RefundPolicy.tsx` — real policy text |
| `privacy-policy.md` | `PrivacyPolicy.tsx` — GDPR, retention, rights |
| `pricing.md` | `constants.ts` `PRICING_TIERS` — Starter €149, Growth €349, Enterprise |
| `features.md` | `PRODUCT_TOUR_TABS` + `AI_AGENTS` — all 8 AI agents, all features |
| `demo-users.md` | `CommerceSeedService.java` + `demo-state.json` — Anna Mueller, seed orders |
| `support-capabilities.md` | masova-support agent tools — what the agent can/cannot do |
| `contact.md` | `constants.ts` — `masova@souravamseekar.com`, store: Berlin DOM001 |

### 5.5 Docker Compose (`docker-compose.yml`)

Spins up two containers only:

```yaml
services:
  n8n:
    image: n8nio/n8n
    ports: ["5678:5678"]
    volumes: ["./n8n/data:/home/node/.n8n"]

  qdrant:
    image: qdrant/qdrant
    ports: ["6333:6333"]
    volumes: ["./qdrant/storage:/qdrant/storage"]
```

Voicebox and masova-support run separately (user starts them independently).

---

## 6. Real MaSoVa Data Used in RAG Docs

### Menu (from CommerceSeedService.java)

| Item | Cuisine | Category | Price (EUR) |
|---|---|---|---|
| Margherita Pizza | Italian | Pizza | €12.90 |
| Pepperoni Pizza | Italian | Pizza | €14.90 |
| Quattro Formaggi | Italian | Pizza | €15.90 |
| Garlic Bread | Italian | Sides | €4.90 |
| Caesar Salad | Continental | Sides | €7.90 |
| Tiramisu | Italian | Dessert | €6.50 |
| Espresso | Beverages | Hot Drinks | €2.90 |
| Cola | Beverages | Cold Drinks | €2.50 |
| BBQ Burger | American | Burger | €11.90 |
| French Fries | American | Sides | €3.90 |

### Order Statuses (from Order.java)

`RECEIVED → PREPARING → OVEN → BAKED → READY → DISPATCHED → OUT_FOR_DELIVERY → DELIVERED` (delivery)  
`RECEIVED → PREPARING → READY → COMPLETED` (takeaway)  
`RECEIVED → PREPARING → READY → SERVED` (dine-in)  
`CANCELLED` (any stage, requires manager approval)

### Demo Seed Orders (from CommerceSeedService.java)

| Order Number | Status | Type |
|---|---|---|
| SEED-ORD-RECV-1 | RECEIVED | Delivery |
| SEED-ORD-PREP-1 | PREPARING | Delivery |
| SEED-ORD-OFD-1 | OUT_FOR_DELIVERY | Delivery |
| SEED-ORD-DLVR-1 | DELIVERED | Delivery |
| SEED-ORD-COMP-1 | COMPLETED | Takeaway |
| SEED-ORD-CANC-1 | CANCELLED | Delivery |

Demo customer: **Anna Mueller** (`anna.mueller@gmail.com`, `+491511000011`), Berlin, store `DOM001`  
Delivery address: Alexanderplatz 1, Berlin 10178, Germany

### Pricing (from constants.ts)

- **Starter** — €149/month — 1 location, 10 staff, no AI agents
- **Growth** — €349/month (Most Popular) — 3 locations, 50 staff, all AI agents, driver app
- **Enterprise** — Custom — unlimited locations, white-label, 24/7 support
- Extra locations on Growth: €99/location/month

### Refund Policy (from RefundPolicy.tsx)

- Restaurant-controlled — manager approves in console
- AI agents may only **propose** refunds, never auto-execute
- Card refunds: 5–10 business days
- Aggregator orders (Wolt/Deliveroo/etc.) follow that platform's process
- Contact: `masova@souravamseekar.com`

### Agent Capabilities (masova-support tools)

Can: order status, order cancellation request, menu items, store hours, store wait time, complaint submission, refund request (propose only), loyalty points balance  
Cannot: execute payments, override manager approvals, access other customers' data, modify menu

---

## 7. Data Flow — Step by Step

1. User clicks **Start Call** → browser requests mic permission
2. User speaks: *"What's the status of order SEED-ORD-OFD-1?"*
3. After 1.5s silence → audio blob POSTed to `n8n webhook :5678`
4. n8n Node 2 → Voicebox `/transcribe` → `"What's the status of order SEED-ORD-OFD-1?"`
5. n8n Node 3 → Qdrant search with query text → returns top-3 chunks from `order-lifecycle.md` + `demo-users.md`
6. n8n Node 4 → masova-support `/chat`:
   ```json
   {
     "message": "What's the status of order SEED-ORD-OFD-1?",
     "context": "<rag chunks>",
     "session_id": "browser-session-uuid"
   }
   ```
7. masova-support agent (Groq llama-3.1-8b-instant) replies:
   *"Order SEED-ORD-OFD-1 is currently out for delivery to Alexanderplatz 1, Berlin. Your driver is on the way."*
8. n8n Node 5 → Voicebox `/speak` with reply text → returns `audio/mpeg`
9. n8n Node 6 → responds to browser with audio binary + `X-Transcript` header
10. Browser plays audio, appends bubble to transcript panel
11. Loop — user speaks again, same session_id preserves conversation history

---

## 8. Session Management

- Browser generates a UUID on page load, stored in `sessionStorage`
- Sent as `session_id` in every request to masova-support
- masova-support's existing Redis session service handles history natively
- n8n is stateless — it just passes session_id through

---

## 9. Error Handling

| Failure | Behaviour |
|---|---|
| Mic permission denied | UI shows "Mic access required" banner, no call starts |
| Voicebox not running | n8n returns 502 → UI shows "Voice service unavailable, try text chat" |
| Groq rate limit hit | masova-support returns error → n8n speaks fallback: "I'm having trouble, please try again shortly" |
| Qdrant not running | n8n skips RAG, proceeds with agent only (graceful degradation) |
| masova-support not running | n8n speaks fallback response, logs error |

---

## 10. File Structure

```
D:/projects/masova-voice-demo/
├── ui/
│   └── index.html                  # Standalone demo UI
├── n8n/
│   ├── workflow.json               # Importable n8n workflow
│   └── data/                       # n8n persistent data (gitignored)
├── qdrant/
│   ├── ingest.py                   # KB ingestion script
│   └── storage/                    # Qdrant data (gitignored)
├── docs/
│   ├── kb/
│   │   ├── menu.md
│   │   ├── order-lifecycle.md
│   │   ├── faqs.md
│   │   ├── refund-policy.md
│   │   ├── privacy-policy.md
│   │   ├── pricing.md
│   │   ├── features.md
│   │   ├── demo-users.md
│   │   ├── support-capabilities.md
│   │   └── contact.md
│   └── superpowers/
│       └── specs/
│           └── 2026-07-12-masova-voice-support-design.md
├── docker-compose.yml
├── requirements.txt                # Python deps for ingest.py
└── README.md
```

---

## 11. Prerequisites (User Runs Separately)

| Service | How to start | Port |
|---|---|---|
| Voicebox | Download installer from voicebox.sh/download/windows | 17493 |
| masova-support | `uvicorn src.masova_agent.main:app --port 8000` | 8000 |
| n8n + Qdrant | `docker compose up -d` (this repo) | 5678 / 6333 |

---

## 12. Out of Scope

- Authentication — demo only, no login required
- Production deployment — local only
- Modifying masova-support agent code
- WhatsApp / phone channel integration
- Voice interruption / barge-in
- Multi-language TTS (English only for demo)
