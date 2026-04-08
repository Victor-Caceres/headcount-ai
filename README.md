# Headcount Planning AI

A natural language interface for workforce planning. Business leaders ask headcount questions in plain English — staffing gaps, capacity calculations, what-if scenarios — and get verified, mathematically accurate answers with the work shown.

**Live:** https://headcount-ai.vercel.app

---

## The Core Design Decision

This is not a RAG project. That's intentional.

Most AI tools reach for vector search and retrieval by default. The right call here was recognizing that this problem has no retrieval component — it has a calculation component. Those require different architectures.

The system is built on a strict separation of concerns:

- **Claude handles language** — intent classification, parameter extraction, prose composition
- **Python handles math** — six deterministic formula functions that own all arithmetic
- **Claude never calculates.** It calls typed functions that do.

This makes the system trustworthy by design, not by instruction. Every number in every response traces back to a Python function return value — not Claude's inference.

---

## How It Works

```
User types question
       ↓
React chat UI
       ↓ POST /chat
FastAPI backend fetches live data from Supabase
       ↓
Claude receives question + full data model in system prompt
       ↓ extracts parameters, calls appropriate tool
Formula Engine (pure Python) executes math deterministically
       ↓ returns typed dict with all intermediate values
Claude composes natural language answer from returned values only
       ↓
Frontend renders answer + formula tags showing which tools were called
```

---

## Formula Primitives

Six composable functions in `formulas.py` cover the complete math surface area of the data model. Claude routes to these — it never computes.

| Function | Answers |
|----------|---------|
| `effective_capacity` | How many productive hours does a region have? |
| `tickets_handleable` | What's the max ticket volume a team can handle? |
| `agents_required` | How many agents do we need for a given volume? |
| `utilization_actual` | What utilization rate is a team running at? |
| `staffing_gap` | How many net-new agents do we need to hire? |
| `regional_summary` | Aggregate analysis across all regions |

Rounding is intentional: `math.floor` for capacity (never overstate what a team can do), `math.ceil` for headcount (never understaff).

---

## Data Model

Three tables in Supabase mirror the source headcount model:

- **global_assumptions** — working hours, shrinkage rate, utilization target
- **roster** — active agents and AHT by region (NAMER, EMEA, APAC)
- **projected_tickets** — next month ticket volume by region

The formula engine and Claude orchestration are fully decoupled from the data source via a `get_model_data()` abstraction in `db.py`. Swapping to a production model with hundreds of rows requires changing one function.

---

## Handling What the Model Doesn't Know

Questions outside the model's scope — costs, attrition, ramp time, historical trends — return an explicit refusal:

> "That question requires data not currently in this model."

A system that knows its limits is more trustworthy than one that always produces an answer. Graceful refusal is a feature.

---

## Stack

| Layer | Choice |
|-------|--------|
| Frontend | React + Vite + Tailwind |
| Backend | Python + FastAPI |
| AI | Claude Sonnet via Anthropic SDK (tool use) |
| Database | Supabase (PostgreSQL) |
| Frontend hosting | Vercel |
| Backend hosting | Render |
| Keep-alive | UptimeRobot on `/ping` |

---

## Project Structure

```
headcount-ai/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── ChatMessage.jsx
│   │       └── FormulaTag.jsx
│   └── vite.config.js
├── backend/
│   ├── main.py          # FastAPI app, /chat + /ping endpoints
│   ├── db.py            # Supabase data access, get_model_data()
│   ├── formulas.py      # Six pure Python formula primitives
│   ├── tools.py         # Claude tool definitions (JSON schema)
│   └── agent.py         # Claude orchestration + tool dispatch
└── README.md
```

---

## Running Locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:
```
ANTHROPIC_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_SERVICE_KEY=your_key_here
```

```bash
python -m uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```
VITE_API_URL=http://localhost:8000
```

```bash
npm run dev
```

---

## Built As

A hiring assessment for a Senior AI Program Manager role for a company with a large global customer support team. The brief asked for a prototype that could ingest a headcount model and accurately answer questions without hallucinating. The architecture was designed to make hallucination structurally impossible, not just unlikely.

Built and deployed in less than a day using Claude Code. Planned using a structured five-phase product and engineering framework before any code was written.
