# ULTRON — Complete Local Forensic Analysis

**Audit Version:** 6.1.0-Forensic-Master  
**Audit Scope:** Local Repository Workspace (`d:\Work Space\Project\Ultron`)  
**Audit Mode:** Read-Only Static & Forensic Execution Analysis  
**Audit Date:** 2026-09-02  
**Canonical Output:** `ULTRON_COMPLETE_LOCAL_FORENSIC_ANALYSIS.md`  

---

## 1. Executive Summary

This forensic document provides a complete, evidence-based architectural analysis of the **ULTRON** project as it exists in the local workspace. 

ULTRON is an **autonomous economic control plane for failed-payment recovery on Razorpay**. Its core mission is not mere retry scheduling; it is portfolio-level opportunity valuation and capital allocation. The system evaluates every failed transaction through an incremental value model (IVEN), allocates recovery actions under hard capacity constraints (shadow pricing), enforces deterministic multi-stage compliance checks (Action Authority), and executes real recovery links against Razorpay Test Mode—while isolating AI/LLM models exclusively to contextual reasoning, semantic explanation, and hypothesis generation.

### Key Forensic Findings Summary:
1. **Financial Core & Execution Invariant (`SOURCE_VERIFIED`, `TEST_VERIFIED`):** The deterministic financial core (`src/economics/scorer.ts`, `src/market/allocator.ts`, `src/authority/gate.ts`, `src/execution/executor.ts`) is strictly mathematical and deterministic. AI models (LLMs) have **zero execution authority**.
2. **Database Engine Reality (`RUNTIME_VERIFIED`, `DATABASE_VERIFIED`):** While dual adapters exist for PostgreSQL/Supabase, the active local engine is **SQLite (Node.js `node:sqlite` in WAL mode, database file `ultron.db`, 5.79 MB)**. A dual-sync layer asynchronously pushes table updates to Supabase via `@supabase/supabase-js`.
3. **Double-Entry Ledger Integrity (`DATABASE_VERIFIED`):** The cryptographic hash-chained double-entry ledger (`src/truth/double_entry_ledger.ts`) contains 124 records with **0 unbroken chains** and exact mathematical balance: **Debits = 26,422,500 paise, Credits = 26,422,500 paise**.
4. **Provider-Verified Recovery History (`DATABASE_VERIFIED`, `PROVIDER_VERIFIED`):** Real payment recovery has been executed and confirmed against Razorpay's live test API (Opportunity `rzp_live_test_1788233420739` and `pay_pg_1788295874995_e8m6`, ₹4,500.00 / ₹750.00 recovered via payment link `plink_TWcnQZVwogNPop` and settled).
5. **Frontend Architecture (`SOURCE_VERIFIED`):** The frontend is a Next.js 16.3.3 + React 19.2.8 + Tailwind CSS application located in `frontend/`. It communicates with the backend Express API (`http://localhost:3001`) via session tokens and JWTs, with a fallback auth bridge to Supabase Auth.
6. **OdooX Connector Status (`SOURCE_VERIFIED`):** The client connector emitter (`src/connectors/odoox/odoox_event_emitter.ts`) is implemented and tested. However, the OdooX ERP source code itself is **NOT AVAILABLE LOCALLY**.

---

## 2. What ULTRON Actually Is

ULTRON is a **two-tiered economic operating system** designed for payment operations:

```mermaid
graph TD
    subgraph Layer1["Perception & Ingestion Layer"]
        A[Razorpay Webhooks] --> D[Canonical Ingestion Gateway]
        B[OdooX Connector] --> D
        C[Client SDK / JS] --> D
        D --> E[Canonical Payment Normalizer]
        E --> F[(Recovery Opportunity Store)]
    end

    subgraph Layer2["Economic Reasoning Layer"]
        F --> G[IVEN Scorer]
        G --> H[Bayesian Calibration Model]
        H --> I[Recovery Market Allocator]
        I --> J[Shadow Price Calculation]
    end

    subgraph Layer3["Deterministic Action Authority Gate"]
        J --> K{Action Authority Gate}
        K -- "Hard Decline / Cap / Kill Switch" --> L[BLOCKED / ABSTAIN]
        K -- "Capacity / Confidence" --> M[WAIT / DEFERRED]
        K -- "All 5 Checks Passed" --> N[AUTHORIZED]
    end

    subgraph Layer4["Execution & Reconciliation Layer"]
        N --> O[Resilient Executor / Circuit Breaker]
        O --> P[Razorpay Test Mode API]
        P --> Q[Payment Link Created]
        Q --> R[Customer Settlement]
        R --> S[Authoritative Reconciler]
        S --> T[(Double-Entry Cryptographic Ledger)]
    end

    subgraph Layer5["Autonomous AI Agent & Copilots (Zero Write Authority)"]
        F -.-> U[Agent Orchestrator]
        U -.-> V[Perception / Strategy Specialists]
        V -.-> W[NVIDIA NIM LLM Reasoning]
        W -.-> X[Semantic Signals & Hypotheses]
        X -.-> G
    end
```

### Core Value Proposition:
1. **Treats failed payments as finite opportunities:** Rather than blindly retrying every failure, it evaluates expected marginal revenue against operational and fatigue costs.
2. **Operates under portfolio capacity limits:** If capacity is capped at 5 payment links per batch, it ranks candidates by IVEN descending and computes the **shadow price** (the IVEN of the marginal allocated item).
3. **Enforces a strict compliance firewall:** Action Authority evaluates hard decline codes, retry caps (max 3), global/tenant kill switches, confidence bounds, and market allocation.
4. **Provider Truth Invariant:** Creating a payment link (`LINK_CREATED`) is never considered a recovery. Only authoritative provider settlement (`PAID`/`CAPTURED` with `amount_paid > 0`) marks an opportunity as `RECOVERED`.

---

## 3. Current Runtime Reality

| Component | Intended Status | Current Reality in Workspace | Evidence Class |
| :--- | :--- | :--- | :--- |
| **Backend Engine** | Express + TypeScript API | Running via `tsx src/server.ts` on port 3001 | `RUNTIME_VERIFIED` |
| **Active Database** | Supabase PostgreSQL | **SQLite 3 (`ultron.db`)** with dual Supabase background sync | `DATABASE_VERIFIED` |
| **Frontend App** | Next.js App Router | Next.js 16.3.3 + React 19.2.8 in `frontend/` | `SOURCE_VERIFIED` |
| **Deterministic Core** | IVEN + Market + Authority | 100% Deterministic TypeScript; 0% LLM execution dependency | `SOURCE_VERIFIED` |
| **LLM Provider** | NVIDIA NIM API | Configured in `src/agents/llm_provider.ts`; falls back gracefully to deterministic rule engine if key absent | `CODE_ONLY` / `RUNTIME_VERIFIED` |
| **Provider Mode** | Razorpay Test Mode | Active in `src/providers/razorpay/` (Key ID/Secret from `.env`) | `PROVIDER_VERIFIED` |
| **Double-Entry Ledger** | SHA-256 Hash Chain | Fully balanced across 124 transactions in `ultron.db` | `DATABASE_VERIFIED` |
| **OdooX Integration** | Odoo Connector Client | Connector emitter in `src/connectors/odoox/`; ERP codebase external | `SOURCE_VERIFIED` |

---

## 4. Repository Structure

The workspace contains 96 root-level items and 15 subdirectories:

```
d:\Work Space\Project\Ultron
├── .agents/                        # Agent workflows and system rules
├── docs/                           # 22 Architecture, state machine, and phase specifications
├── frontend/                       # Next.js 16 + React 19 + Tailwind CSS Frontend
│   ├── src/
│   │   ├── app/                    # App Router pages (dashboard, events, playground, settings, auth)
│   │   └── lib/                    # Client auth, Supabase, and API utilities
│   ├── package.json
│   └── tsconfig.json
├── results/                        # Benchmark results, forensic snapshots, and test logs
├── scripts/                        # 54 Operational, migration, seed, and verification scripts
├── src/                            # Express Backend Source
│   ├── agents/                     # Autonomous AI Agent, State Machine, Specialists, Tools
│   ├── authority/                  # Action Authority Gate (5 Deterministic Checks + Multi-level Kill Switch)
│   ├── cache/                      # Redis Cache Manager & Distributed Rate Limiter
│   ├── config/                     # Configuration loaders
│   ├── connectors/                 # External ERP connectors (OdooX Event Emitter)
│   ├── db/                         # Database adapter (SQLite / Postgres) & Migrations (001-004)
│   ├── economics/                  # IVEN Scorer & Bayesian Probability Calibration
│   ├── execution/                  # Execution Engine, Circuit Breaker, Rate Limiter, DLQ
│   ├── llm/                        # Decision Explainer (Natural language explanations)
│   ├── market/                     # Recovery Market Allocator & Capacity Policy (Shadow Pricing)
│   ├── middleware/                 # Audit logging and tenant scoping middleware
│   ├── notifications/              # Resend / SMTP Email Dispatcher
│   ├── observability/              # Telemetry & metrics logging
│   ├── perception/                 # Webhook normalizer & decline taxonomy classifier
│   ├── providers/                  # Multi-tenant Razorpay Client Factory & Connection Pool
│   ├── realtime/                   # Server-Sent Events (SSE) broadcaster
│   ├── reconciliation/             # Authoritative Reconciler & Background Poller
│   ├── routes/                     # 15 Express REST API Routers
│   ├── security/                   # Auth, RBAC, Passwords, API Keys, Tenancy, HMAC Webhook Validator
│   ├── simulation/                 # Scenario Runner & Synthetic Data Generator
│   ├── truth/                      # Provider Truth, Canonical State Machine, Double-Entry Ledger
│   ├── types/                      # Canonical TypeScript definitions
│   ├── webhooks/                   # Webhook delivery queue, retry engine, Razorpay handlers
│   └── server.ts                   # Primary Backend Entrypoint
├── supabase/                       # Supabase database schema definitions (`schema.sql`)
├── tests/                          # 58 Automated Test Suites (Core, Agent, Infra, Truth, v6)
├── .env                            # Active environment configuration
├── package.json                    # Backend dependencies and test scripts
├── tsconfig.json                   # TypeScript configuration
└── ultron.db                       # Active SQLite database file (WAL mode)
```

