# Resolve — Agentic AI Customer Support Resolution System

An end-to-end multi-agent customer support system: a FastAPI + LangGraph backend
that triages, retrieves policy/FAQ knowledge (RAG), proposes and selectively
executes resolutions, escalates high-risk cases to humans, and reviews its own
output — paired with a React + TypeScript + Tailwind support console.

---

## 1. Architecture overview

```
                         ┌─────────────────────────────┐
                         │        React Frontend        │
                         │  (chat UI + ticket dashboard) │
                         └───────────────┬───────────────┘
                                         │ JWT-authenticated REST
                                         ▼
                         ┌─────────────────────────────┐
                         │        FastAPI Backend        │
                         │   /auth  /chat  /tickets       │
                         └───────────────┬───────────────┘
                                         │
                                         ▼
                    ┌───────────────────────────────────────┐
                    │        LangGraph Agent Pipeline         │
                    │                                          │
                    │  Triage → Customer Context → Knowledge   │
                    │  Retrieval → Resolution → Escalation →   │
                    │  Decision/Reviewer                       │
                    └───────────────┬───────────────┬─────────┘
                                    │               │
                     ┌──────────────┘               └──────────────┐
                     ▼                                              ▼
         ┌───────────────────────┐                    ┌────────────────────────┐
         │  ChromaDB (RAG store)  │                    │  PostgreSQL (tickets,   │
         │  FAQs / docs / policy  │                    │  accounts, agent logs,  │
         └───────────────────────┘                    │  escalation records)    │
                                                        └────────────────────────┘
                     ▲
                     │
         ┌───────────────────────┐
         │  Redis (short-term     │
         │  multi-turn memory)    │
         └───────────────────────┘
```

### Agent responsibilities

| Agent | Responsibility |
|---|---|
| **Triage Agent** | Classifies category (billing/technical/subscription/account/product/service_request/other), determines priority, summarizes intent. |
| **Customer Context Agent** | Pulls account/subscription/billing facts from PostgreSQL (cached in Redis); maintains multi-turn context. Pure information retrieval. |
| **Knowledge Retrieval Agent** | RAG search over FAQs, product docs, and support policies (ChromaDB). Returns labeled, cited source chunks — never presented as final answer text. |
| **Resolution Agent** | Produces a diagnosis, step-by-step guidance, and a list of **recommended actions**. Executes only a small **whitelist of low-risk tool calls** automatically (e.g. resend confirmation email, retry payment, send password reset link). |
| **Escalation Agent** | Decides if a human rep is required (high-risk action, critical priority, risk flags on the account) and writes a handoff summary. |
| **Decision/Reviewer Agent** | Final QA gate — checks accuracy/relevance/completeness against retrieved knowledge, and produces the actual customer-facing `final_response`. |

### The three-way action distinction (core requirement)

The system always keeps these separate, both internally and in the API/UI:

1. **Information retrieved** — `retrieved_knowledge` (RAG chunks), `account context` facts. Never treated as an instruction.
2. **Recommended actions** — `recommended_actions`: things the Resolution Agent proposes but does **not** execute (e.g. "Issue refund for duplicate charge").
3. **Actions actually performed** — `actions_performed`: only low-risk, whitelisted tool calls the system is authorized to run automatically (see `backend/app/agents/tools.py`). Anything touching money, cancellations, account deletion, identity/ownership changes, or data export is **never** auto-executed — it is routed to the Escalation Agent instead, enforced by both an LLM judgment call and a deterministic keyword/policy check as a safety net.

---

## 2. Tech stack

**Backend:** Python, FastAPI, LangGraph (agent orchestration), OpenAI API (LLM + embeddings, swappable), Pydantic, async SQLAlchemy, JWT auth.
**Frontend:** React 18, TypeScript, Tailwind CSS, React Router, Axios.
**Data:** PostgreSQL (persistent ticket history & accounts), Redis (short-term conversation memory), ChromaDB (RAG vector store).
**Deployment:** Backend → Render (`render.yaml` blueprint provided). Frontend → Vercel (`vercel.json` provided).

---

## 3. Repository layout

