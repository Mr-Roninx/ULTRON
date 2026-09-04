# ULTRON — Complete Architecture & Working Analysis

## 1. Executive Summary
ULTRON is an autonomous economic control plane for failed-payment recovery. It prioritizes recovery actions deterministically based on marginal economics, allocating a scarce portfolio budget of payment links across opportunities. An AI context layer (LLM) enriches diagnosis, but zero LLM outputs are directly executed without passing through deterministic gates.

## 2. What ULTRON Actually Is Today
ULTRON today is a Node.js/Express backend accompanied by a Next.js frontend dashboard. It actively uses a local SQLite database with WAL mode (transparently falling back from Supabase if unreachable). It integrates exclusively with Razorpay (Test Mode) using the Razorpay Node SDK. 

## 3. Repository Structure
- `src/`: Backend API, Agents, Economics, Market, Authority, Execution, and Reconciliation logic.
- `frontend/`: Next.js 13+ React application for the merchant dashboard.
- `scripts/`: Assorted TSX scripts for testing, simulating webhooks, and seeding data.
- `tests/`: Granular unit/integration test suites.

## 4. Runtime Entry Points
- **Backend API**: `src/server.ts` (Express Server)
- **Frontend App**: `frontend/src/app/layout.tsx` (Next.js App Router)
- **Webhooks**: POST `/webhooks/razorpay/:tenant_id`
- **Simulations**: POST `/internal/simulate-webhook/:tenant_id`

## 5. Technology Stack
- **Backend**: Node.js, Express.js, TypeScript.
- **Frontend**: Next.js, React, Tailwind CSS.
- **Database**: Dual-engine (`pg` for Supabase, `node:sqlite` for local/fallback).
- **LLM**: NVIDIA NIM (`nvidia/nemotron-3.5-lightning-30b-a3b`).
- **Provider**: Razorpay.

## 6. Dependency Graph
Merchant/Frontend → API Router (Express) → Security/Auth Middleware → Agent (Context) → Deterministic Economics (Scorer) → Recovery Market (Allocator) → Action Authority (Gate) → Executor (Razorpay SDK) → Provider Truth (Reconciliation) → Double-Entry Ledger → SQLite DB.

## 7. Backend Architecture
The backend uses a standard middleware pipeline (Helmet, CORS, Rate Limiting, JWT/API Key Auth). Requests are routed to specialized domains (`/opportunities`, `/market`, `/authority`, `/execution`, `/dashboard`, `/agents`).
*Evidence*: `src/server.ts`

## 8. API Inventory
- `GET /health`
- `POST /v1/auth/signup` and `/v1/auth/login`
- `POST /webhooks/razorpay/:tenant_id`
- `POST /internal/simulate-webhook/:tenant_id`
- `GET /dashboard/summary`
- `POST /market/run`
- `POST /authority/run`
- `POST /execution/run`
- `GET /opportunities`

## 9. Database Architecture
Currently active runtime is **SQLite** (file `ultron.db` in root). The `DatabaseAdapter` (`src/db/adapter.ts`) attempts to initialize a PostgreSQL pool using `SUPABASE_DATABASE_URL`, but gracefully falls back to `sqlite:///ultron.db` upon failure. Both engines share a unified SQL translation layer for parameterized queries.

## 10. Complete Data Model
- `recovery_opportunities`: Core state machine for payment lifecycle.
- `scores`: Stores IVEN and incremental probabilities.
- `allocation_decisions`: Market batch ranks and shadow prices.
- `authority_checks`: 5 compliance checks per execution.
- `execution_records`: Idempotency and provider link storage.
- `double_entry_ledger`: Immutably logs financial recovery events.
- `tenants`, `users`, `api_keys`: Multi-tenancy and RBAC.

## 11. Deterministic Financial Core
The core does not use LLMs for math. It scores opportunities, ranks them, and allocates capacity.
*Evidence*: `src/economics/scorer.ts`

## 12. IVEN
**Formula**: `IVEN = (incremental_prob * amount_paise) - operational_cost - fatigue_cost`
Probabilities are drawn from hand-coded baseline assumptions based on reason codes.
*Evidence*: `src/economics/scorer.ts`

## 13. Recovery Market
A greedy allocator. Sorts eligible (Confidence `!low` AND `IVEN > 0`) opportunities by IVEN descending. Assigns `ACT` up to `capacity`, else `WAIT`. Records the `shadow_price_paise`.
*Evidence*: `src/market/allocator.ts`