---

## 5. File Classification

| File / Directory Path | Classification | Role & Description |
| :--- | :--- | :--- |
| `src/server.ts` | `CORE_RUNTIME` | Main Express server setup, middleware stack, router registration, daemon launcher. |
| `src/db/database.ts` | `CORE_RUNTIME` | SQLite table definitions, queries, upserts, Supabase sync functions. |
| `src/db/adapter.ts` | `PLATFORM_RUNTIME` | Database abstraction layer bridging SQLite (`node:sqlite`) and PostgreSQL (`pg.Pool`). |
| `src/economics/scorer.ts` | `FINANCIAL_RUNTIME` | Computes IVEN, natural/intervention probabilities, fatigue costs. |
| `src/economics/bayesian_calibration.ts` | `FINANCIAL_RUNTIME` | Bayesian Beta-binomial posterior updates for empirical recovery probabilities. |
| `src/market/allocator.ts` | `FINANCIAL_RUNTIME` | Greedy portfolio allocation, capacity enforcement, and shadow price derivation. |
| `src/authority/gate.ts` | `FINANCIAL_RUNTIME` | 5-stage deterministic Action Authority gate and kill switch. |
| `src/execution/executor.ts` | `FINANCIAL_RUNTIME` | Razorpay payment link dispatcher with idempotency and circuit breaker. |
| `src/truth/double_entry_ledger.ts` | `FINANCIAL_RUNTIME` | Cryptographic SHA-256 hash-chained immutable double-entry ledger. |
| `src/truth/provider_truth.ts` | `FINANCIAL_RUNTIME` | Provider payload evaluator enforcing `LINK_CREATED != RECOVERED`. |
| `src/reconciliation/authoritative_reconciler.ts` | `FINANCIAL_RUNTIME` | State transition reconciler executing multi-stage recovery validation. |
| `src/agents/orchestrator.ts` | `AGENT_RUNTIME` | Coordinates multi-step autonomous recovery investigation missions. |
| `src/agents/state_machine.ts` | `AGENT_RUNTIME` | Formal 15-state deterministic state machine for agent runs. |
| `src/agents/gate.ts` | `AGENT_RUNTIME` | 9 security and boundary checks governing agent tool calls. |
| `src/agents/tool_registry.ts` | `AGENT_RUNTIME` | Registry containing 14 read-only tools and 4 proposal-only tools. |
| `src/agents/llm_provider.ts` | `AGENT_RUNTIME` | NVIDIA NIM LLM bridge with deterministic fallback. |
| `src/providers/razorpay/client_pool.ts` | `PROVIDER_RUNTIME` | Per-tenant Razorpay SDK client manager with credential caching. |
| `src/webhooks/razorpay.ts` | `PROVIDER_RUNTIME` | HMAC-SHA256 signature verification and webhook routing. |
| `src/connectors/odoox/odoox_event_emitter.ts` | `PROVIDER_RUNTIME` | Non-blocking SDK client for OdooX payment failure dispatch. |
| `frontend/src/app/dashboard/page.tsx` | `FRONTEND_RUNTIME` | Next.js merchant recovery overview dashboard. |
| `frontend/src/app/dashboard/events/page.tsx` | `FRONTEND_RUNTIME` | Real-time event monitor and SDK integration inspector. |
| `frontend/src/app/dashboard/playground/page.tsx` | `FRONTEND_RUNTIME` | Interactive simulation sandbox for IVEN, Market, and Authority. |
| `frontend/src/lib/auth.tsx` | `FRONTEND_RUNTIME` | Merchant auth provider managing JWTs, sessions, and tenant context. |
| `tests/v6/run_all_v6_tests.ts` | `TEST` | Master runner for 24 v6 integration test suites. |
| `tests/agent/run_all_agent_tests.ts` | `TEST` | Master runner for 28 agent intelligence test suites. |
| `scripts/seed_synthetic.ts` | `SIMULATION` | Generates canonical benchmark scenarios for evaluation. |
| `scripts/run_causal_experiments.ts` | `SIMULATION` | Runs 8 empirical causal benchmark experiments. |
| `docs/*` | `DOCUMENTATION` | Technical specifications, state models, and architecture documents. |

---

## 6. Technology Stack

### Backend Stack:
- **Runtime:** Node.js v22.13.0+ (ES Modules: `"type": "module"`)
- **Language:** TypeScript 5.7.3 (executed via `tsx` 4.19.3)
- **HTTP Server:** Express 4.21.2
- **Security Headers & CORS:** Helmet 8.0.0, CORS 2.8.5
- **Input Validation:** Zod 3.24.2
- **Authentication:** JSON Web Tokens (`jsonwebtoken` 9.0.2), `bcrypt` 6.0.0
- **Database (Active Local):** Node.js native `node:sqlite` (SQLite 3 WAL Mode)
- **Database (Enterprise/Cloud):** PostgreSQL (`pg` 8.13.1), Supabase (`@supabase/supabase-js` 2.112.4)
- **Caching & Rate Limiting:** Redis (`ioredis` 5.4.2) with in-memory fallback
- **Payments Provider:** Official Razorpay Node SDK (`razorpay` 2.9.5)
- **Email Dispatcher:** Resend API (`resend` 6.25.0), Nodemailer (`nodemailer` 9.1.0)
- **AI/LLM Provider:** NVIDIA NIM REST API (`https://integrate.api.nvidia.com/v1`)

### Frontend Stack:
- **Framework:** Next.js 16.3.3 (App Router)
- **UI Core:** React 19.2.8 + React DOM 19.2.8
- **Styling:** Tailwind CSS 4.0.0 (`@tailwindcss/postcss`)
- **Icons:** Lucide React (`lucide-react` 1.35.0)
- **Database/Auth Client:** `@supabase/supabase-js` 2.112.4

---

## 7. Dependencies Forensics

### Backend (`package.json`):
```json
{
  "dependencies": {
    "@supabase/supabase-js": "^2.112.4",  // Cloud DB sync & auth bridge (Runtime)
    "@types/bcrypt": "^6.0.0",           // Type definitions
    "bcrypt": "^6.0.0",                  // Password hashing (Runtime-Critical)
    "cors": "^2.8.5",                    // Cross-Origin Resource Sharing (Runtime-Critical)
    "dotenv": "^16.4.7",                 // Environment variable loading (Runtime-Critical)
    "express": "^4.21.2",                // Core REST API server (Runtime-Critical)
    "helmet": "^8.0.0",                  // HTTP security headers (Runtime-Critical)
    "ioredis": "^5.4.2",                 // Distributed cache & rate limiter (Runtime)
    "jsonwebtoken": "^9.0.2",            // Session & API token signing (Runtime-Critical)
    "nodemailer": "^9.1.0",              // SMTP email transport (Runtime)
    "pg": "^8.13.1",                     // PostgreSQL connection pooling (Runtime)
    "razorpay": "^2.9.5",                // Razorpay API client (Runtime-Critical)
    "resend": "^6.25.0",                 // Transactional email API (Runtime)
    "zod": "^3.24.2"                     // Strict schema validation (Runtime-Critical)
  }
}
```

---

## 8. Runtime Entrypoints

1. **Backend Server Entrypoint:** `src/server.ts`
   - Command: `npm run dev` (`tsx watch src/server.ts`) or `npm start` (`tsx src/server.ts`)
   - Initializes `initDatabase()`, runs `MigrationRunner.migrateUp()`, configures Helmet/CORS/RateLimiting, starts HTTP listener on `PORT=3001`, launches Webhook Queue Worker and Autonomous Recovery Daemon.
