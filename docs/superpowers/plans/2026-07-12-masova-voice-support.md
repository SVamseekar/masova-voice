# MaSoVa Voice Support Demo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone voice support demo where a user speaks into a browser mic, the MaSoVa support agent (Groq llama-3.1-8b-instant) answers using RAG over real platform data, and Voicebox MCP speaks the reply back.

**Architecture:** Browser captures mic audio via WebRTC → POSTs to n8n webhook (Docker) → n8n calls Voicebox MCP for STT, Qdrant for RAG context, masova-support agent for the answer, then Voicebox MCP for TTS → returns audio to browser. No changes to any existing repo.

**Tech Stack:** HTML/JS (no framework), n8n (Docker), Qdrant (Docker), Python 3.11+ (ingest script), Voicebox local (MCP), masova-support (existing, untouched), Groq API (free tier, llama-3.1-8b-instant)

---

## File Map

| File | Responsibility |
|---|---|
| `docker-compose.yml` | Spins up n8n (:5678) + Qdrant (:6333) |
| `ui/index.html` | Standalone demo UI — WebRTC mic, audio playback, transcript |
| `n8n/workflow.json` | Importable n8n workflow — 6 nodes, full pipeline |
| `qdrant/ingest.py` | Chunks + embeds KB docs → upserts into Qdrant |
| `requirements.txt` | Python deps for ingest.py |
| `docs/kb/menu.md` | Real MaSoVa menu from CommerceSeedService.java |
| `docs/kb/order-lifecycle.md` | 11 real order statuses from Order.java |
| `docs/kb/faqs.md` | 8 real FAQs from constants.ts |
| `docs/kb/refund-policy.md` | Real refund policy from RefundPolicy.tsx |
| `docs/kb/pricing.md` | Real pricing tiers from constants.ts |
| `docs/kb/features.md` | Real features + 8 AI agents from constants.ts |
| `docs/kb/demo-users.md` | Real seed customers + orders from CommerceSeedService.java |
| `docs/kb/support-capabilities.md` | What masova-support agent can/cannot do |
| `docs/kb/contact.md` | Real support email, store, address |
| `README.md` | Setup + run instructions |

---

## Task 1: Project Scaffold + Docker Compose

**Files:**
- Create: `docker-compose.yml`
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Create `.gitignore`**

```
n8n/data/
qdrant/storage/
__pycache__/
*.pyc
.env
venv/
```

- [ ] **Step 2: Create `requirements.txt`**

```
qdrant-client==1.9.1
requests==2.31.0
groq==0.9.0
tiktoken==0.7.0
python-dotenv==1.0.1
```

- [ ] **Step 3: Create `docker-compose.yml`**

```yaml
version: "3.8"

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: masova-n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=false
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678
      - GENERIC_TIMEZONE=Europe/Berlin
    volumes:
      - ./n8n/data:/home/node/.n8n
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    container_name: masova-qdrant
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant/storage:/qdrant/storage
    restart: unless-stopped
```

- [ ] **Step 4: Create `README.md`**

```markdown
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
```

- [ ] **Step 5: Create required directories**

```bash
mkdir -p n8n/data qdrant/storage docs/kb ui
```

- [ ] **Step 6: Verify Docker starts**

```bash
docker compose up -d
docker compose ps
```

Expected output:
```
NAME             STATUS
masova-n8n       running (healthy)
masova-qdrant    running (healthy)
```

- [ ] **Step 7: Commit**

```bash
git add docker-compose.yml requirements.txt .gitignore README.md
git commit -m "feat: project scaffold with docker-compose for n8n and qdrant"
```

---

## Task 2: Knowledge Base Documents

**Files:**
- Create: `docs/kb/menu.md`
- Create: `docs/kb/order-lifecycle.md`
- Create: `docs/kb/faqs.md`
- Create: `docs/kb/refund-policy.md`
- Create: `docs/kb/pricing.md`
- Create: `docs/kb/features.md`
- Create: `docs/kb/demo-users.md`
- Create: `docs/kb/support-capabilities.md`
- Create: `docs/kb/contact.md`

- [ ] **Step 1: Create `docs/kb/menu.md`**

```markdown
# MaSoVa Menu

MaSoVa restaurant (store DOM001, Berlin) serves the following items:

## Pizza (Italian)
- Margherita Pizza — classic tomato, mozzarella, basil — €12.90
- Pepperoni Pizza — pepperoni and mozzarella — €14.90
- Quattro Formaggi — four cheese pizza — €15.90

## Burgers (American)
- BBQ Burger — beef burger with BBQ sauce — €11.90

## Sides
- Garlic Bread (Italian) — toasted garlic bread with herbs — €4.90
- Caesar Salad (Continental) — romaine, parmesan, croutons — €7.90
- French Fries (American) — crispy fries — €3.90

## Desserts
- Tiramisu (Italian) — coffee mascarpone dessert — €6.50

## Beverages
- Espresso — double espresso — €2.90
- Cola — soft drink 0.33L — €2.50

## Notes
- All items include 14 EU allergen declarations (displayed at checkout)
- Preparation time: approximately 18-25 minutes
- Delivery fee: €2.50 flat rate
- VAT (7%) is included in prices shown
- Currency: EUR
```

