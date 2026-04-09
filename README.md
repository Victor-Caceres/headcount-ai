# Headcount Planning AI

A natural language interface for workforce planning. Business leaders ask headcount questions in plain English — staffing gaps, capacity calculations, what-if scenarios — and get verified, mathematically accurate answers with the work shown.

**Live:** https://headcount-ai.vercel.app

---

## The Core Design Decision

This is not a RAG project. That's intentional.

Most AI tools reach for vector search and retrieval by default. The right call here was recognizing that this problem has no retrieval component — it has a calculation component. Those require different architectures.

The system is built on a strict separation of concerns:

- **Claude handles language** — routing, intent classification, parameter extraction, prose composition
- **Python handles math** — six deterministic formula functions that own all arithmetic
- **Claude never calculates.** It calls typed functions that do.

This makes the system trustworthy by design, not by instruction. Every number in every response traces back to a Python function return value — not Claude's inference.

---

## Try It

The tool understands plain English questions about the headcount model. You don't need to use specific phrasing — ask naturally.

**The model covers three regions:** NAMER, EMEA, and APAC, each with their own active agent count, average handle time (AHT), and projected ticket volume.

**Global assumptions** apply across all regions: working hours per month, shrinkage rate, and utilization target.

### Example questions

**Data retrieval**
> "How many active agents do we currently have in EMEA, and what is our assumed shrinkage rate?"

**Capacity calculation**
> "Based on our current metrics, what is the maximum number of tickets our NAMER team can handle next month?"

**What-if scenario**
> "If ticket volume in APAC increases by 30% and handle time increases by 2 minutes, how many net-new agents do we need to hire?"

**Utilization check**
> "What utilization rate is EMEA currently running at given their projected volume?"

**Staffing gap**
> "Are we overstaffed or understaffed in NAMER next month?"

**Global view**
> "Give me a full staffing gap analysis across all regions."

The tool will tell you clearly if a question falls outside the model's scope — costs, attrition rates, historical trends, and similar inputs aren't in this dataset.

---

## How It Works

```
User types question
       ↓
React chat UI
       ↓ POST /chat
FastAPI backend
       ↓
Claude Sonnet (routing step)
Reads the question, identifies relevant regions and tables,
fetches only what is needed from Supabase
       ↓ selective fetch
Supabase returns targeted model data
       ↓
Claude Sonnet (orchestrator)
Receives question + relevant data, extracts parameters,
calls the appropriate formula tool
       ↓ tool call + params
Formula engine (pure Python) executes math deterministically
       ↓ typed result dict with all intermediate values
Claude Sonnet (composer)
Writes natural language answer from returned values only —
never infers or calculates
       ↓
Frontend renders answer + formula tags showing which tools were called
```

Claude appears three times by design — as router, orchestrator, and composer. It never performs arithmetic in any role.

---

## Why Selective Fetching Matters

On a small dataset, fetching everything on every request would work. But it doesn't scale — a production headcount model with dozens of regions, historical snapshots, and multiple metrics would exceed Claude's context window and introduce unnecessary latency and cost.

The routing step solves this by semantically understanding the question before touching the database. A question about APAC fetches only APAC data. A question about utilization fetches only the tables needed to calculate it. The routing step understands natural language region references — "Asia Pacific team" resolves to APAC, "European region" resolves to EMEA — without requiring exact terminology.

This means the architecture genuinely scales to a production dataset. Add regions, add tables, add metrics — describe them to the routing step and it handles the rest. No hardcoded fetch logic to maintain.

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

The formula engine and Claude orchestration are fully decoupled from the data source via a `get_model_data()` abstraction in `db.py`. The routing step determines which regions and tables to fetch on a per-question basis — the system never blindly pulls the full dataset.

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
| AI | Claude Sonnet via Anthropic SDK (routing, tool use, composition) |
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
│   ├── db.py            # Supabase data access, selective get_model_data()
│   ├── formulas.py      # Six pure Python formula primitives
│   ├── tools.py         # Claude tool definitions (JSON schema)
│   └── agent.py         # Claude routing, orchestration, tool dispatch + composition
└── README.md
```

---

## Running Your Own Instance

The live version at [headcount-ai.vercel.app](https://headcount-ai.vercel.app) is the intended entry point. If you want to run a local instance or fork the project with your own data model, you'll need:

- Anthropic API key
- Supabase project with the three tables seeded (schema in `db.py`)
- `backend/.env` with `ANTHROPIC_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- `frontend/.env.local` with `VITE_API_URL=http://localhost:8000`

Backend: `pip install -r requirements.txt` → `python -m uvicorn main:app --reload`

Frontend: `npm install` → `npm run dev`

---

## Built As

A hiring assessment for a Senior AI Program Manager role at a company with a large global customer support team. The brief asked for a prototype that could ingest a headcount model and accurately answer questions without hallucinating. The architecture was designed to make hallucination structurally impossible — not just unlikely.

Built and deployed in less than 24 hours using Claude Code. Planned using a structured five-phase product and engineering framework before any code was written (see: https://victorcaceres.com/thefineprint/how-i-work#:~:text=Planning%20Before%20Doing).