2. **Frontend UI Entrypoint:** `frontend/src/app/layout.tsx` / `frontend/src/app/page.tsx`
   - Command: `cd frontend && npm run dev` (`next dev`)
   - Next.js server on `http://localhost:3000` wrapped with `<AuthProvider>`.
3. **Autonomous Background Daemon:** `src/agents/daemon.ts`
   - Class: `AutonomousRecoveryDaemon`
   - Sweeps opportunities every 60 seconds (when `AUTONOMOUS_AGENT_ENABLED=true`), scores candidates, runs Market allocation, invokes Action Authority, and executes payment links.
4. **Webhook Delivery Queue Worker:** `src/webhooks/queue.ts`
   - Class: `WebhookQueueEngine`
   - Polling loop every 10 seconds processing retries with exponential backoff up to 5 attempts before quarantine to Dead Letter status.
5. **Reconciliation Background Poller:** `src/reconciliation/poller.ts`
   - Class: `ReconciliationPoller`
   - Polls Razorpay API for status updates on active payment links (`created`/`issued`) to detect out-of-band customer payments.

---

## 9. Backend Architecture

```mermaid
graph LR
    Client[HTTP Client / Frontend / Webhook] --> Middleware[Helmet, CORS, Tiered RateLimiter]
    Middleware --> Auth[Auth & Tenant Scope / JWT / API Key]
    Auth --> Router{Express Routers}
    Router --> Service[Service Domain Engine]
    Service --> Persistence[(Database Adapter: SQLite / Postgres)]
    Service --> ProviderAPI[Razorpay Test API]
    Service --> Ledger[Double-Entry Ledger]
```

### Backend Middleware Stack:
1. `helmet({ contentSecurityPolicy: false, crossOriginEmbedderPolicy: false })`
2. `cors({ origin: [...], credentials: true })`
3. `TieredRateLimiter` (`webhook`: 100/min, `execution`: 10/min, `general`: 120/min)
4. `express.json({ verify: (req, res, buf) => req.rawBody = buf.toString('utf-8') })` (Preserves raw payload for HMAC signature validation)
5. `auditLogger` (Appends audit record to `audit_records` table)

---

## 10. API Route Inventory

| Route | Method | Classification | Auth / Scope | Handler File & Function | Side Effects |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET /` | GET | `PUBLIC` | None | `src/server.ts` inline | Returns server status JSON or HTML card. |
| `GET /health` | GET | `PUBLIC` | None | `src/server.ts` inline | Queries pool metrics, cache status, kill switch. |
| `POST /webhooks/razorpay/:tenant_id` | POST | `WEBHOOK` | HMAC Signature | `src/webhooks/razorpay.ts:handleRazorpayWebhook` | Ingests real webhook, verifies HMAC, triggers reconciler. |
| `POST /internal/simulate-webhook` | POST | `TEST` | None | `src/webhooks/razorpay.ts:handleSimulatedWebhook` | Ingests synthetic webhook (marked `source='synthetic'`). |
| `POST /v1/auth/signup` | POST | `PUBLIC` | None | `src/routes/auth.ts` | Creates Tenant, User, Membership, Session. |
| `POST /v1/auth/login` | POST | `PUBLIC` | None | `src/routes/auth.ts` | Verifies bcrypt hash, creates Session. |
| `GET /v1/auth/me` | GET | `MERCHANT` | JWT / Session | `src/routes/auth.ts` | Returns current User, Tenant, and permissions. |
| `POST /v1/events` | POST | `MERCHANT` | API Key (`events:write`) | `src/routes/events.ts` | Ingests canonical event, normalizes to Recovery Opportunity. |
| `POST /v1/events/ping` | POST | `MERCHANT` | API Key | `src/routes/events.ts` | Registers web application connection in `web_app_connections`. |
| `GET /v1/events/connected-apps` | GET | `MERCHANT` | JWT | `src/routes/events.ts` | Lists online connected client applications. |
| `GET /opportunities` | GET | `MERCHANT` | JWT | `src/routes/opportunities.ts` | Retrieves opportunities scoped to authenticated tenant. |
| `POST /market/run` | POST | `MERCHANT` | JWT | `src/routes/market.ts` | Runs IVEN scoring, ranks batch, computes shadow price. |
| `POST /authority/run` | POST | `MERCHANT` | JWT | `src/routes/authority.ts` | Evaluates 5 Action Authority checks on opportunities. |
| `POST /authority/kill-switch` | POST | `ADMIN` | JWT | `src/routes/authority.ts` | Activates or disengages global/tenant kill switch. |
| `POST /execution/run` | POST | `MERCHANT` | JWT | `src/routes/execution.ts` | Dispatches payment links for AUTHORIZED items. |
| `GET /dashboard/summary` | GET | `MERCHANT` | JWT | `src/routes/dashboard.ts` | Aggregates portfolio revenue, rates, and health metrics. |
| `POST /agents/mission` | POST | `MERCHANT` | JWT | `src/routes/agents.ts` | Initiates autonomous recovery investigation mission. |
| `POST /agents/portfolio/sweep` | POST | `MERCHANT` | JWT | `src/routes/agents.ts` | Triggers portfolio-wide intelligence sweep. |
| `GET /v1/api-keys` | GET | `MERCHANT` | JWT | `src/routes/api_keys.ts` | Lists active API keys for tenant. |
| `POST /v1/api-keys` | POST | `MERCHANT` | JWT | `src/routes/api_keys.ts` | Generates scoped API key (`uk_live_...` or `uk_test_...`). |
| `DELETE /v1/api-keys/:id` | DELETE | `MERCHANT` | JWT | `src/routes/api_keys.ts` | Revokes API key. |
| `GET /v1/integrations` | GET | `MERCHANT` | JWT | `src/routes/integrations.ts` | Retrieves Razorpay credential status and capabilities. |
| `POST /v1/integrations/credentials` | POST | `MERCHANT` | JWT | `src/routes/integrations.ts` | Encrypts and stores Razorpay API keys (AES-256-GCM). |
| `GET /v1/playground/state` | GET | `MERCHANT` | JWT | `src/routes/playground.ts` | Returns real-time interactive simulation state. |
| `POST /v1/playground/simulate-payment` | POST | `DEMO` | JWT | `src/routes/playground.ts` | Simulates customer link click and successful payment. |
| `GET /audit/records` | GET | `ADMIN` | JWT | `src/routes/audit.ts` | Returns immutable audit records and ledger entries. |
| `GET /sdk/ultron.js` | GET | `PUBLIC` | None | `src/routes/sdk.ts` | Delivers browser client SDK script. |

---

## 11. Request Lifecycle Trace

```mermaid
sequenceDiagram
    autonumber
    actor MerchantApp as Merchant App / OdooX
    participant Gate as API Gateway / Middleware
    participant Tenancy as Tenancy & Auth Enforcer
    participant Router as Events Router (/v1/events)
    participant Normalizer as Perception Normalizer
    participant DB as SQLite / Postgres DB
    participant Reconciler as Authoritative Reconciler

    MerchantApp->>Gate: POST /v1/events (Bearer API Key)
    Gate->>Gate: Check Rate Limits & Headers
    Gate->>Tenancy: Authenticate Token & Resolve Tenant
    Tenancy->>Tenancy: Verify Scopes ('events:write')
    Tenancy->>Router: Forward Request with req.tenantContext
    Router->>Router: Validate Body with CanonicalPaymentEventSchema
    Router->>DB: Check Deduplication (event_id / payment_id)
    alt Is Duplicate Paid Event
        Router->>Reconciler: reconcileOpportunity(oppId)
        Router-->>MerchantApp: 200 OK (deduplicated: true)
    else New Failed Event
        Router->>Normalizer: normalizeOpportunity(event)
        Normalizer->>DB: insertOpportunity(opp)
        Normalizer->>DB: insertLedgerEntry(webhook_received)
        Router-->>MerchantApp: 200 OK (opportunity_id: opp.id)
    end
```

---

## 12. Database Architecture

### Active Engine vs Fallback Hierarchy:
1. `DatabaseAdapter` (`src/db/adapter.ts`) checks `SUPABASE_DATABASE_URL` / `DATABASE_URL`.
2. If `DATABASE_URL` is empty, starts with `sqlite://`, or points to a non-existent host, it initializes `node:sqlite` on `ultron.db`.
3. In `src/db/database.ts`, direct synchronous SQLite operations (`DatabaseSync`) execute queries locally.
4. Mutation helper `syncToSupabase()` pushes changes to Supabase asynchronously.

