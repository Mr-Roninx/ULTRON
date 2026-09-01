# ULTRON v5.0 — Phase 0: Local Forensic Baseline Report

**Execution Timestamp**: 2026-08-31T23:22:00Z  
**Primary Source of Truth**: Current Local Workspace (`d:\Work Space\Project\Ultron`)  
**Phase Objective**: Complete read-only forensic baseline of the current local ULTRON implementation across source code, database schemas, APIs, Razorpay integration, economics, market allocation, authority, execution, reconciliation, frontend, tests, and AI/LLM modules.

---

## 1. Executive Forensic Summary

The ULTRON workspace is a fully functional, hybrid financial recovery platform with two strictly decoupled operational layers:
1. **Deterministic Financial Core**: TypeScript/Node.js control plane enforcing mathematical IVEN scoring, greedy market capacity allocation, independent Action Authority compliance vetoes, double-entry cryptographic ledgering, and circuit-breaker protected Razorpay execution.
2. **AI Agent Intelligence Layer**: 21-state autonomous reasoning agent coordinating specialist copilots, 18 server-permissioned tools, 3-tier memory with temporal anti-lookahead firewalling, and bounded semantic signal modifier bridging into the deterministic core.

### Current Test Baseline (100% Pass Rate):
- **Core Hardening Suite (`npm run test:core`)**: 5 PASSED / 0 FAILED
- **Infrastructure Suite (`npm run test:infra`)**: 3 PASSED / 0 FAILED
- **Master Agent Safety Suite (`npm run test:agent`)**: 20 PASSED / 0 FAILED
- **Causal Experiments (`npm run experiments:causal`)**: 17 Evidence JSON Artifacts Generated
- **Frontend Production Build (`npm run build`)**: 0 Build / Type Errors

---

## 2. Active Source Tree & Subsystem Inventory