## 14. Action Authority
5 strict deterministic gates evaluated in `src/authority/gate.ts`:
1. Hard Decline Check
2. Retry Cap Check
3. Kill Switch Check
4. Confidence Recheck
5. Capacity Recheck
Any failure results in `BLOCKED`, `ABSTAIN`, or `WAIT`.

## 15. Execution Engine
Executes ONLY if verdict is `AUTHORIZED`. Leverages `CircuitBreaker` and records `idempotency_key` locally before calling Razorpay API.
*Evidence*: `src/execution/executor.ts`

## 16. Razorpay Integration
Utilizes official `razorpay` npm package. Creates Payment Links (`rzpClient.paymentLink.create`). Handled cleanly through tenant-specific `RazorpayClientPool`.
*Evidence*: `src/execution/executor.ts`

## 17. Provider Truth
The source of truth is ALWAYS Razorpay. Handled by `ProviderTruthEvaluator.evaluate(providerPayload)` which normalizes states.
*Evidence*: `src/truth/provider_truth.ts`

## 18. Reconciliation
Atomic SQLite transactions apply provider truth to `recovery_opportunities` and `execution_records`. Out-of-order events are ignored if already terminal (`recovered`).
*Evidence*: `src/reconciliation/authoritative_reconciler.ts`

## 19. Double-Entry Ledger
Implemented in `src/truth/double_entry_ledger.ts`. Records entries (e.g., Debit `bank_settlement`, Credit `recovered_revenue`). Uses a cryptographic SHA-256 hash chain (`prev_hash`, `entry_hash`) for immutability.

## 20. AI Agent Architecture
Orchestrator manages the mission lifecycle. It delegates semantic signal synthesis to the `LLMProvider`, which then feeds the `SemanticEconomicsBridge`.
*Evidence*: `src/agents/orchestrator.ts`

## 21. Agent State Machine
States: IDLE → OBSERVE → INVESTIGATE → DIAGNOSE → HYPOTHESIZE → PLAN → VALIDATE_PLAN → PROPOSE → WAIT_AUTHORITY → EXECUTE → OBSERVE_OUTCOME → LEARN → MEMORY_UPDATE → COMPLETE.

## 22. Agent Orchestrator
Creates an `AgentRunRecord`, routes through Perception Agent, Context Builder, LLM Intent, Planner, Economic Bridge, Market Allocator, and Authority Gate.
*Evidence*: `src/agents/orchestrator.ts`

## 23. Agent Tools
Currently mapped as conceptual capabilities requested by LLM Intent JSON (e.g., `get_gateway_state`). Execution is strictly deterministic via Orchestrator.

## 24. LLM Architecture
**Provider**: NVIDIA NIM API (`nvidia/nemotron-3.5-lightning-30b-a3b`).
If missing keys or disabled, falls back to local `generateDeterministicFallbackIntent`.
*Evidence*: `src/agents/llm_provider.ts`

## 25. Memory
Uses `AgentMemoryStore` (SQLite `agent_memories` table). Records `episodic` memory for Learning feedback loops.

## 26. Planning
Handled by `AgentPlanner.createPlan`. Checks basic validity assumptions (e.g., gateway_health).

## 27. Replanning
LoopGuard is designed, but complex replanning is largely Code_Only for now.

## 28. Uncertainty
Confidence is explicitly bounded: `LOW`, `MEDIUM`, `HIGH`. `LOW` confidence forces `ABSTAIN` in the Authority Gate.

## 29. EVOI
Mentioned in types, but essentially Code_Only for active execution logic today.

## 30. Portfolio Intelligence
`PortfolioAgent.sweep()` analyzes opportunities and proposes rankings, but hands final execution to the deterministic Market Allocator.

## 31. Concurrency
`MissionConcurrencyCoordinator` handles batch parallel execution (Code_Only / scripts usage mostly).

## 32. Replay
`WebhookQueueEngine` handles redelivery and DLQ operations for failed webhook attempts.
*Evidence*: `src/webhooks/queue.ts`

## 33. Learning
`AgentLearningEngine` computes Brier Score prediction errors based on actual reconciliation outcomes.

## 34. Merchant Platform
Next.js App Router containing full Authentication, Settings, Team, Audit, and Execution views.
*Evidence*: `frontend/src/app/*`

## 35. Multi-Tenancy
Fully implemented via `tenant_id` filtering. JWT and API Keys map explicitly to specific `tenant_id` scopes in Express middleware.
*Evidence*: `src/security/auth.ts`