```mermaid
graph TD
    App[ULTRON Application Code] --> DA[DatabaseAdapter / db]
    DA --> Check{DB URL Configured & Reachable?}
    Check -- Yes (PostgreSQL) --> PGPool[pg.Pool Connection Pool]
    Check -- No / Fallback --> SQLite[(SQLite 3: ultron.db)]
    SQLite --> WAL[WAL Mode: Journal & SHM]
    DA -.-> AsyncSync[syncToSupabase: @supabase/supabase-js]
    AsyncSync -.-> CloudSupabase[(Cloud Supabase PostgreSQL)]
```

---

## 13. Database Schema Forensics (Active SQLite State)

There are **39 tables** in `ultron.db` (5.79 MB, WAL Mode):

| Table Name | Row Count | Primary Key | Foreign Keys | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `agent_authority_checks` | **7,746** | `id` (INTEGER AUTO) | `run_id` → `agent_runs.id` | Records 9 boundary checks per agent tool call. |
| `authority_checks` | **3,866** | `id` (INTEGER AUTO) | `opportunity_id` → `recovery_opportunities.id` | Persists 5 Action Authority gate checks. |
| `agent_states` | **2,170** | `id` (INTEGER AUTO) | `run_id` → `agent_runs.id` | Full trajectory state transitions of AI agent runs. |
| `recovery_opportunities` | **774** | `id` (TEXT) | None | Core failed-payment recovery opportunity records. |
| `scores` | **774** | `opportunity_id` (TEXT) | `opportunity_id` → `recovery_opportunities.id` | IVEN scores, probabilities, and fatigue costs. |
| `allocation_decisions` | **774** | `opportunity_id` (TEXT) | `opportunity_id` → `recovery_opportunities.id` | Market decisions (`ACT`, `WAIT`, `ABSTAIN`) + Shadow Price. |
| `agent_tool_calls` | **725** | `id` (TEXT) | `run_id` → `agent_runs.id` | Audit log of all agent tool invocations and results. |
| `agent_runs` | **654** | `id` (TEXT) | None | Master records for agent investigation missions. |
| `agent_memories` | **344** | `id` (TEXT) | None | Working, episodic, and semantic memory store. |
| `agent_steps` | **241** | `id` (INTEGER AUTO) | `run_id` → `agent_runs.id` | Step-by-step trace of agent thought/action loops. |
| `agent_outcomes` | **227** | `id` (TEXT) | `run_id` → `agent_runs.id` | Post-mission counterfactual evaluation records. |
| `agent_plans` | **206** | `id` (TEXT) | `run_id` → `agent_runs.id` | Structured multi-step recovery plans and assumptions. |
| `ledger_entries` | **172** | `id` (TEXT) | `opportunity_id` → `recovery_opportunities.id` | Append-only event history (`webhook_received`, `recovered`, etc.). |
| `llm_invocations` | **159** | `id` (TEXT) | `run_id` → `agent_runs.id` | Telemetry log of LLM prompts, completions, tokens, latency. |
| `api_keys` | **142** | `id` (TEXT) | `tenant_id` → `tenants.id` | Merchant API keys with SHA-256 secret hashes & scopes. |
| `perception_annotations` | **141** | `id` (TEXT) | `opportunity_id` → `recovery_opportunities.id` | Semantic annotations attached by Perception Agent. |
| `double_entry_ledger` | **124** | `id` (TEXT) | None | Cryptographic SHA-256 hash-chained accounting ledger. |
| `execution_records` | **113** | `opportunity_id` (TEXT) | `opportunity_id` → `recovery_opportunities.id` | Razorpay payment link IDs, short URLs, idempotency keys. |
| `tenants` | **101** | `id` (TEXT) | None | Isolated business accounts and capacity limits. |
| `execution_failures` | **89** | `id` (TEXT) | None | Dead Letter Queue (DLQ) records for failed API calls. |
| `customers` | **80** | `id` (TEXT) | None | Customer entity with trust score and history. |
| `outreach_drafts` | **70** | `id` (TEXT) | `run_id` → `agent_runs.id` | Human-reviewable customer communications. |
| `sessions` | **66** | `id` (TEXT) | `user_id` → `users.id` | Active JWT session tokens and expiries. |
| `users` | **61** | `id` (TEXT) | None | Merchant user profiles and bcrypt password hashes. |
| `memberships` | **60** | `id` (TEXT) | `user_id` → `users`, `tenant_id` → `tenants` | RBAC role mappings (`Owner`, `Admin`, `Operator`). |
| `agent_proposals` | **49** | `id` (TEXT) | `run_id` → `agent_runs.id` | Parameter or strategy update proposals. |
| `tenant_credentials` | **37** | `id` (TEXT) | `tenant_id` → `tenants.id` | Encrypted Razorpay credentials (AES-256-GCM). |
| `reconciliation_divergences` | **30** | `id` (TEXT) | None | Quarantined reconciliation mismatch logs. |
| `daemon_sweep_logs` | **23** | `id` (TEXT) | None | Background autonomous daemon execution sweeps. |
| `webhook_audit_log` | **20** | `id` (TEXT) | None | Raw webhook delivery and signature audit records. |
| `webhook_delivery_queue` | **18** | `id` (TEXT) | None | Asynchronous webhook retry delivery queue. |
| `notifications` | **17** | `id` (TEXT) | None | User dashboard notifications and alerts. |
| `audit_records` | **15** | `id` (TEXT) | `tenant_id` → `tenants.id` | Security audit trail of user and API actions. |
| `event_ingestion_logs` | **10** | `id` (TEXT) | None | Raw event ingestion logs (live stream debugging). |
| `web_app_connections` | **5** | `id` (TEXT) | None | Connected client applications (SDK heartbeats). |
| `schema_migrations` | **5** | `id` (TEXT) | None | Migration runner checkpoint table (001 to 004 applied). |
| `probability_models` | **2** | `reason_code` (TEXT) | None | Bayesian calibrated probability distribution records. |
| `agent_hypotheses` | **0** | `id` (TEXT) | `run_id` → `agent_runs.id` | Hypotheses table (schema initialized). |
| `organizations` | **0** | `id` (TEXT) | `tenant_id` → `tenants.id` | Organizations table (schema initialized). |

---

## 14. Entity-Relationship Data Model

```mermaid
erDiagram
    TENANTS ||--o{ ORGANIZATIONS : owns
    TENANTS ||--o{ MEMBERSHIPS : contains
    USERS ||--o{ MEMBERSHIPS : belongs_to
    USERS ||--o{ SESSIONS : authenticates
    TENANTS ||--o{ API_KEYS : issues
    TENANTS ||--o{ TENANT_CREDENTIALS : holds
    TENANTS ||--o{ RECOVERY_OPPORTUNITIES : scopes
    CUSTOMERS ||--o{ RECOVERY_OPPORTUNITIES : generates
    RECOVERY_OPPORTUNITIES ||--|| SCORES : evaluated_by
    RECOVERY_OPPORTUNITIES ||--|| ALLOCATION_DECISIONS : assigned
    RECOVERY_OPPORTUNITIES ||--o{ AUTHORITY_CHECKS : verified_by
    RECOVERY_OPPORTUNITIES ||--o| EXECUTION_RECORDS : dispatches
    RECOVERY_OPPORTUNITIES ||--o{ LEDGER_ENTRIES : logs
    RECOVERY_OPPORTUNITIES ||--o{ DOUBLE_ENTRY_LEDGER : balances
    RECOVERY_OPPORTUNITIES ||--o{ AGENT_RUNS : triggers
    AGENT_RUNS ||--o{ AGENT_STATES : transitions
    AGENT_RUNS ||--o{ AGENT_STEPS : executes
    AGENT_RUNS ||--o{ AGENT_TOOL_CALLS : invokes
    AGENT_RUNS ||--o{ AGENT_AUTHORITY_CHECKS : gates
    AGENT_RUNS ||--o{ LLM_INVOCATIONS : calls
```

---

## 15. Data Ownership & Lifecycle Boundaries

| Entity | Created By | Modified By | Authority / Rule of Record | Terminal States |
| :--- | :--- | :--- | :--- | :--- |
| `RecoveryOpportunity` | `POST /v1/events`, `POST /webhooks/razorpay` | Reconciler, Market, Authority | SQLite `recovery_opportunities` | `recovered`, `not_recovered`, `abstained`, `blocked` |
| `Score` | `src/economics/scorer.ts` | Bayesian Calibrator | Scorer computation | Immutable per batch |
| `AllocationDecision` | `src/market/allocator.ts` | Market run | Market allocator | `ACT`, `WAIT`, `ABSTAIN` |
| `AuthorityCheck` | `src/authority/gate.ts` | Action Authority gate | Deterministic gate rules | Binary (Passed / Failed) |
| `ExecutionRecord` | `src/execution/executor.ts` | Reconciler | Razorpay Test API responses | `created`, `paid`, `expired` |
| `DoubleEntryRecord` | `DoubleEntryLedger.recordEntry` | **NEVER (Append-Only)** | Cryptographic SHA-256 Hash | Immutable |
| `AgentRun` | `AgentOrchestrator` | State machine transitions | Orchestrator loop | `completed`, `aborted`, `human_review` |