- [ ] **Step 2: Create `docs/kb/order-lifecycle.md`**

```markdown
# MaSoVa Order Lifecycle

## Order Statuses

Every order moves through these statuses:

### Delivery orders
RECEIVED → PREPARING → OVEN → BAKED → READY → DISPATCHED → OUT_FOR_DELIVERY → DELIVERED

### Takeaway orders
RECEIVED → PREPARING → OVEN → BAKED → READY → COMPLETED

### Dine-in orders
RECEIVED → PREPARING → READY → SERVED

### Cancelled orders
Any order can be CANCELLED — requires manager approval. A cancellation request does NOT
immediately cancel — the kitchen continues until a manager approves.

## Status Descriptions

- **RECEIVED** — Order placed and confirmed, awaiting kitchen
- **PREPARING** — Kitchen has started work on the order
- **OVEN** — Items are in the oven (baked items only)
- **BAKED** — Baking complete
- **READY** — Order is ready for pickup, dispatch, or serving
- **DISPATCHED** — Awaiting driver pickup at restaurant
- **OUT_FOR_DELIVERY** — Driver assigned and en route to customer
- **DELIVERED** — Successfully delivered to customer
- **SERVED** — Served to table (dine-in)
- **COMPLETED** — Picked up by customer (takeaway)
- **CANCELLED** — Order cancelled (manager approved)

## Order Types
- DELIVERY — delivered to customer address
- TAKEAWAY — customer collects from restaurant
- DINE_IN — served at table

## Payment Statuses
- PENDING, PAID, FAILED, REFUNDED

## Payment Methods
- CARD (Stripe, SCA/3D Secure), CASH, UPI, WALLET, AGGREGATOR_COLLECTED
```

- [ ] **Step 3: Create `docs/kb/faqs.md`**

```markdown
# MaSoVa Frequently Asked Questions

**Q: How long does setup take?**
A: Most restaurants are live within 48 hours. We handle onboarding, menu import, and staff training. Enterprise customers get a dedicated onboarding specialist.

**Q: Do I need new hardware?**
A: MaSoVa runs on any modern tablet or screen. No proprietary hardware required. The KDS runs on any wall-mounted screen, and drivers use their own smartphones.

**Q: Is MaSoVa GDPR compliant?**
A: Yes — fully. MaSoVa includes consent management, data export (Article 15), right to erasure (Article 17), breach logging, and data residency options for EU customers.

**Q: Which payment methods does MaSoVa support?**
A: MaSoVa supports card payments, iDEAL (Netherlands), Bancontact (Belgium), SEPA Direct Debit, Apple Pay, and Google Pay — all via Stripe with PSD2/SCA compliance.

**Q: Does MaSoVa handle EU VAT and fiscal signing?**
A: Yes. MaSoVa calculates VAT across 12 EU countries by order type (dine-in, takeaway, delivery) and item category. Fiscal signing for Germany, France, Italy, Belgium, Hungary, and the UK runs automatically at order completion, with a compliance dashboard for managers.

**Q: Can I use MaSoVa if I already have a POS system?**
A: Enterprise plans support custom integrations. For Starter and Growth, MaSoVa replaces your existing POS, KDS, and delivery management in one unified system.

**Q: What happens if I need more than 3 locations on Growth?**
A: You can add extra locations at €99/location/month on Growth, or upgrade to Enterprise for unlimited locations with a custom price.

**Q: Do the smart assistants change things without asking?**
A: No. MaSoVa only suggests actions — reorder lists, review replies, shift plans, and the like. A manager approves before anything goes live.
```

- [ ] **Step 4: Create `docs/kb/refund-policy.md`**

```markdown
# MaSoVa Refund Policy

Last updated: July 10, 2026

## Scope
This policy covers payments processed through MaSoVa for restaurant orders (customer app / web / POS card payments). It does not replace mandatory consumer rights in your country (e.g. EU consumer law).

## Restaurant-Controlled Refunds
Individual restaurants decide whether and how much to refund. Managers approve full or partial refunds in the MaSoVa manager console.

IMPORTANT: AI support agents may only PROPOSE refunds — they never auto-execute payouts. A manager must approve before any refund is processed.

## Timing
- Approved card refunds typically appear in 5–10 business days depending on the bank.
- Cash or COD orders are settled at the store — not via card networks.
- Aggregator orders (Wolt, Deliveroo, Just Eat, Uber Eats) follow that platform's own refund process.

## Subscription (SaaS)
MaSoVa software subscription billing is separate from diner order refunds. Contact masova@souravamseekar.com for billing disputes.

## Contact
For a specific order, contact the restaurant first. Platform issues: masova@souravamseekar.com
```

- [ ] **Step 5: Create `docs/kb/pricing.md`**