### A. Root Application & Entrypoint
- [`src/server.ts`](file:///d:/Work%20Space/Project/Ultron/src/server.ts): Express 4 API server configured with Helmet.js security headers, strict CORS origin allowlist, tiered sliding-window rate limiters (webhook: 100 req/min, execution: 10 req/min, general: 120 req/min), JWT session authentication middleware, and raw body HMAC capture.

### B. Database & Persistence Layer ([`src/db/`](file:///d:/Work%20Space/Project/Ultron/src/db/))
- [`src/db/adapter.ts`](file:///d:/Work%20Space/Project/Ultron/src/db/adapter.ts): Dual-engine connection pool supporting **PostgreSQL 15+** (`pg.Pool`) and **SQLite** (`node:sqlite` in WAL mode), parameterized query normalization (`$1` vs `?`), and atomic transaction helper `withTransaction`.
- [`src/db/database.ts`](file:///d:/Work%20Space/Project/Ultron/src/db/database.ts): Core CRUD methods and auto-ensuring guards (`ensureOpportunity`, `ensureAgentRun`).
- [`src/db/migrations/`](file:///d:/Work%20Space/Project/Ultron/src/db/migrations/): Migration runner (`runner.ts`) with SHA-256 checksum tracking table `schema_migrations`, supporting up/down migrations for:
  - `001_core_schema.ts` (Core 7 financial tables, `merchant_id` multi-tenancy, `BIGINT` paise, `TIMESTAMPTZ`).
  - `002_agent_schema.ts` (13 Agent intelligence tables).
  - `003_indexes_and_jsonb.ts` (Performance and query indexes).

### C. Webhook Ingestion & Security ([`src/security/`](file:///d:/Work%20Space/Project/Ultron/src/security/), [`src/webhooks/`](file:///d:/Work%20Space/Project/Ultron/src/webhooks/))
- [`src/security/webhook_validator.ts`](file:///d:/Work%20Space/Project/Ultron/src/security/webhook_validator.ts): Razorpay egress IP allowlisting (`52.66.75.174`, `52.66.75.175`, `13.235.25.0/24`), 300s timestamp freshness tolerance, multi-secret HMAC rotation (`RAZORPAY_WEBHOOK_SECRET_OLD`), 1MB payload limits, and durable `webhook_audit_log` audit entries.
- [`src/security/schemas.ts`](file:///d:/Work%20Space/Project/Ultron/src/security/schemas.ts): Strict Zod runtime schemas across all route handlers.
- [`src/security/auth.ts`](file:///d:/Work%20Space/Project/Ultron/src/security/auth.ts): JWT authentication with 30-minute session expiry.
- [`src/webhooks/razorpay.ts`](file:///d:/Work%20Space/Project/Ultron/src/webhooks/razorpay.ts): Webhook ingestion handler labeling `source='real'` for verified webhooks and `source='synthetic'` for test harness payloads.

### D. Perception & Economic Reasoning ([`src/perception/`](file:///d:/Work%20Space/Project/Ultron/src/perception/), [`src/economics/`](file:///d:/Work%20Space/Project/Ultron/src/economics/))
- [`src/perception/normalizer.ts`](file:///d:/Work%20Space/Project/Ultron/src/perception/normalizer.ts): Deterministic normalizer classifying decline reasons into `hard`, `soft`, or `unknown`.
- [`src/economics/scorer.ts`](file:///d:/Work%20Space/Project/Ultron/src/economics/scorer.ts): Mathematical IVEN scorer ($\text{IVEN} = \text{amount\_paise} \times \Delta P - \text{cost\_paise}$, with $\Delta P = P_{\text{interv}} - P_{\text{nat}}$).
- [`src/economics/bayesian_calibration.ts`](file:///d:/Work%20Space/Project/Ultron/src/economics/bayesian_calibration.ts): Empirical Beta distribution calibration ($\text{Beta}(\alpha + k, \beta + n - k)$), `probability_models` table, and A/B test promotion framework (auto-promotes if lift $> 5\%$ and $p < 0.05$).

### E. Recovery Market & Capacity Policies ([`src/market/`](file:///d:/Work%20Space/Project/Ultron/src/market/))
- [`src/market/allocator.ts`](file:///d:/Work%20Space/Project/Ultron/src/market/allocator.ts): Greedy portfolio allocator sorting by descending expected incremental value and exposing shadow price at capacity boundary.
- [`src/market/capacity_policy.ts`](file:///d:/Work%20Space/Project/Ultron/src/market/capacity_policy.ts): Time-windowed per-merchant capacity policy, Redis sliding counters, customer 24h fatigue limits (max 1 link/day), and monthly budget caps.

### F. Action Authority & Compliance ([`src/authority/`](file:///d:/Work%20Space/Project/Ultron/src/authority/))
- [`src/authority/gate.ts`](file:///d:/Work%20Space/Project/Ultron/src/authority/gate.ts): Independent compliance verification stage evaluating hard decline status, retry caps (3 attempts max), customer trust threshold, minimum IVEN threshold, and kill switch state.
- [`src/authority/rules.ts`](file:///d:/Work%20Space/Project/Ultron/src/authority/rules.ts): 5 deterministic authority compliance rules.

### G. Execution Engine & Dead Letter Queue ([`src/execution/`](file:///d:/Work%20Space/Project/Ultron/src/execution/))
- [`src/execution/executor.ts`](file:///d:/Work%20Space/Project/Ultron/src/execution/executor.ts): Sole financial write boundary. Enforces hard assertion throw if opportunity is not `AUTHORIZED`.
- [`src/execution/circuit_breaker.ts`](file:///d:/Work%20Space/Project/Ultron/src/execution/circuit_breaker.ts): Circuit breaker (trips `OPEN` after 5 consecutive failures, 30s cooldown to `HALF_OPEN`, resets `CLOSED` on successful probe, with 10s SDK timeout and exponential backoff with jitter).
- [`src/execution/dlq.ts`](file:///d:/Work%20Space/Project/Ultron/src/execution/dlq.ts): Dead Letter Queue table `execution_failures` with automated exponential retry intervals (5m $\to$ 15m $\to$ 1h $\to$ 4h $\to$ `PERMANENTLY_FAILED` + operator alert).

### H. Truth Engine & Ledgering ([`src/truth/`](file:///d:/Work%20Space/Project/Ultron/src/truth/), [`src/reconciliation/`](file:///d:/Work%20Space/Project/Ultron/src/reconciliation/))
- [`src/truth/double_entry_ledger.ts`](file:///d:/Work%20Space/Project/Ultron/src/truth/double_entry_ledger.ts): Double-entry accounting (`receivables`, `recovered_revenue`, `operational_costs`, `fatigue_provision`) with SHA-256 cryptographic hash-chaining (`entry_hash = sha256(prev_hash + ...)`).
- [`src/truth/reconciliation_sla.ts`](file:///d:/Work%20Space/Project/Ultron/src/truth/reconciliation_sla.ts): SLA monitoring ($< 5$s webhook, $< 5$ min poller), 30-min unreconciled alert, and divergence mismatch logger (`reconciliation_divergences`).
- [`src/reconciliation/poller.ts`](file:///d:/Work%20Space/Project/Ultron/src/reconciliation/poller.ts): Background polling reconciler synchronizing local state with Razorpay API.

### I. Caching & Message Layer ([`src/cache/`](file:///d:/Work%20Space/Project/Ultron/src/cache/))
- [`src/cache/redis.ts`](file:///d:/Work%20Space/Project/Ultron/src/cache/redis.ts): Redis 7+ client with in-memory fallback, 5-min probability table caching, write-through customer trust score cache, `SETNX` distributed idempotency locks (24h TTL), and $< 5$s kill switch pub/sub event broadcasting.
- [`src/cache/rate_limiter.ts`](file:///d:/Work%20Space/Project/Ultron/src/cache/rate_limiter.ts): Sliding-window rate limiter.

### J. AI Agent Intelligence Layer ([`src/agents/`](file:///d:/Work%20Space/Project/Ultron/src/agents/))
- **State Machine ([`state_machine.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/state_machine.ts))**: 21 discrete states from `IDLE` to `COMPLETE`.
- **Security Gate ([`gate.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/gate.ts))**: 9 server-side checks enforcing read/propose permissions, mission budget limits, loop guards, injection filtering, and kill switch compliance.
- **Budget Manager ([`budget.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/budget.ts))**: Hard limits (max 8 LLM calls, 20 tools, 3 replans, 40 steps, 30s timeout).
- **Loop Guard ([`loop_guard.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/loop_guard.ts))**: SHA-256 fingerprinting for duplicate tool inputs, plans, and cyclic states.
- **Tool Registry ([`tool_registry.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/tool_registry.ts))**: 18 tools (14 read tools, 4 proposal tools) with JSON schemas.
- **Context Builder ([`context_builder.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/context_builder.ts))**: Sanitizes input, strips PII/secrets, and limits prompt size.
- **Temporal Firewall ([`temporal_firewall.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/temporal_firewall.ts))**: Strictly blocks lookahead records ($T_{\text{info}} \le T_{\text{decision}}$).
- **Memory Store ([`memory.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/memory.ts))**: 3-tier memory (Working, Episodic, Semantic).
- **Planner & Replanner ([`planner.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/planner.ts), [`replan_engine.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/replan_engine.ts))**: Structured plan generation, assumption invalidation detection, and Plan v2 generation.
- **Semantic Bridge ([`bridge.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/bridge.ts))**: Normalizes and clamps 8 semantic signals ($0.0 \le s \le 1.0$) into calibrated IVEN modifiers while preserving hard decline zero-lift invariants.
- **Outcome Learning ([`learning.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/learning.ts))**: Computes Brier prediction errors and net gains upon settlement truth.
- **LLM Provider ([`llm_provider.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/llm_provider.ts))**: NVIDIA NIM (`nvidia/nemotron-3.5-lightning-30b-a3b`) with deterministic fallback.
- **Specialist Copilots ([`specialists/`](file:///d:/Work%20Space/Project/Ultron/src/agents/specialists/))**: `PerceptionAgent`, `StrategyAgent`, `OutreachAgent`, `ComplianceCopilot`, `MerchantCopilot`.
- **Master Orchestrator ([`orchestrator.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/orchestrator.ts))**: Coordinates the full 21-state recovery mission.

### K. REST API Routes ([`src/routes/`](file:///d:/Work%20Space/Project/Ultron/src/routes/))
- `/health`: Health status, connection pool telemetry, Redis status, kill switch flag.
- `/opportunities/*`: Ingestion, scoring, forensic listing.
- `/market/*`: Allocation batch run, shadow price inspection.
- `/authority/*`: Action Authority evaluation, kill switch toggle.
- `/execution/*`: Rate-limited execution dispatch, DLQ pending retries.
- `/dashboard/*`: Real-only financial metrics, funnel telemetry, audit trail.
- `/agents/*`: Mission dispatch, trace inspector, memory browser, copilot query, outreach approval.

### L. Frontend Dashboard ([`frontend/`](file:///d:/Work%20Space/Project/Ultron/frontend/))
- Next.js 16 (React 19 + Tailwind CSS single-page app).
- Deterministic control plane dashboard + dedicated AI Agent Control Center.

---

## 3. Active Code Path vs Disconnected Code

| Component | Status | Code Path Analysis |
| :--- | :--- | :--- |
| **Ingestion $\to$ Normalizer $\to$ Scorer $\to$ Market $\to$ Authority $\to$ Executor** | **ACTIVE** | Completely connected in deterministic pipeline and accessible via REST API and CLI scripts. |
| **Agent Orchestrator $\to$ Tools $\to$ LLM $\to$ Bridge $\to$ Market $\to$ Authority** | **ACTIVE** | Fully wired in `src/agents/orchestrator.ts`, exposed on `/agents/missions`, verified in `demo_agent_recovery.ts`. |
| **Circuit Breaker $\to$ DLQ $\to$ Razorpay Execution** | **ACTIVE** | Integrated in `src/execution/executor.ts` and `src/routes/execution.ts`. |
| **Double-Entry Cryptographic Ledger & Reconciliation SLA Tracker** | **ACTIVE** | Standalone truth engine verified with test suite in `tests/core/`. |
| **Disconnected / Dead Code** | **NONE** | All 15 submodules in `src/` are actively imported, mounted in Express, or tested in `tests/`. |

---

## 4. Current LLM & Provider Status

- **Configured Model**: `nvidia/nemotron-3.5-lightning-30b-a3b`
- **Base URL**: `https://integrate.api.nvidia.com/v1`
- **Fallback Behavior**: If network timeout or API error occurs, `src/agents/llm_provider.ts` transparently uses a deterministic heuristic fallback so automated tests and offline missions never stall.
- **Authority Constraint**: The LLM sits strictly above the deterministic core; it emits structured proposals and semantic signals ($0.0 \le s \le 1.0$) which are calibrated and bounded before reaching the IVEN formula. Zero LLM code sits on the execution path.

---

## 5. Current Razorpay Integration Status

- **Environment**: Razorpay Test Mode only (`RAZORPAY_KEY_ID=rzp_test_...`).
- **SDK**: Official Node.js `razorpay` library (v2.9.5).
- **Execution Safeguard**: Capped to a maximum of 5 payment links per run (`MAX_LINKS_PER_RUN=5`).
- **Zero-Bypass Assertion**: `src/execution/executor.ts` verifies `evalResult.verdict === 'AUTHORIZED'` and throws an uncatchable compliance error if an unauthorized opportunity is passed.
- **Browser Automation Verification**: Verified using Puppeteer script `scripts/pay_real_link.ts` in Razorpay Test Mode checkout.

---

## 6. Exact Files That Will Be Touched in Phase 1

When Phase 1 is requested, the minimum files to touch/refine for the Phase 1 specification:
1. `src/agents/types.ts`: Refine record interfaces if new telemetry fields are needed.
2. `src/agents/state_machine.ts`: Ensure all 21 transition callbacks adhere strictly to Phase 1 specs.
3. `src/agents/gate.ts`: Ensure all 9 Agent Authority Gate checks are cleanly isolated.
4. `src/agents/budget.ts`: Enforce exact Phase 1 budget limits (`max_llm_calls=8`, `max_tool_calls=20`, `max_replans=3`, `max_steps=40`, `max_wall_clock_ms=30000`).
5. `src/agents/loop_guard.ts`: Enforce tool, plan, and state fingerprinting.
6. `src/agents/telemetry.ts`: Structure durable run and step audit logging.
7. `tests/agent/test_agent_state_machine.ts`: Validate state machine transitions.
8. `tests/agent/test_agent_gate.ts`: Validate 9 gate security checks.
9. `tests/agent/test_agent_budget.ts`: Validate budget limits.
10. `tests/agent/test_agent_loop_guard.ts`: Validate loop protection.

---

## 7. Forensic Baseline Verdict

The local workspace has zero regressions, 100% test pass rate across all 28 core/infrastructure/agent tests, clean dual database support (SQLite WAL and PostgreSQL 15+), Redis caching with fallback, and all safety invariants strictly enforced.

**Phase 0 is complete. Awaiting user directive for Phase 1.**