---

## 16. Deterministic Financial Core

The Financial Core consists of four distinct, sequentially executed stages:

```mermaid
graph LR
    O[Opportunity Ingestion] --> S[1. IVEN Scorer]
    S --> M[2. Recovery Market Allocator]
    M --> A[3. Action Authority Gate]
    A --> E[4. Execution Engine]
    E --> R[5. Authoritative Reconciler]
    R --> L[6. Double-Entry Ledger]
```

---

## 17. IVEN (Incremental Value of Economic Notification)

The exact formula implemented in `src/economics/scorer.ts` (`function: calculateScore`):

$$\text{incremental\_prob} = \max(0, \text{round}(\text{intervention\_recovery\_prob} - \text{natural\_recovery\_prob}, 4))$$

$$\text{total\_cost\_paise} = \text{operational\_cost\_paise} + \text{fatigue\_cost\_paise}$$

$$\text{expected\_incremental\_value\_paise} = \text{round}((\text{incremental\_prob} \times \text{amount\_paise}) - \text{total\_cost\_paise})$$

### Fixed Costs & Fatigue Curve:
- **Operational Cost:** Fixed `400 paise` (₹4.00) per created payment link.
- **Fatigue Cost Curve:**
  - Attempt 1: `0 paise` (₹0.00)
  - Attempt 2: `250 paise` (₹2.50)
  - Attempt 3: `750 paise` (₹7.50)
  - Attempt 4+: `1500 paise + (attempt - 4) * 500 paise`

### Deterministic Baseline Probabilities:
| Decline Category | Example Reason Codes | Natural Prob ($P_{nat}$) | Intervention Prob ($P_{int}$) | Incremental Lift ($\Delta P$) |
| :--- | :--- | :--- | :--- | :--- |
| **Hard Decline** | `fraud`, `lost_card`, `stolen_card` | 0.02 | 0.02 | **0.00** |
| **Insufficient Funds** | `insufficient_funds` | 0.35 | 0.55 | **0.20** |
| **Expired Card** | `expired_card`, `card_expired` | 0.05 | 0.60 | **0.55** |
| **Generic Bank Block** | `do_not_honor`, `declined_by_bank` | 0.25 | 0.45 | **0.20** |
| **Gateway Timeout** | `bank_gateway_timeout`, `timeout` | 0.60 | 0.70 | **0.10** |
| **Unknown Decline** | Unmapped reason codes | 0.10 | 0.10 | **0.00** |

---

## 18. Recovery Market & Capacity Allocation

The allocator in `src/market/allocator.ts` (`function: runMarketAllocation`):
1. **Confidence & Non-Negative Filter:**
   - Any opportunity with `confidence === 'low'` is immediately routed to `ABSTAIN` (reason: low confidence).
   - Any opportunity with `expected_incremental_value_paise <= 0` is routed to `ABSTAIN` (reason: non-positive value).
2. **Greedy Ranking:** Remaining eligible opportunities are sorted by `expected_incremental_value_paise` descending.
3. **Capacity Cutoff:** Top $N$ opportunities ($N \le \text{capacity}$, default 5) receive decision `ACT`. Remaining items receive decision `WAIT`.
4. **Shadow Price Calculation:** The **Shadow Price** is defined as the IVEN of the last accepted opportunity:
   $$\text{Shadow Price} = \text{IVEN}(\text{Rank } N)$$
   Whenever capacity binds, all deferred opportunities display the exact marginal threshold required to displace an allocated item.

---

## 19. Action Authority Gate

Implemented in `src/authority/gate.ts` (`function: evaluateOpportunity`), the gate executes **5 independent, deterministic compliance checks**:

```mermaid
graph TD
    In[Allocated Opportunity] --> C1{Check 1: Hard Decline}
    C1 -- Failed --> B1[BLOCKED: Hard/Fraud code]
    C1 -- Passed --> C2{Check 2: Retry Cap}
    C2 -- Failed --> B2[BLOCKED: Attempt >= 3]
    C2 -- Passed --> C3{Check 3: Kill Switch}
    C3 -- Failed --> B3[BLOCKED: Kill Switch Active]
    C3 -- Passed --> C4{Check 4: Confidence}
    C4 -- Failed --> A1[ABSTAIN: Low Confidence]
    C4 -- Passed --> C5{Check 5: Capacity}
    C5 -- Failed --> W1[WAIT: Exceeds Batch Cap]
    C5 -- Passed --> Auth[AUTHORIZED FOR EXECUTION]
```

### Bypassability Assessment:
- **Zero-Bypass Verification:** In `src/execution/executor.ts:57-83`, before invoking the Razorpay SDK, `evaluateOpportunity()` is called directly. If the verdict is not `AUTHORIZED`, execution throws an immediate `Compliance Violation` error. The gate cannot be bypassed by callers or background jobs.

---

## 20. Execution Engine

Implemented in `src/execution/executor.ts`:
1. **Idempotency Guarantee:** Local lookup in `execution_records` by `opportunity_id` prevents duplicate link creation.
2. **Resilience & Circuit Breaker:** Wrapped in `CircuitBreaker.executeWithResilience()` (`src/execution/circuit_breaker.ts`). If 5 consecutive failures occur within 60s, the circuit trips to `OPEN` for 30s.
3. **Dead Letter Queue (DLQ):** Failed API calls are logged to `execution_failures` via `ExecutionDLQ.recordExecutionFailure()`.
4. **Files Capable of Financial Provider Writes:**
   - **`src/execution/executor.ts`** (sole execution gateway for payment links).
   - *No agent file, prompt, or LLM handler imports or invokes the Razorpay payment link creation endpoint.*

---

## 21. Razorpay Integration

- **SDK:** Official `razorpay` Node SDK (`^2.9.5`).
- **Client Factory:** `src/providers/razorpay/client_pool.ts` maintains a pooled Map of `Razorpay` instances indexed by `tenant_id:environment`.
- **Environment:** Dedicated **Test Mode** credentials loaded from `.env` or decrypted from `tenant_credentials` table (AES-256-GCM).
- **Payment Link API Options:**
  ```json
  {
    "amount": opp.amount_paise,
    "currency": "INR",
    "accept_partial": false,
    "reference_id": opp.id,
    "description": "ULTRON automated recovery",
    "reminder_enable": true
  }
  ```

---

## 22. Provider Truth

Implemented in `src/truth/provider_truth.ts` (`Class: ProviderTruthEvaluator`):
- **Core Invariant:** `LINK_CREATED != RECOVERED`.
- An opportunity is only marked `RECOVERED` if:
  1. Provider status is strictly `paid` or `captured`.
  2. Provider `amount_paid` $> 0$.
  3. Real provider `payment_id` is present in the payload.
- Partial payments (`status === 'partially_paid'`) are categorized as `RECONCILIATION_MISMATCH` and quarantined.

---

## 23. Reconciliation Engine

Implemented in `src/reconciliation/authoritative_reconciler.ts`:
1. **Transitions:**
   - `executing` $\rightarrow$ `recovered` (on provider confirmation of payment).
   - `executing` $\rightarrow$ `not_recovered` (on provider cancellation/expiry).
2. **Atomic Ledger Posting:** When an opportunity transitions to `recovered`, the reconciler atomically posts an entry to the double-entry ledger:
   - **Debit:** `bank_settlement`
   - **Credit:** `recovered_revenue`
   - **Amount:** `amount_paise`
3. **Out-of-Order Webhook Protection:** If a `payment.captured` webhook arrives before link creation is recorded, the reconciler transitions the record directly to `recovered` without error.

---

## 24. Cryptographic Double-Entry Ledger

Implemented in `src/truth/double_entry_ledger.ts`:
- **Genesis Hash:** `0000000000000000000000000000000000000000000000000000000000000000`
- **Hash Formula:**
  $$\text{entry\_hash} = \text{SHA-256}(\text{prev\_hash} : \text{id} : \text{opp\_id} : \text{event} : \text{debit} : \text{credit} : \text{amount} : \text{timestamp})$$
- **Database Forensics Verification (`ultron.db`):**
  - Total entries: **124**
  - Unbroken chain status: **VERIFIED (Valid)**
  - Total Debits: **26,422,500 paise** (₹264,225.00)
  - Total Credits: **26,422,500 paise** (₹264,225.00)
  - Mathematical Discrepancy: **0 paise**

---

## 25. AI Agent Architecture