```markdown
# MaSoVa Pricing

## Starter — €149/month
Best for single-location restaurants.

Includes:
- Online ordering (web + mobile app)
- POS with staff PIN login
- Kitchen display screen
- Menu management
- Basic order analytics
- Customer loyalty points
- Email + SMS notifications
- Delivery management (1 zone)
- EU VAT calculation
- Fiscal signing (supported countries)
- GDPR compliance tools
- 1 location, up to 10 staff accounts

Does NOT include: Smart assistants, Advanced analytics, Custom branding

## Growth — €349/month (Most Popular)
For restaurants scaling across locations.

Includes everything in Starter, plus:
- 24/7 customer chat assistant
- Manager insights (plain English queries)
- Advanced analytics + BI dashboard
- Sales forecasting + demand prediction
- Multi-store management (up to 3 locations)
- Driver app + auto-dispatch
- Live GPS delivery tracking
- Inventory + purchase orders
- Waste tracking + analysis
- Supplier management
- Up to 50 staff accounts
- Custom branding (logo + colours)
- Priority support (chat, 12h SLA)

Extra locations on Growth: €99/location/month

## Enterprise — Custom pricing
For chains and franchises across Europe.

Includes everything in Growth, plus:
- Kitchen & delivery smart assistants
- Smarter dispatch across busy runs
- Unlimited locations and staff
- White-label (your brand)
- Multi-currency (EUR, GBP, SEK, DKK)
- Multi-language (EN, DE, NL, FR)
- Custom integrations (ERP, accounting)
- EU data residency choice
- 99.9% uptime SLA
- 24/7 phone support
- Dedicated account manager
- Onboarding + staff training

Contact: masova@souravamseekar.com
```

- [ ] **Step 6: Create `docs/kb/features.md`**

```markdown
# MaSoVa Features

## Core Platform Features

### Online Ordering
Customers order from branded web app or mobile app. EU allergen labels shown on every item. VAT shown at checkout. Delivery fees computed from customer address. Orders land on KDS the moment payment clears.

### Kitchen Display System (KDS)
Live order queue via WebSocket updates. Allergen badges on tickets. Prep timers and predictive prep alerts. Quality checkpoints and recipe viewer. 11-state order lifecycle.

### Delivery
Auto-assigns nearest available driver when order is ready. Delivery zones with server-side fees. Live GPS tracking. OTP proof of delivery at the door. Dispatched in under 8 seconds.

### Payments & EU Compliance
Stripe with SCA/3D Secure, iDEAL, Bancontact, SEPA. EU VAT calculated per country, order type, and item category. Automated fiscal signing at order completion for DE, FR, IT, BE, HU, GB.

### Aggregator Hub
Wolt, Deliveroo, Just Eat, and Uber Eats orders normalised into same pipeline as direct orders. Per-channel commission and margin tracking. Stop juggling tablets.

### Analytics & BI
Sales trends, peak-hour heatmaps, staff leaderboards, waste analysis, demand forecasting, multi-store benchmarking. Updated in real time from live order events.

### POS + Kiosk
Touch-first counter POS with PIN auth. Dine-in, takeaway, delivery modes. Cash recording and self-service kiosk terminals.

### Allergen Compliance
14 EU allergens tracked per item. Items cannot go live without manager declaration. Badges appear on customer menus and kitchen tickets.

### Inventory & Suppliers
Stock levels, low-stock alerts, auto-generated purchase orders, supplier management, waste tracking with cost analysis.

### Staff & Shifts
Weekly scheduling, clock-in sessions with manager approval, shift lifecycle, performance leaderboards.

### Loyalty, Reviews & Campaigns
Bronze → Platinum loyalty tiers. Review moderation with sentiment analysis. Email/SMS/push campaign builder.

### Refunds & Reconciliation
Full and partial refunds via Stripe. Manager approval queue for agent-initiated refunds. Daily payment reconciliation.

### GDPR Toolkit
Consent management, data export, right to erasure, portability, rectification, breach logging, audit trail.

## 8 AI Smart Assistants

All assistants use a propose-then-approve model — nothing goes live without manager sign-off.

1. **Customer Chat** (Always on) — Answers order status, menu questions, and refund requests in the app so your team isn't glued to the phone.

2. **Demand Planner** (Every night) — Spots which dishes and hours will be busy tomorrow so prep and staffing aren't guesswork.

3. **Peak-Hour Pricing** (During service) — Suggests small menu price tweaks when demand spikes. You approve before anything goes live.

4. **Stock Watch** (Throughout the day) — Warns before ingredients run out and drafts reorder lists for your sign-off.

5. **Kitchen Insights** (End of day) — Summarises what slowed the line today and what to fix before the next rush.

6. **Loyalty Keeper** (Every morning) — Notices regulars who haven't ordered lately and drafts personal offers — you choose whether to send.

7. **Review Helper** (When reviews arrive) — Drafts thoughtful replies to low ratings. Nothing posted until manager approves.

8. **Shift Planner** (Weekly) — Proposes next week's rota based on forecasted footfall. Adjust and publish when ready.
```