## 36. API Keys
Format: `ul_live_*` or `ul_test_*`. Secured using `bcrypt` hash in the database.

## 37. Frontend
Verified structure. Next.js server-side rendered application.

## 38. OdooX Integration
Exists as a fire-and-forget REST connector (`OdooXEventEmitter`) sending payloads to `/v1/events`. Zero local Odoo infrastructure present.
*Evidence*: `src/connectors/odoox/odoox_event_emitter.ts`

## 39. Complete Event Flow
Webhook (Razorpay) → Webhook Queue → Reconciler → Database (opp/exec records) → Double-Entry Ledger → Notification/Audit.

## 40. Complete End-to-End Payment Recovery Flow
Failed Payment Webhook → `recovery_opportunities` (pending) → Agent Orchestrator → LLM context enrichment → Deterministic Scorer → Market Allocator (`ACT`) → Authority Gate (`AUTHORIZED`) → Executor (Razorpay Payment Link) → Executing status.

## 41. Failure Handling
- **LLM down**: Deterministic Rule-Engine Fallback (VERIFIED).
- **DB down**: Graceful fallback to local SQLite (VERIFIED).
- **Razorpay Error**: Quarantine / Dead Letter Queue (VERIFIED).
- **Kill Switch**: Immediate halt in Orchestrator/Gate (VERIFIED).

## 42. Security Architecture
Helmet & CORS enabled. API keys are hashed. Webhook signatures validated.

## 43. Environment Configuration
Uses `.env` containing keys for Supabase, Razorpay, NVIDIA, Resend, etc. (Verified from `.env.example`).

## 44. Test Architecture
Rich suite of Node scripts (`tsx scripts/test_*`) covering truth consistency, causality, agent isolation, and core market mechanics.

## 45. Documentation vs Implementation
- **Supabase**: Documented as primary DB; Implemented but frequently falls back to SQLite runtime.
- **CP-SAT Solver**: Documented in past phases, completely removed/replaced with Greedy Allocator.

## 46. Mock / Synthetic Data
Used extensively in `scripts/seed_synthetic.ts` and `scripts/test_*` but explicitly isolated via `source = 'synthetic'` columns in SQLite.

## 47. Legacy Code
None explicitly detected; heavily refactored recently.

## 48. External Services
- **Razorpay**: Node SDK.
- **NVIDIA NIM**: REST fetch API.

## 49. Architectural Invariants
1. AI cannot execute writes (VERIFIED).
2. Authority Gate cannot be bypassed (VERIFIED).
3. Provider Truth dominates (VERIFIED).
4. Ledger Hash Chain (VERIFIED).

## 50. Evidence & Confidence
Almost entirely VERIFIED by source code and local runtime inspection.

## 51. Technical Debt
- Silent fallback from PostgreSQL to SQLite can mask connection errors in production.
- Prompt construction is heavy and could incur large token usage.

## 52. Production Readiness Gap
System uses Razorpay Test Mode exclusively. Live Money execution is strictly disabled. Real production deployment requires dedicated PostgreSQL (no SQLite fallback for Enterprise scale).

## 53. What Is Actually Working
- Database layer (SQLite)
- Express API server
- Scorer & Market Allocator
- Authority Gate
- Razorpay API Test Mode
- Reconciler & Ledger Hash Chain

## 54. What Is Partially Working
- Supabase PostgreSQL (Config-dependent)

## 55. What Is Not Verified
- Resend / Email delivery (External service untested)

## 56. Unknowns
- Exact Next.js frontend build success without full `npm run build` verification.

## 57. Final Architecture Diagram
```text
Merchant → API → Auth/Tenant Firewall → [Agent Orchestrator]
                                              ↓
                                        [Deterministic Scorer]
                                              ↓
                                      [Recovery Market Allocator]
                                              ↓
                                      [Action Authority Gate]
                                              ↓
                                           [Executor]
                                              ↓
                                          (Razorpay)
                                              ↓
                                        [Provider Truth]
                                              ↓
                                   [Authoritative Reconciler]
                                              ↓
                                      [Double-Entry Ledger]
```

## 58. Final Verdict
ULTRON CURRENTLY CONSISTS OF a deterministic financial control plane wrapping an AI context engine, operating against Razorpay in test mode, using a local SQLite database that seamlessly intercepts Supabase failures, served by a Next.js frontend.