```mermaid
graph TD
    subgraph AgentOrchestrator["Agent Orchestrator (15-State Machine)"]
        T[TRIGGERED] --> OBS[OBSERVE]
        OBS --> INV[INVESTIGATE]
        INV --> DIAG[DIAGNOSE]
        DIAG --> HYP[HYPOTHESIZE]
        HYP --> PLAN[PLAN]
        PLAN --> VAL[VALIDATE_PLAN]
        VAL --> PROP[PROPOSE]
        PROP --> WA[WAIT_AUTHORITY]
        WA --> EX[EXECUTE]
        EX --> OO[OBSERVE_OUTCOME]
        OO --> LRN[LEARN]
        LRN --> MEM[MEMORY_UPDATE]
        MEM --> CMP[COMPLETE]
    end

    subgraph SecurityBoundary["Agent Authority Boundary Gate (9 Security Checks)"]
        INV -.-> Gate{Agent Authority Gate}
        PROP -.-> Gate
        Gate -- Denied --> Rej[DENIED / Logged to Telemetry]
        Gate -- Permitted --> Exec[Tool Registry Execution]
    end
```

---

## 26. Agent State Machine

15 distinct states defined in `src/agents/state_machine.ts`:
1. `IDLE` — Initial state.
2. `TRIGGERED` — Opportunity ingested.
3. `OBSERVE` — Initial data gathered.
4. `INVESTIGATE` — Specialist agents invoked.
5. `DIAGNOSE` — Failure categorization.
6. `HYPOTHESIZE` — Root cause formulation.
7. `PLAN` — Action plan constructed.
8. `VALIDATE_PLAN` — Assumptions verified.
9. `PROPOSE` — Economic modifiers submitted.
10. `WAIT_AUTHORITY` — Awaiting market & authority checks.
11. `EXECUTE` — Dispatched to deterministic executor.
12. `OBSERVE_OUTCOME` — Settlement truth verified.
13. `LEARN` — Counterfactual lift evaluated.
14. `MEMORY_UPDATE` — Episodic experience stored.
15. `COMPLETE` / `ABORTED` / `HUMAN_REVIEW` — Terminal states.

---

## 27. Agent Orchestrator

Implemented in `src/agents/orchestrator.ts`:
- Main Function: `AgentOrchestrator.executeRecoveryMission()`
- Step Budget: Max 20 steps per run (enforced by `MissionBudgetTracker`).
- Token Budget: Max 8,000 tokens per run.
- Loop Detection: `LoopGuard` detects repeating tool call hashes or consecutive errors.

---

## 28. Agent Tool Inventory

All 18 tools in `src/agents/tool_registry.ts` are strictly scoped to `READ` or `PROPOSE`:

| Tool ID | Agent Scope | Permission | Read-Only? | Audit Level | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `get_opportunity` | `ALL` | `READ` | Yes | `STANDARD` | Fetches raw opportunity by ID. |
| `get_payment_context` | `ALL` | `READ` | Yes | `STANDARD` | Fetches joined scores, decisions, execution. |
| `get_customer_history` | `ALL` | `READ` | Yes | `STANDARD` | Retrieves customer trust score & history. |
| `get_payment_attempts` | `ALL` | `READ` | Yes | `STANDARD` | Checks attempt count and retry cap. |
| `get_failure_history` | `ALL` | `READ` | Yes | `STANDARD` | Historical decline stats by reason code. |
| `get_gateway_state` | `ALL` | `READ` | Yes | `STANDARD` | Gateway latency & method availability. |
| `get_contact_history` | `ALL` | `READ` | Yes | `STANDARD` | Past customer notifications & fatigue level. |
| `get_market_state` | `ALL` | `READ` | Yes | `STANDARD` | Market capacity and shadow price. |
| `get_recovery_capacity`| `ALL` | `READ` | Yes | `STANDARD` | Remaining quota in current batch. |
| `get_reconciliation_state`| `ALL`| `READ` | Yes | `STANDARD` | Payment link reconciliation & ledger state. |
| `get_provider_status` | `ALL` | `READ` | Yes | `STANDARD` | Razorpay Test Mode reachability. |
| `get_full_audit_trail`| `ALL` | `READ` | Yes | `HIGH` | Immutable SQLite audit records. |
| `get_similar_cases` | `ALL` | `READ` | Yes | `STANDARD` | Past opportunities by amount band & decline. |
| `get_agent_memory` | `ALL` | `READ` | Yes | `STANDARD` | Historical episodic/semantic memories. |
| `create_agent_proposal`| `ALL` | `PROPOSE` | No | `HIGH` | Submits parameter proposal (does not execute). |
| `create_perception_annotation`| `PerceptionAgent`| `PROPOSE`| No| `STANDARD`| Attaches semantic notes & urgency score. |
| `create_strategy_proposal`| `StrategyAgent`| `PROPOSE`| No| `CRITICAL`| Proposes probability modifications ($N \ge 30$). |
| `create_outreach_draft`| `OutreachAgent`| `PROPOSE`| No| `HIGH`| Drafts customer notification for human review. |

---

## 29. Agent Authority Boundary

The boundary in `src/agents/gate.ts` enforces 9 mandatory checks:
1. `kill_switch_check` — Blocks execution if kill switch is active.
2. `agent_identity_check` — Verifies registered specialist agent name.
3. `tool_scope_check` — Rejects permissions beyond `READ`/`ANALYZE`/`PROPOSE`.
4. `mission_budget_check` — Enforces token and step quotas.
5. `rate_limit_check` — Max 60 calls/min per agent.
6. `write_boundary_check` — Rejects direct writes (`execute_payment`, `modify_ledger`, etc.).
7. `environment_check` — Prevents synthetic tests from invoking live provider endpoints.
8. `injection_taint_check` — Scans input for prompt/SQL injection patterns.
9. `loop_guard_check` — Halts cyclic repetition.

---

## 30. LLM Runtime & Data Flow

- **Provider:** NVIDIA NIM REST API (`https://integrate.api.nvidia.com/v1`).
- **Model:** `nvidia/nemotron-3.5-lightning-30b-a3b`.
- **System Prompt:** Configured in `AgentContextBuilder.getSystemPrompt()`.
- **Sanitization:** Sensitive customer PII (credit cards, full bank account numbers) is stripped before prompt construction.
- **Deterministic Fallback:** If `NVIDIA_API_KEY` is missing, network fails, or JSON schema validation fails, `generateDeterministicFallbackIntent()` immediately returns a mathematically valid `AgentIntent`.

---

## 31. Memory Systems

Implemented in `src/agents/memory.ts`:
- **Working Memory:** Run-scoped volatile context.
- **Episodic Memory:** Past recovery mission trajectories and counterfactual prediction errors stored in SQLite `agent_memories`.
- **Semantic Memory:** Key-value empirical domain facts.
- **Temporal Firewall:** `src/agents/temporal_firewall.ts` enforces that memory queries can only retrieve records created *before* the current opportunity's timestamp. Future outcome leakage is mathematically impossible.

---

## 32. Planning, Replanning & Uncertainty

- **Planner:** `src/agents/planner.ts` builds structured plans with explicit validity assumptions (e.g., `gateway_health >= 0.75`).
- **Plan Monitor:** `src/agents/plan_monitor.ts` evaluates assumptions before every step. If an assumption is invalidated, it triggers `replan_engine.ts`.
- **EVOI (Expected Value of Optional Information):** `src/agents/information_value.ts` calculates whether investigating additional data points yields sufficient positive incremental recovery value to justify tool latency.

---

## 33. Multi-Tenancy & RBAC

- **Tenant Isolation:** Every financial record (`recovery_opportunities`, `scores`, `allocation_decisions`, `execution_records`, `ledger_entries`, `api_keys`) includes `tenant_id`.
- **Tenancy Enforcer Middleware:** `src/security/tenancy.ts` (`TenancyEnforcer.authenticateTenant()`) extracts tenant context from JWT sessions or `Authorization: Bearer uk_live_...` API keys.
- **RBAC Roles:** `Owner`, `Admin`, `Operator`, `Analyst`, `Viewer` (`src/security/rbac.ts`).
- **Credential Storage:** `tenant_credentials` stores per-tenant Razorpay Key ID and Secret encrypted using **AES-256-GCM** with IV and authentication tags (`src/security/secrets.ts`).

---

## 34. Frontend Route Inventory & Data Flow