- [ ] **Step 7: Create `docs/kb/demo-users.md`**

```markdown
# MaSoVa Demo Users & Orders

## Demo Store
- Store ID: DOM001
- Store Code: DOM001
- Location: Berlin, Germany
- Currency: EUR
- Timezone: Europe/Berlin

## Demo Customers

| Name | Email | Phone |
|---|---|---|
| Anna Mueller | anna.mueller@gmail.com | +491511000011 |
| Lena Wagner | lena.wagner@gmail.com | — |
| Thomas Braun | thomas.braun@gmail.com | — |
| Sophie Richter | sophie.richter@gmail.com | — |
| Felix Schmidt | felix.schmidt@gmail.com | — |

Primary demo customer: **Anna Mueller**

## Demo Staff Credentials
- Manager: manager.berlin@gmail.com / Demo@1234
- Driver: driver.berlin@gmail.com / Demo@1234
- Customer: anna.mueller@gmail.com / password123

## Demo Delivery Address
Alexanderplatz 1, Berlin 10178, Germany (52.5219°N, 13.4132°E)

## Seed Orders (Anna Mueller)

| Order Number | Status | Type | Paid |
|---|---|---|---|
| SEED-ORD-RECV-1 | RECEIVED | Delivery | No |
| SEED-ORD-PREP-1 | PREPARING | Delivery | No |
| SEED-ORD-OVEN-1 | OVEN | Takeaway | No |
| SEED-ORD-READY-1 | READY | Takeaway | No |
| SEED-ORD-DISP-1 | DISPATCHED | Delivery | No |
| SEED-ORD-OFD-1 | OUT_FOR_DELIVERY | Delivery | No |
| SEED-ORD-DLVR-1 | DELIVERED | Delivery | Yes |
| SEED-ORD-DLVR-2 | DELIVERED | Delivery | Yes |
| SEED-ORD-COMP-1 | COMPLETED | Takeaway | Yes |
| SEED-ORD-CANC-1 | CANCELLED | Delivery | No |

All seed orders contain 1x the first available menu item. Delivery fee: €2.50. VAT: 7% (Germany). Payment method: CARD for delivery, CASH for takeaway.
```

- [ ] **Step 8: Create `docs/kb/support-capabilities.md`**

```markdown
# MaSoVa Support Agent Capabilities

## What the Support Agent CAN Do

- **Check order status** — provide current status of any order by order number
- **Request order cancellation** — submit a cancellation request (requires manager approval to execute)
- **Get menu items** — list available menu items for a store
- **Get store hours** — provide opening/closing times for a store
- **Get store wait time** — current estimated wait time
- **Submit complaint** — log a customer complaint for manager review
- **Request refund** — propose a refund (manager must approve before payout)
- **Check loyalty points** — retrieve a customer's loyalty point balance and tier

## What the Support Agent CANNOT Do

- Execute payments or refunds directly (manager approval always required)
- Override manager decisions
- Access another customer's order or account data
- Modify menu items, prices, or store settings
- Guarantee delivery times (estimates only)
- Process aggregator (Wolt/Deliveroo/Uber Eats/Just Eat) refunds — those follow the aggregator's process

## Response Guidelines

- Responses are kept under 150 words for voice readability
- Agent confirms customer identity before performing account actions
- Agent never accepts alternate customer IDs mid-conversation
- Fallback contact: masova@souravamseekar.com

## Escalation

If the agent cannot resolve an issue, it provides the support email: masova@souravamseekar.com
```

- [ ] **Step 9: Create `docs/kb/contact.md`**

```markdown
# MaSoVa Contact & Support

## Support Contact
Email: masova@souravamseekar.com
Response: Within 30 days for GDPR requests; standard support response time varies by plan.

## Platform
Website: https://masova.souravamseekar.com
GitHub: https://github.com/SVamseekar/masova-platform

## Demo Store (Berlin)
Store ID: DOM001
Address: Alexanderplatz 1, 10178 Berlin, Germany
Currency: EUR
VAT country: DE (7% food/beverages)

## Support Tiers by Plan
- **Starter** — Community support
- **Growth** — Priority chat support, 12-hour SLA
- **Enterprise** — 24/7 phone support + dedicated account manager

## Legal Pages
- Privacy Policy: covers GDPR, data retention (7 years financial records, 30 days post-cancellation account data)
- Refund Policy: 5–10 business day card refunds, manager approval required
- Terms of Service: restaurant operators and authorised staff
```

- [ ] **Step 10: Commit KB docs**

```bash
git add docs/kb/
git commit -m "feat: add knowledge base docs sourced from real masova-platform codebase"
```

---

## Task 3: Qdrant Ingestion Script

**Files:**
- Create: `qdrant/ingest.py`
- Create: `.env` (not committed — in .gitignore)

- [ ] **Step 1: Create `.env` template**

Create `.env` in project root (manually — not committed):
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at https://console.groq.com

- [ ] **Step 2: Create `qdrant/ingest.py`**