```
support-ai/
├── backend/
│   ├── app/
│   │   ├── agents/          # 6 agents + LangGraph graph + shared state/schemas/tools
│   │   ├── api/routes/      # auth, chat, tickets
│   │   ├── core/            # config, security (JWT), LLM client
│   │   ├── db/              # SQLAlchemy models, Postgres session, Redis client
│   │   ├── kb/               # seed knowledge-base documents
│   │   ├── rag/              # ChromaDB vector store wrapper
│   │   ├── schemas/          # Pydantic API request/response models
│   │   ├── services/         # ticket persistence service layer
│   │   └── main.py           # FastAPI app entrypoint
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml    # local Postgres + Redis + backend
│   ├── render.yaml           # Render deployment blueprint
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/               # Axios client
    │   ├── components/        # ChatPanel, TicketList, TicketDetailPanel, AgentTimeline, badges
    │   ├── context/           # AuthContext
    │   ├── pages/              # Login, Register, Dashboard
    │   └── App.tsx / main.tsx
    ├── vercel.json
    └── .env.example
```

---

## 4. Running locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (recommended, for Postgres + Redis) — or local installs of both
- An OpenAI API key (or adapt `app/core/llm_client.py` / `app/rag/vector_store.py` for another provider — the seams are marked)

### Backend

```bash
cd backend
cp .env.example .env        # fill in OPENAI_API_KEY, JWT_SECRET_KEY, etc.

# Start Postgres + Redis
docker compose up -d postgres redis

# Install deps
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the API (tables auto-created on startup for dev; use Alembic for prod migrations)
uvicorn app.main:app --reload
```

The API will be live at `http://localhost:8000`, docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
cp .env.example .env        # VITE_API_BASE_URL=http://localhost:8000/api/v1
npm install
npm run dev
```

Visit `http://localhost:5173`, register an account, and start a conversation.

### Try it

Send: *"I was charged twice for my subscription this month. Please check the issue and tell me what I should do."*

Expected flow: Triage classifies as `billing` / high priority → Customer Context pulls the account's billing facts → Knowledge Retrieval surfaces the duplicate-charge and refund policies → Resolution Agent diagnoses the duplicate charge and recommends a refund (flagged **high-risk**, since refunds move money) → Escalation Agent routes it to a human billing specialist → Reviewer Agent writes the final customer-facing message explaining the case was escalated.

---

## 5. Deployment

### Backend → Render
1. Push this repo to GitHub.
2. In Render, create a new **Blueprint** from `backend/render.yaml` (creates the web service, a Postgres DB, and a Redis instance together).
3. Set the `OPENAI_API_KEY` env var (marked `sync: false` in the blueprint, so Render will prompt for it).
4. Update `CORS_ORIGINS` once your Vercel frontend URL is known.

### Frontend → Vercel
1. Import the `frontend/` directory as a new Vercel project (framework preset: Vite).
2. Set `VITE_API_BASE_URL` to your deployed Render backend URL + `/api/v1`.
3. Deploy — `vercel.json` handles SPA routing rewrites.

---

## 6. Security & risk-handling notes

- JWT auth on every route except `/auth/register` and `/auth/login`; tokens expire after 8 hours by default.
- Passwords hashed with bcrypt.
- High-risk actions (`refund`, `account_deletion`, `subscription_cancellation`, `chargeback_dispute`, `data_export`, `identity_change`) are defined centrally in `app/core/config.py` and checked deterministically in addition to LLM judgment before anything is auto-executed or exempted from escalation.
- All tool calls in `app/agents/tools.py` are mocked for this reference implementation (safe to run without live billing/CRM credentials) — swap in real API integrations for production use, keeping the low-risk/high-risk boundary intact.

---

## 7. What maps to the assignment's "Expected Output"

The `TicketDetailPanel` component (frontend) and `TicketDetailOut` schema (backend) surface every required field: ticket status (resolved / requires more information / escalated), customer query, issue category, priority, retrieved knowledge, suggested resolution, recommended vs. performed actions, escalation status, full agent execution history (with per-agent timing), and the final response.