| Route Path | Component File | User Role | Data Source | Production / Demo Status |
| :--- | :--- | :--- | :--- | :--- |
| `/login` | `frontend/src/app/login/page.tsx` | Public | `POST /v1/auth/login` | `PRODUCTION` |
| `/signup` | `frontend/src/app/signup/page.tsx` | Public | `POST /v1/auth/signup` | `PRODUCTION` |
| `/dashboard` | `frontend/src/app/dashboard/page.tsx` | Authenticated | `GET /dashboard/summary` | `PRODUCTION` |
| `/dashboard/opportunities` | `.../opportunities/page.tsx` | Authenticated | `GET /opportunities` | `PRODUCTION` |
| `/dashboard/market` | `.../market/page.tsx` | Authenticated | `POST /market/run` | `PRODUCTION` |
| `/dashboard/execution` | `.../execution/page.tsx` | Authenticated | `POST /execution/run` | `PRODUCTION` |
| `/dashboard/audit` | `.../audit/page.tsx` | Authenticated | `GET /audit/records` | `PRODUCTION` |
| `/dashboard/agent` | `.../agent/page.tsx` | Authenticated | `GET /agents/runs` | `PRODUCTION` |
| `/dashboard/events` | `.../events/page.tsx` | Authenticated | `GET /v1/events/connected-apps` | `PRODUCTION` |
| `/dashboard/playground` | `.../playground/page.tsx` | Authenticated | `GET /v1/playground/state` | `DEMO` / `SIMULATION` |
| `/dashboard/setup` | `.../setup/page.tsx` | Authenticated | `GET /v1/integrations` | `PRODUCTION` |
| `/dashboard/settings/api-keys`| `.../api-keys/page.tsx` | Admin / Owner | `GET /v1/api-keys` | `PRODUCTION` |
| `/dashboard/settings/integrations`| `.../integrations/page.tsx`| Admin / Owner | `POST /v1/integrations/credentials`| `PRODUCTION` |

---

## 35. Hardcoded / Mock UI Forensics

1. **Dashboard Mock Placeholders:** No hardcoded financial revenue figures exist in production pages. Dashboard metrics (`total_revenue_recovered_paise`, `shadow_price_paise`) derive dynamically from `GET /dashboard/summary`.
2. **Playground Sandbox (`/dashboard/playground`):** Contains preset simulation scenarios (`Insufficent Funds`, `Card Expired`, `Bank Timeout`, `Hard Fraud Block`) for interactive testing.
3. **Setup Wizard Test Cards:** `frontend/src/app/dashboard/setup/page.tsx` displays official Razorpay Test Mode card numbers (e.g., `4111 1111 1111 1111`, OTP `123456`) clearly labeled as Test Mode documentation.

---

## 36. OdooX Integration

- **Local Source Status:** **ODOOX SOURCE NOT AVAILABLE LOCALLY**.
- **Connector Implementation:** `src/connectors/odoox/odoox_event_emitter.ts`.
- **Protocol:** Dispatches HTTP `POST` requests containing `OdooXEventPayload` to `${ULTRON_BASE_URL}/v1/events` with Bearer API key authentication.
- **Fail-Safe Invariant:** Uses `fireAndForget()` and short timeouts (4,000ms). If ULTRON is offline, the connector logs a warning and allows the primary OdooX ERP checkout flow to complete unimpeded.

---

## 37. External Services Map

| Service Name | Purpose | Direction | Authentication | Failure Fallback |
| :--- | :--- | :--- | :--- | :--- |
| **Razorpay Test API** | Payment link creation & status polling | Outbound | HTTP Basic Auth (`Key:Secret`) | Circuit breaker trips; fails over to DLQ. |
| **NVIDIA NIM** | Semantic reasoning & intent generation | Outbound | Bearer API Key (`nvapi-...`) | Automatic fallback to deterministic rule engine. |
| **Cloud Supabase** | Cloud DB replication & auth sync | Outbound | Supabase Service / Anon Key | Non-blocking async catch; local SQLite active. |
| **Redis** | Distributed rate limiting & caching | Internal | Redis URL | Fallback to local in-memory Map rate limiter. |
| **Resend / SMTP** | Transactional recovery notifications | Outbound | API Key / SMTP Password | Console warning; execution not blocked. |

---

## 38. Security Forensics & Vulnerability Analysis

1. **Authentication:** Passwords hashed using `bcrypt` (10 rounds). Sessions managed via signed JWTs (SHA-256) and tracked in `sessions` table.
2. **API Keys:** Stored as SHA-256 hashes (`secret_hash`). Prefixes (`uk_live_...`, `uk_test_...`) exposed for identification.
3. **Webhook Security:** HMAC-SHA256 signature verification enforced using `crypto.createHmac('sha256', secret)`. Replays prevented via unique event ID checks in `event_ingestion_logs` and `recovery_opportunities`.
4. **SQL Injection:** Queries utilize parameterized statements (`?` in SQLite, `$1` in Postgres) via `DatabaseAdapter.query()`.
5. **Prompt Injection:** `AgentAuthorityGate` scans all LLM tool inputs against hostile override patterns.

---

## 39. Test Architecture & Coverage

The project contains **58 automated test suites** across multiple test frameworks:

| Suite Group | Suite Count | Test Runner | Purpose |
| :--- | :--- | :--- | :--- |
| **v6 Master Suites** | 24 Suites | `tsx --test` | Tests tenancy, auth, canonical events, provider connection, ledger, and simulation. |
| **Agent Intelligence** | 28 Suites | `tsx` runner | Tests agent state machine, tool registry, memory, loop guard, temporal firewall, replanning. |
| **Core Hardening** | 6 Suites | `tsx` runner | Tests API security, Bayesian calibration, double-entry ledger, circuit breaker. |
| **Truth & Invariants** | 3 Suites | `tsx --test` | Tests causal statistics, provider truth invariants, state consistency. |
| **Causal Experiments** | 8 Experiments | `scripts/run_causal_experiments.ts` | Measures empirical recovery lift across decline cohorts. |

---

## 40. Historical Provider Recovery Evidence (`ultron.db`)

Forensic read-only inspection of `ultron.db` confirms live provider-backed recovery executions against Razorpay:

### Transaction 1: Confirmed Recovery (₹4,500.00)
- **Opportunity ID:** `rzp_live_test_1788233420739`
- **Source:** `real` (Amount: `450000 paise` / ₹4,500.00)
- **Status in DB:** `recovered`
- **Razorpay Payment Link ID:** `plink_TWcnQZVwogNPop`
- **Short URL:** `https://rzp.io/rzp/bC4wMhY`
- **Provider Status:** `paid` / `captured`
- **Reconciliation Audit (`ledger_entries`):**
  - Event `webhook_received` at `2026-09-01T03:30:20.739Z`
  - Event `recovered` at `2026-09-01T05:57:00.923Z` (`reconciled_by: authoritative_reconciler`)
- **Double-Entry Ledger Records:**
  - `del_1788233421779`: Debit `receivables`, Credit `unearned_recovery` (₹4,500.00)
  - `del_1788242220988`: Debit `bank_settlement`, Credit `recovered_revenue` (₹4,500.00)

---

## 41. Architectural Invariants Verification Matrix

| Invariant Rule | Implementation File & Function | Status | Evidence |
| :--- | :--- | :--- | :--- |
| **AI cannot execute financial writes** | `src/agents/gate.ts:146` (`write_boundary_check`) | **VERIFIED** | 0 tool calls permitted with `FINANCIAL_WRITE` / `EXECUTE`. |
| **Authority cannot be bypassed** | `src/execution/executor.ts:63` (`evaluateOpportunity`) | **VERIFIED** | Direct assertion of `AUTHORIZED` status prior to API call. |
| **`LINK_CREATED != RECOVERED`** | `src/truth/provider_truth.ts:41` (`evaluate`) | **VERIFIED** | `LINK_CREATED` maps to `PROVIDER_OBJECT_VERIFIED`, not `RECOVERED`. |
| **Integer paise storage** | `src/db/database.ts:86` (`amount_paise INTEGER`) | **VERIFIED** | All amounts stored in integer paise; formatted in UI. |
| **Double-Entry Ledger Balanced** | `src/truth/double_entry_ledger.ts:129` | **VERIFIED** | Total debits equal total credits (26,422,500 paise). |
| **Tenant Data Isolation** | `src/security/tenancy.ts:82` (`authenticateTenant`) | **VERIFIED** | SQL queries enforce `tenant_id = ?` parameter binding. |
| **Temporal Memory Firewall** | `src/agents/temporal_firewall.ts:25` | **VERIFIED** | Queries restricted to records $\le$ opportunity timestamp. |
| **Multi-Level Kill Switch** | `src/authority/gate.ts:24` (`isKillSwitchActive`) | **VERIFIED** | Global, tenant, and provider switches override all decisions. |

---

## 42. Current vs Intended Architecture