```python
"""
Ingests docs/kb/*.md into Qdrant collection 'masova_kb'.
Chunks at ~500 tokens with 50-token overlap.
Embeds via Groq llama-3.1-8b-instant (free tier).
Run: python qdrant/ingest.py
"""

import os
import uuid
import glob
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, PayloadSchemaType
)

load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
QDRANT_URL = "http://localhost:6333"
COLLECTION = "masova_kb"
EMBED_MODEL = "llama-3.1-8b-instant"
VECTOR_SIZE = 4096   # llama-3.1-8b-instant embedding dimension
CHUNK_CHARS = 1800   # ~500 tokens at ~3.6 chars/token
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
```

- [ ] **Step 3: Verify Qdrant is running before ingesting**

```bash
curl http://localhost:6333/collections
```

Expected: `{"result":{"collections":[]},"status":"ok","time":...}`

If not running: `docker compose up -d`

- [ ] **Step 4: Run ingestion**

```bash
python qdrant/ingest.py
```

Expected output:
```
Collection 'masova_kb' already exists — upserting (or Created collection 'masova_kb')
  contact.md: 1 chunks ingested
  demo-users.md: 2 chunks ingested
  faqs.md: 3 chunks ingested
  features.md: 4 chunks ingested
  menu.md: 1 chunks ingested
  order-lifecycle.md: 2 chunks ingested
  pricing.md: 2 chunks ingested
  refund-policy.md: 1 chunks ingested
  support-capabilities.md: 2 chunks ingested

Done. ~18-22 total chunks in 'masova_kb'
Qdrant collection vectors count: 18 (approx)
```

- [ ] **Step 5: Verify search works**

```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
import os
from groq import Groq
from qdrant_client import QdrantClient

groq_client = Groq(api_key=os.environ['GROQ_API_KEY'])
qdrant = QdrantClient(url='http://localhost:6333')

resp = groq_client.embeddings.create(model='llama-3.1-8b-instant', input='what is on the menu')
vec = resp.data[0].embedding

hits = qdrant.search(collection_name='masova_kb', query_vector=vec, limit=2)
for h in hits:
    print(h.payload['source'], '|', h.payload['text'][:100])
"
```

Expected: prints menu.md and/or features.md chunks.

- [ ] **Step 6: Commit**

```bash
git add qdrant/ingest.py requirements.txt
git commit -m "feat: qdrant ingestion script for masova KB docs"
```

---

## Task 4: n8n Workflow

**Files:**
- Create: `n8n/workflow.json`

- [ ] **Step 1: Open n8n and import the workflow**

Navigate to http://localhost:5678 in browser.

- [ ] **Step 2: Create the workflow JSON**

Create `n8n/workflow.json` with this content:

```json
{
  "name": "MaSoVa Voice Support",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "masova-voice",
        "responseMode": "responseNode",
        "options": {}
      },
      "id": "webhook-node",
      "name": "Voice Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [240, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://host.docker.internal:17493/transcribe",
        "sendBody": true,
        "contentType": "multipart-form-data",
        "bodyParameters": {
          "parameters": [
            {
              "parameterType": "formBinaryData",
              "name": "file",
              "inputDataFieldName": "data"
            }
          ]
        },
        "options": {}
      },
      "id": "transcribe-node",
      "name": "Voicebox STT",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [460, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://host.docker.internal:17493/embed",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ text: $json.text }) }}",
        "options": {}
      },
      "id": "embed-node",
      "name": "Embed Query",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [680, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://host.docker.internal:6333/collections/masova_kb/points/search",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ vector: $json.embedding, limit: 3, with_payload: true }) }}",
        "options": {}
      },
      "id": "qdrant-node",
      "name": "RAG Search",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [900, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://host.docker.internal:8000/chat",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({\n  message: $('Voicebox STT').item.json.text,\n  context: $json.result.map(r => r.payload.text).join('\\n\\n'),\n  session_id: $('Voice Webhook').item.json.body.session_id || 'default-session'\n}) }}",
        "options": {}
      },
      "id": "agent-node",
      "name": "MaSoVa Agent",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1120, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "http://host.docker.internal:17493/speak",
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify({ text: $json.reply || $json.response || $json.message }) }}",
        "options": {
          "response": {
            "response": {
              "responseFormat": "file"
            }
          }
        }
      },
      "id": "tts-node",
      "name": "Voicebox TTS",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [1340, 300]
    },
    {
      "parameters": {
        "respondWith": "binary",
        "responseBody": "={{ $binary.data }}",
        "options": {
          "responseHeaders": {
            "entries": [
              {
                "name": "Content-Type",
                "value": "audio/mpeg"
              },
              {
                "name": "X-Transcript",
                "value": "={{ encodeURIComponent($('Voicebox STT').item.json.text || '') }}"
              },
              {
                "name": "X-Reply",
                "value": "={{ encodeURIComponent($('MaSoVa Agent').item.json.reply || $('MaSoVa Agent').item.json.response || '') }}"
              },
              {
                "name": "Access-Control-Allow-Origin",
                "value": "*"
              },
              {
                "name": "Access-Control-Expose-Headers",
                "value": "X-Transcript, X-Reply"
              }
            ]
          }
        }
      },
      "id": "respond-node",
      "name": "Respond with Audio",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1.1,
      "position": [1560, 300]
    }
  ],
  "connections": {
    "Voice Webhook": {
      "main": [[{"node": "Voicebox STT", "type": "main", "index": 0}]]
    },
    "Voicebox STT": {
      "main": [[{"node": "Embed Query", "type": "main", "index": 0}]]
    },
    "Embed Query": {
      "main": [[{"node": "RAG Search", "type": "main", "index": 0}]]
    },
    "RAG Search": {
      "main": [[{"node": "MaSoVa Agent", "type": "main", "index": 0}]]
    },
    "MaSoVa Agent": {
      "main": [[{"node": "Voicebox TTS", "type": "main", "index": 0}]]
    },
    "Voicebox TTS": {
      "main": [[{"node": "Respond with Audio", "type": "main", "index": 0}]]
    }
  },
  "settings": {
    "executionOrder": "v1"
  }
}
```

- [ ] **Step 3: Import into n8n**

1. Open http://localhost:5678
2. Click **+** (new workflow) → **...** menu → **Import from file**
3. Select `n8n/workflow.json`
4. Click **Activate** toggle (top right)

- [ ] **Step 4: Test webhook endpoint is live**

```bash
curl -X POST http://localhost:5678/webhook/masova-voice \
  -F "data=@/dev/null" \
  -F "session_id=test"
```

Expected: some response (may error at Voicebox step — that's fine, confirms webhook is live)

- [ ] **Step 5: Commit**

```bash
git add n8n/workflow.json
git commit -m "feat: n8n workflow — webhook to STT to RAG to agent to TTS pipeline"
```

---

## Task 5: Demo UI

**Files:**
- Create: `ui/index.html`

- [ ] **Step 1: Create `ui/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MaSoVa Voice Support</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #080808;
      color: #fff;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 32px 16px;
    }

    header {
      text-align: center;
      margin-bottom: 32px;
    }

    header h1 {
      font-size: 1.6rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    header p {
      color: #888;
      font-size: 0.875rem;
      margin-top: 6px;
    }

    .gold { color: #D4AF37; }

    .status-bar {
      display: flex;
      align-items: center;
      gap: 10px;
      background: #111;
      border: 1px solid #222;
      border-radius: 12px;
      padding: 12px 20px;
      margin-bottom: 24px;
      font-size: 0.875rem;
      min-width: 280px;
      justify-content: center;
    }

    .status-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #333;
      transition: background 0.3s;
    }

    .status-dot.idle     { background: #333; }
    .status-dot.listening { background: #22c55e; animation: pulse 1s infinite; }
    .status-dot.processing { background: #f59e0b; }
    .status-dot.speaking { background: #3b82f6; animation: pulse 1s infinite; }
    .status-dot.error    { background: #ef4444; }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }

    .controls {
      display: flex;
      gap: 12px;
      margin-bottom: 32px;
    }

    button {
      border: none;
      border-radius: 10px;
      padding: 12px 28px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.2s, transform 0.1s;
    }

    button:active { transform: scale(0.97); }
    button:disabled { opacity: 0.4; cursor: not-allowed; }

    #btn-start { background: #22c55e; color: #000; }
    #btn-end   { background: #ef4444; color: #fff; display: none; }
    #btn-mute  { background: #1e1e1e; color: #aaa; border: 1px solid #333; }

    .transcript {
      width: 100%;
      max-width: 600px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      overflow-y: auto;
      max-height: 420px;
      padding-right: 4px;
    }

    .bubble {
      max-width: 85%;
      padding: 10px 14px;
      border-radius: 12px;
      font-size: 0.875rem;
      line-height: 1.5;
    }

    .bubble.user {
      align-self: flex-end;
      background: #1e3a5f;
      color: #e0efff;
      border-bottom-right-radius: 4px;
    }

    .bubble.agent {
      align-self: flex-start;
      background: #1a1a1a;
      border: 1px solid #2a2a2a;
      color: #ccc;
      border-bottom-left-radius: 4px;
    }

    .bubble .label {
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 4px;
      opacity: 0.6;
    }

    .empty-state {
      color: #444;
      font-size: 0.875rem;
      text-align: center;
      padding: 40px 0;
    }
  </style>
</head>
<body>

<header>
  <h1><span class="gold">MaSoVa</span> Voice Support</h1>
  <p>Speak to our AI support agent — powered by Voicebox</p>
</header>

<div class="status-bar">
  <div class="status-dot idle" id="status-dot"></div>
  <span id="status-text">Ready — click Start Call to begin</span>
</div>

<div class="controls">
  <button id="btn-start">Start Call</button>
  <button id="btn-end">End Call</button>
  <button id="btn-mute" disabled>Mute</button>
</div>

<div class="transcript" id="transcript">
  <div class="empty-state" id="empty-state">Your conversation will appear here</div>
</div>

<script>
  const N8N_WEBHOOK = 'http://localhost:5678/webhook/masova-voice';
  const SILENCE_THRESHOLD = 0.01;
  const SILENCE_DURATION_MS = 1500;

  let mediaRecorder = null;
  let audioChunks = [];
  let analyser = null;
  let silenceTimer = null;
  let isMuted = false;
  let isActive = false;
  const sessionId = crypto.randomUUID();

  const btnStart = document.getElementById('btn-start');
  const btnEnd   = document.getElementById('btn-end');
  const btnMute  = document.getElementById('btn-mute');
  const dot      = document.getElementById('status-dot');
  const statusTxt = document.getElementById('status-text');
  const transcript = document.getElementById('transcript');
  const emptyState = document.getElementById('empty-state');

  function setStatus(state, text) {
    dot.className = 'status-dot ' + state;
    statusTxt.textContent = text;
  }

  function addBubble(role, text) {
    if (emptyState) emptyState.remove();
    const div = document.createElement('div');
    div.className = 'bubble ' + role;
    div.innerHTML = `<div class="label">${role === 'user' ? 'You' : 'MaSoVa Agent'}</div>${escapeHtml(text)}`;
    transcript.appendChild(div);
    transcript.scrollTop = transcript.scrollHeight;
  }

  function escapeHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  async function startCall() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      isActive = true;

      btnStart.style.display = 'none';
      btnEnd.style.display = 'inline-block';
      btnMute.disabled = false;

      const audioCtx = new AudioContext();
      const source = audioCtx.createMediaStreamSource(stream);
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);

      startRecording(stream);
      setStatus('listening', 'Listening — speak now');
    } catch (e) {
      setStatus('error', 'Mic access denied — please allow microphone access');
    }
  }

  function startRecording(stream) {
    if (!isActive) return;
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
    mediaRecorder.onstop = () => sendAudio();
    mediaRecorder.start(100);
    detectSilence(stream);
  }

  function detectSilence(stream) {
    const data = new Uint8Array(analyser.frequencyBinCount);
    const check = () => {
      if (!isActive || isMuted) { return; }
      analyser.getByteFrequencyData(data);
      const avg = data.reduce((a, b) => a + b, 0) / data.length / 255;
      if (avg < SILENCE_THRESHOLD) {
        if (!silenceTimer) {
          silenceTimer = setTimeout(() => {
            if (mediaRecorder && mediaRecorder.state === 'recording' && audioChunks.length > 0) {
              mediaRecorder.stop();
            }
            silenceTimer = null;
          }, SILENCE_DURATION_MS);
        }
      } else {
        clearTimeout(silenceTimer);
        silenceTimer = null;
      }
      if (isActive) requestAnimationFrame(check);
    };
    requestAnimationFrame(check);
  }

  async function sendAudio() {
    if (!audioChunks.length || !isActive) return;
    setStatus('processing', 'Processing your message...');

    const blob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('data', blob, 'audio.webm');
    formData.append('session_id', sessionId);

    try {
      const res = await fetch(N8N_WEBHOOK, { method: 'POST', body: formData });

      if (!res.ok) throw new Error('n8n returned ' + res.status);

      const userText = decodeURIComponent(res.headers.get('X-Transcript') || '');
      const agentText = decodeURIComponent(res.headers.get('X-Reply') || '');

      if (userText) addBubble('user', userText);
      if (agentText) addBubble('agent', agentText);

      const audioBlob = await res.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      setStatus('speaking', 'Agent is speaking...');
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        if (isActive) {
          setStatus('listening', 'Listening — speak now');
          const stream = mediaRecorder.stream;
          startRecording(stream);
        }
      };
      audio.play();

    } catch (e) {
      console.error('Voice pipeline error:', e);
      setStatus('error', 'Pipeline error — check that all services are running');
      if (isActive) {
        setTimeout(() => {
          setStatus('listening', 'Listening — speak now');
          const stream = mediaRecorder.stream;
          startRecording(stream);
        }, 3000);
      }
    }
  }

  function endCall() {
    isActive = false;
    if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
    mediaRecorder?.stream?.getTracks().forEach(t => t.stop());
    mediaRecorder = null;
    clearTimeout(silenceTimer);
    silenceTimer = null;

    btnEnd.style.display = 'none';
    btnStart.style.display = 'inline-block';
    btnMute.disabled = true;
    isMuted = false;
    btnMute.textContent = 'Mute';
    setStatus('idle', 'Call ended — click Start Call to begin again');
  }

  function toggleMute() {
    isMuted = !isMuted;
    btnMute.textContent = isMuted ? 'Unmute' : 'Mute';
    setStatus(isMuted ? 'idle' : 'listening', isMuted ? 'Muted' : 'Listening — speak now');
  }

  btnStart.addEventListener('click', startCall);
  btnEnd.addEventListener('click', endCall);
  btnMute.addEventListener('click', toggleMute);
</script>
</body>
</html>
```

- [ ] **Step 2: Open the UI in browser**

Open `ui/index.html` directly in Chrome or Edge (double-click the file).

You should see: dark background, gold "MaSoVa" header, green "Start Call" button, status bar.

- [ ] **Step 3: Test mic capture (no services needed)**

Click **Start Call** → allow mic access.
Status dot should turn green and pulse. Status text: "Listening — speak now".
Click **End Call** → status returns to idle.

- [ ] **Step 4: Commit**

```bash
git add ui/index.html
git commit -m "feat: standalone voice demo UI with WebRTC mic capture and audio playback"
```

---

## Task 6: End-to-End Integration Test

**Prerequisite:** All 4 services running — Voicebox (:17493), masova-support (:8000), n8n (:5678), Qdrant (:6333)

- [ ] **Step 1: Verify all services are up**

```bash
curl http://localhost:17493/docs -s -o /dev/null -w "%{http_code}"
# Expected: 200

curl http://localhost:8000/docs -s -o /dev/null -w "%{http_code}"
# Expected: 200

curl http://localhost:5678/healthz -s -o /dev/null -w "%{http_code}"
# Expected: 200

curl http://localhost:6333/collections/masova_kb -s | python -m json.tool | grep "vectors_count"
# Expected: some number > 0
```

- [ ] **Step 2: Test STT directly**

Record a short WAV file (or use any `.webm`/`.mp3`) and test Voicebox transcription:

```bash
curl -X POST http://localhost:17493/transcribe \
  -F "file=@test.webm" \
  -H "Accept: application/json"
```

Expected: `{"text": "your spoken words here"}`

- [ ] **Step 3: Test masova-support chat endpoint**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What is on the menu?\", \"session_id\": \"test-123\"}"
```

Expected: JSON with `reply` or `response` field containing menu info.

- [ ] **Step 4: Test TTS directly**

```bash
curl -X POST http://localhost:17493/speak \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Hello, welcome to MaSoVa support.\"}" \
  --output test-response.mp3
```

Expected: `test-response.mp3` created. Play it to verify.

- [ ] **Step 5: Full pipeline test via n8n**

Open the n8n UI at http://localhost:5678, navigate to your workflow, click **Test workflow**. Use the manual trigger with a sample audio file.

Alternatively, use the demo UI:
1. Open `ui/index.html` in Chrome
2. Click **Start Call**
3. Say: *"What's on the menu?"*
4. Wait for audio response

Expected: hear a spoken list of menu items, transcript shows both your words and agent reply.

- [ ] **Step 6: Test conversation continuity**

In same session (don't refresh):
1. Say: *"What is the status of order SEED-ORD-OFD-1?"*
2. Expected: agent says order is out for delivery to Alexanderplatz 1 Berlin
3. Say: *"How do I request a refund?"*
4. Expected: agent explains the refund proposal process (no auto-execution)

- [ ] **Step 7: Test error graceful degradation**

Stop Qdrant: `docker stop masova-qdrant`

Say something in the UI. Expected: pipeline continues without RAG (agent answers from system prompt alone), no crash.

Restart Qdrant: `docker start masova-qdrant`

- [ ] **Step 8: Final commit**

```bash
git add .
git commit -m "feat: complete masova voice support demo — STT + RAG + LLM + TTS pipeline"
```

---

## Self-Review Checklist

### Spec Coverage

| Spec requirement | Task |
|---|---|
| WebRTC mic capture | Task 5 |
| Voicebox MCP STT (`/transcribe`) | Task 4 (n8n Node 2) |
| Qdrant RAG with real MaSoVa docs | Tasks 2 + 3 |
| Groq llama-3.1-8b-instant via masova-support | Task 4 (n8n Node 4) |
| Voicebox MCP TTS (`/speak`) | Task 4 (n8n Node 5) |
| Audio playback in browser | Task 5 |
| Transcript display | Task 5 |
| Session continuity | Task 5 (sessionId in sessionStorage) |
| Docker Compose for n8n + Qdrant | Task 1 |
| Real menu data from CommerceSeedService | Task 2 |
| Real order statuses from Order.java | Task 2 |
| Real FAQs from constants.ts | Task 2 |
| Real refund policy from RefundPolicy.tsx | Task 2 |
| Real pricing from constants.ts | Task 2 |
| Real demo users from seed scripts | Task 2 |
| Error graceful degradation | Task 6 Step 7 |
| Nothing in existing repos touched | All tasks — new folder only |

### Notes
- masova-support `/chat` endpoint must accept `{ message, context, session_id }` — if it doesn't match, adjust the n8n Agent node JSON body in Task 4 Step 2 to match the actual request schema of masova-support's FastAPI endpoint.
- Voicebox embed endpoint (`/embed`) may not exist — if Task 4 Step 3 shows a 404, replace the Embed Query node with a Groq embeddings HTTP call directly using your `GROQ_API_KEY` set as an n8n credential.
- `host.docker.internal` works on Docker Desktop for Windows/Mac. On Linux, replace with the host machine's IP (e.g. `172.17.0.1`).