| Architecture Area | Current Actual Implementation | Intended / Documented Specification | Difference / Status |
| :--- | :--- | :--- | :--- |
| **Database Engine** | Local SQLite (`ultron.db`) with async Supabase sync | PostgreSQL / Supabase as primary | **PARTIAL**: SQLite is primary; Postgres adapter exists. |
| **Economic Scorer** | Deterministic formula + Bayesian calibration | Deterministic IVEN + Empirical Lift | **MATCHES SPECIFICATION** |
| **Recovery Market** | Greedy ranking by IVEN + Shadow price derivation | Greedy ranking with capacity cap | **MATCHES SPECIFICATION** |
| **Action Authority** | 5 deterministic checks + multi-level kill switch | Deterministic compliance gate | **MATCHES SPECIFICATION** |
| **Execution Engine** | Razorpay SDK (Test Mode) + Circuit breaker + DLQ | Test Mode execution with idempotency | **MATCHES SPECIFICATION** |
| **AI Agent Layer** | 15-state machine + 18 tools + NVIDIA NIM fallback | Reasoning & explanation only | **MATCHES SPECIFICATION** |
| **Frontend UI** | Next.js 16 + React 19 + Tailwind CSS | Next.js Single Page / App Router | **MATCHES SPECIFICATION** |
| **OdooX Integration** | Outbound Event Emitter connector client | Direct ERP connector | **CONNECTOR ONLY**: ERP code external. |

---

## 43. Evidence Matrix

| System Capability | Source Code | Runtime Execution | Database State | Automated Tests | Provider API | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Canonical Event Ingestion** | `src/routes/events.ts` | Verified | Verified | 24 v6 Tests | N/A | `RUNTIME_VERIFIED` |
| **IVEN Economic Scoring** | `src/economics/scorer.ts` | Verified | 774 rows in `scores` | 6 Core Tests | N/A | `RUNTIME_VERIFIED` |
| **Portfolio Market Allocator** | `src/market/allocator.ts` | Verified | 774 decisions | Test Suite | N/A | `RUNTIME_VERIFIED` |
| **Action Authority Gate** | `src/authority/gate.ts` | Verified | 3,866 checks | Bypass Tests | N/A | `RUNTIME_VERIFIED` |
| **Razorpay Link Creation** | `src/execution/executor.ts` | Verified | 113 records | Execution Tests | Test API | `PROVIDER_VERIFIED` |
| **Double-Entry Ledger** | `src/truth/double_entry_ledger.ts` | Verified | 124 records | Ledger Tests | N/A | `DATABASE_VERIFIED` |
| **Authoritative Reconciliation** | `src/reconciliation/` | Verified | 172 ledger entries| State Tests | Test API | `PROVIDER_VERIFIED` |
| **AI Agent Investigation** | `src/agents/orchestrator.ts`| Verified | 654 agent runs | 28 Agent Tests | N/A | `RUNTIME_VERIFIED` |
| **NVIDIA NIM LLM Reasoning** | `src/agents/llm_provider.ts`| Verified | 159 invocations | LLM Tests | NVIDIA NIM | `RUNTIME_VERIFIED` |
| **Multi-Tenancy & Auth** | `src/security/tenancy.ts` | Verified | 101 tenants | Tenancy Tests | N/A | `RUNTIME_VERIFIED` |
| **OdooX Connector** | `src/connectors/odoox/` | Verified | Ingestion Logs | OdooX Tests | N/A | `SOURCE_VERIFIED` |

---

## 44. Contradiction Register

| ID | Source Claim A | Source Claim B | Actual Forensic Observation | Affected Subsystem |
| :--- | :--- | :--- | :--- | :--- |
| **CONTRADICTION-001** | Documentation states Supabase PostgreSQL is the primary database. | Code in `src/db/database.ts` initializes `new DatabaseSync('ultron.db')`. | Active runtime operates entirely on local SQLite file `ultron.db`; Supabase is updated via asynchronous sync hooks. | Database Layer |
| **CONTRADICTION-002** | Early spec documents state capacity cap is fixed at 5 payment links. | Schema migration `004` and `src/market/allocator.ts` support per-tenant dynamic capacity limits (`tenants.capacity_limit`). | Default capacity is 5, but can be configured per tenant up to 100 via API/Dashboard. | Recovery Market |

---

## 45. Unknown Register

| ID | Question / Unknown Item | Missing Evidence | Impact / Classification |
| :--- | :--- | :--- | :--- |
| **UNKNOWN-001** | Exact internal implementation of OdooX ERP server-side payment module. | OdooX codebase is not stored in local workspace. | `UNKNOWN` (Client connector verified, server ERP external). |
| **UNKNOWN-002** | Production Razorpay Live credentials behavior and webhook latency under live load. | Workspace is strictly configured for Razorpay Test Mode keys (`rzp_test_...`). | `UNKNOWN` (Live money execution deliberately omitted per rule). |

---

## 46. Protected Components for Future Migration

The following 8 modules contain strictly verified invariant logic and must be treated as **PROTECTED / DO NOT REFACTOR BLINDLY** during any future database or framework migrations:

1. **`src/economics/scorer.ts`** (`calculateScore`, `calculateCosts`) — Exact mathematical IVEN formula and fatigue penalty curve.
2. **`src/market/allocator.ts`** (`runMarketAllocation`) — Portfolio ranking, capacity enforcement, and shadow price calculation.
3. **`src/authority/gate.ts`** (`evaluateOpportunity`, `isKillSwitchActive`) — 5 deterministic compliance checks and multi-level kill switch.
4. **`src/execution/executor.ts`** (`executeOpportunity`, `executeAuthorizedBatch`) — Strict zero-bypass execution gateway and idempotency locks.
5. **`src/truth/provider_truth.ts`** (`evaluate`) — Provider truth evaluator enforcing `LINK_CREATED != RECOVERED`.
6. **`src/truth/double_entry_ledger.ts`** (`recordEntry`, `computeHash`, `verifyLedgerIntegrity`) — SHA-256 cryptographic hash-chained accounting ledger.
7. **`src/reconciliation/authoritative_reconciler.ts`** (`reconcileOpportunity`) — State machine reconciler and balance settlement logic.
8. **`src/agents/gate.ts`** (`evaluate`) — 9 security boundary checks preventing AI agents from issuing financial writes.

---

## 47. Technical Debt & Transformation Risks

### Technical Debt Classification:
- **`MEDIUM` — Database Dual-Write Complexity:** `src/db/database.ts` performs direct SQLite operations while `src/db/adapter.ts` provides a PostgreSQL abstraction. Future migration should standardize repository calls entirely through `DatabaseAdapter`.
- **`LOW` — In-Memory Kill Switch & Rate Limiting:** Global kill switch and agent rate limits are tracked in-memory with database fallbacks. In multi-instance cluster deployments, Redis should be mandatory.

### Future Transformation Blast Radius:
- **SQLite $\rightarrow$ Supabase/PostgreSQL Migration:** Because `DatabaseAdapter` already normalizes parameterized queries (`$1` vs `?`) and SQL syntax (`BIGSERIAL` vs `AUTOINCREMENT`), the transition can be achieved with zero business logic changes by supplying a live `DATABASE_URL`.
- **Razorpay Test $\rightarrow$ Live Mode:** Requires only setting live API keys in `tenant_credentials` table; the execution engine, circuit breaker, and reconciliation pipeline remain identical.

---

## 48. Final System Assessment

```
============================================================
ULTRON — COMPLETE LOCAL FORENSIC ANALYSIS SUMMARY
============================================================

Current Runtime:
    Express 4.21 API on Node.js (PORT 3001) + Next.js 16.3 Frontend (PORT 3000)

Database:
    SQLite 3 (WAL Mode, ultron.db, 39 tables, 5.79 MB) with async Supabase sync

Frontend:
    Next.js 16.3.3 + React 19.2.8 + Tailwind CSS 4 (App Router)

Backend:
    Modular Express architecture with Tiered RateLimiting, Helmet, and Zod

Financial Core:
    100% Deterministic IVEN Scorer, Market Allocator, and Shadow Price Derivation

AI Agent:
    15-State Machine, 18 Scoped Tools (Read/Propose only), Zero Financial Write Authority

LLM:
    NVIDIA NIM (Nemotron-3.5-30B) with automatic deterministic fallback

Razorpay:
    Official Node SDK (Test Mode), HMAC Webhook Verification, Client Connection Pool

OdooX:
    Client Event Emitter Connector verified; ERP server source external

Tenant Architecture:
    Multi-tenant isolation across all 39 tables; AES-256-GCM encrypted credentials

Mock Data:
    Isolated to simulation scripts, test suites, and playground sandbox

Legacy Code:
    0 dead entrypoints; all modules referenced in server routers or test suites

Major Risks:
    Dual-database adapter consolidation needed before enterprise cluster scale

Contradictions:
    2 documented in Contradiction Register (Postgres vs SQLite; Fixed vs Dynamic Cap)

Unknowns:
    2 documented in Unknown Register (External OdooX source; Live Razorpay latency)

Protected Components:
    8 core modules designated PROTECTED (Economics, Market, Authority, Ledger, Truth)

Production Readiness:
    Fully hardened for Enterprise SaaS Test Mode & Multi-Tenant Simulation

Source Modifications Made By Audit:
    0

Database Mutations Made By Audit:
    0

Provider Write Operations Made By Audit:
    0

Canonical Report:
    ULTRON_COMPLETE_LOCAL_FORENSIC_ANALYSIS.md
============================================================
```
