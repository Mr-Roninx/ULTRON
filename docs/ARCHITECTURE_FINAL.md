# ULTRON v3.2 — ARCHITECTURE FINAL

**Document Type:** Architecture-Readiness Review  
**Specification Source:** [ULTRON_MASTER_SPEC.md](file:///d:/Work%20Space/Project/Ultron/docs/ULTRON_MASTER_SPEC.md)  
**Review Date:** 2026-08-28  
**Repository Root:** `d:\Work Space\Project\Ultron`

---

## 1. EXECUTIVE SUMMARY

The current repository contains a **hackathon-stage prototype** that demonstrates several concepts from the ULTRON v3.2 specification but fails to meet the specification's requirements in **critical areas**. The codebase has hardcoded demo paths, missing subsystems, broken references, and architectural contradictions that must be resolved before production implementation.

**Overall readiness: ~25%** — foundational skeletons exist, but every subsystem requires rework or replacement.

---

## 2. CURRENT REPOSITORY STATE

### 2.1 Directory Structure (Actual)

```text
Ultron/
├── backend/
│   ├── agent/          # Agent runtime, tools, state, execution, LLM adapters
│   ├── api/            # FastAPI routers (agent, chaos, audit, customers, websocket)
│   ├── audit/          # Supabase-dependent audit engine
│   ├── baselines/      # Fixed workflow stub
│   ├── demo/           # Golden scenario script
│   ├── metrics/        # Metrics engine (Supabase-dependent)
│   ├── missions/       # Mission models, audit, metrics (duplicate)
│   ├── main.py         # Backend FastAPI entry point (Vite frontend)
│   └── simulator_api.py # Broken simulator API (references non-existent methods)
├── database/
│   ├── client.py       # Supabase client (external dependency)
│   └── schema.sql      # Supabase schema (external dependency)
├── docs/
│   ├── ULTRON_MASTER_SPEC.md
│   └── Ultron_v3.txt
├── financial/          # FSM, authority, policy, risk, feasible actions, reconciliation, idempotency
├── frontend/           # Vite + React app (basic shell)
├── intelligence/       # LLM (deterministic mock), interference engine
├── memory/             # Episodic memory (stub)
├── simulator/          # World, clock, models, seed, chaos, event bus, customer state
├── static/             # Legacy static HTML/CSS/JS demo
├── tests/              # 12 test files
├── main.py             # Root FastAPI entry point (static demo)
├── requirements.txt    # Minimal Python deps
├── check_size.py
├── download_qwen.py
├── qwen_test.py
└── task.md             # Phase tracker (all marked complete — inaccurate)
```

### 2.2 Specification Target Structure (Required by Spec §8, §45)

```text
Ultron/
├── backend/
│   ├── llm/            # §8: base.py, huggingface.py, local_qwen.py, router.py, schemas.py
│   ├── agent/          # §18: Agent state machine with 13 states
│   ├── tools/          # §20-21: Investigation, Decision, Execution tools
│   ├── economics/      # §23: NetExpectedValue engine
│   ├── episodes/       # §16: Revenue Episode aggregator
│   ├── api/            # §34: FastAPI mission API
│   └── config/         # §9: Environment-driven configuration
├── financial/          # §11-12: FSM, failure intelligence, reconciliation
├── simulator/          # §13-15, §31: World model, virtual clock, chaos engine
├── evaluator/          # §28-29: Counterfactual engine (ISOLATED)
├── intelligence/       # §27: Interference engine
├── memory/             # §26: Episodic memory
├── frontend/           # §34: Next.js + React + Tailwind Command Center
├── tests/              # §38-42: Unit, integration, scenario, adversarial
├── .agents/rules/      # §45: Antigravity workspace rules
└── .agents/workflows/  # §46: Antigravity workflows
```

---

## 3. MISSING PROJECT STRUCTURE

| Required (Spec) | Status | Gap |
|---|---|---|
| `backend/llm/` (§8) | ❌ MISSING | No LLM provider abstraction. Two incompatible LLM files exist: `intelligence/llm.py` (deterministic mock) and `backend/agent/llm.py` (OpenAI-specific) |
| `backend/llm/base.py` | ❌ MISSING | No `LLMProvider` ABC with `generate()`, `structured()`, `health()` |
| `backend/llm/huggingface.py` | ❌ MISSING | No HuggingFace Inference Provider integration |
| `backend/llm/local_qwen.py` | ❌ MISSING | No local Qwen3-4B provider behind OpenAI-compatible interface |
| `backend/llm/router.py` | ❌ MISSING | No auto-routing with fallback + fallback logging |
| `backend/llm/schemas.py` | ❌ MISSING | No structured output schemas |
| `evaluator/` (§28-29) | ❌ MISSING | **Counterfactual engine does not exist.** This is the spec's single most critical subsystem. |
| `backend/economics/` (§23) | ❌ MISSING | No NetExpectedValue calculation. No economic engine. |
| `backend/episodes/` (§16) | ❌ MISSING | No Revenue Episode aggregator |
| `.agents/rules/` (§45) | ❌ MISSING | No Antigravity workspace rules |
| `.agents/workflows/` (§46) | ❌ MISSING | No Antigravity workflows |
| `.env` / config system (§9) | ❌ MISSING | No environment configuration for LLM providers |
| `backend/tools/` (§20-21) | ⚠️ PARTIAL | Tools exist at `backend/agent/tools.py` but only 3 of 14 specified tools are implemented |
| Gateway entity (§13) | ❌ MISSING | No Gateway model in world |
| RecoveryAction entity (§13) | ❌ MISSING | No RecoveryAction model |
| Communication entity (§13) | ❌ MISSING | No Communication model |
| Event entity (§13-14) | ⚠️ PARTIAL | Events exist in event bus but not as proper domain entities |
| Data generation script (§36-37) | ⚠️ PARTIAL | Only one hardcoded seed scenario. No seeded generation of 200 customers / 2000 payments |

---

## 4. MISSING SPECIFICATIONS

| Spec Section | Requirement | Status |
|---|---|---|
| §12 Failure Intelligence | `FailureNormalizer`, `FailureClassifier`, `RetryabilityResolver`, `ReconciliationResolver` | ❌ None exist |
| §12 Failure Classifications | 7 failure categories (TRANSIENT, CUSTOMER_ACTION_REQUIRED, etc.) | ❌ Not implemented |
| §14 Event Model | Unified domain event model from state transitions | ⚠️ Events exist but are ad-hoc strings, not typed domain events |
| §15 Virtual Clock | `schedule()`, `cancel()`, `next_event()`, `run_until()` | ❌ Only `advance()` and `get_time()` exist |
| §16 Revenue Episode | Holistic customer revenue aggregation | ❌ Not implemented |
| §17 Agent Mission | 10 required fields (observations, hypotheses, plans, prediction_errors, replans, etc.) | ⚠️ Only `mission_id`, `goal`, `deadline`, `constraints`, `authority`, `status`, `recovered_amount` exist |
| §19 Bounded Agent Loop | `MAX_STEPS=12`, `MAX_REPLANS=5`, `MAX_IDENTICAL_FAILURES=2` | ⚠️ Circuit breaker exists but uses MAX_ITERATIONS=5 and MAX_REPLANS=2 (spec says 12 and 5) |
| §20 Investigation Tools | 8 tools specified | ⚠️ Only 3 implemented |
| §20 Decision Tools | `get_feasible_actions`, `calculate_action_value` | ⚠️ `get_feasible_actions` exists; `calculate_action_value` does not |
| §20 Execution Tools | 6 tools specified | ⚠️ Only generic `execute_action` exists; no individual tool implementations |
| §24 Recovery Strategy | 9 action types (WAIT, RECONCILE, RETRY, etc.) | ⚠️ Only 4 actions exist |
| §25 Relationship State | Observable signals (recent_contacts, complaints, opt_out, etc.) | ❌ Not implemented |
| §30 Prediction Error | Prediction-vs-reality comparison with REPLAN trigger | ⚠️ `ObservationEngine` exists but not integrated into runtime properly |
| §33 Audit Ledger | Hash-chained tamper-evident audit trail | ❌ Audit exists but has no hash chaining |
| §35 Agent Trace | Timestamped agent decision trace for UI | ⚠️ Audit logs exist but are not formatted as spec-compliant agent traces |

---

## 5. ARCHITECTURAL CONTRADICTIONS

### 5.1 CRITICAL: LLM is Hardcoded Demo Script

**Spec (§7):** "The LLM may investigate, interpret evidence, classify ambiguous information, form hypotheses, choose between deterministic candidate strategies."

**Reality:** `intelligence/llm.py` is a `DeterministicLLM` that returns hardcoded responses based on `call_count`. This is explicitly what the spec calls ❌ *"hardcoded demo"* (§3).

### 5.2 CRITICAL: No Trust Boundary Enforcement

**Spec (§6):** LLM → Structured Intent → Pydantic → Feasibility → Authority → Risk → FSM → Executor → World.

**Reality:** The runtime calls `llm.generate_plan()` which returns a raw dict. There is no Pydantic validation of LLM output. The LLM output goes directly into the executor.

### 5.3 CRITICAL: Database Architecture Contradiction

**Spec (§16):** "SQLite initially; PostgreSQL-ready architecture."

**Reality:** `database/client.py` uses **Supabase** (external cloud service), and `database/schema.sql` references Supabase-specific types (JSONB). The database layer requires credentials that don't exist. Meanwhile, the actual runtime uses in-memory Python dicts exclusively — the database layer is dead code.

### 5.4 CRITICAL: Dual Main Entry Points

`main.py` (root) and `backend/main.py` are two separate FastAPI applications with different routes, different state management, and incompatible architectures.

### 5.5 CRITICAL: Agent States Mismatch

**Spec (§18):** 13 states: OBSERVE, INVESTIGATE, HYPOTHESIZE, PLAN, FEASIBILITY_CHECK, AUTHORITY_CHECK, RISK_CHECK, EXECUTE, WAIT, EVALUATE, LEARN, REPLAN, ESCALATE, COMPLETE.

**Reality:** `backend/agent/state.py` has 11 states: IDLE, INVESTIGATING, PLANNING, VALIDATING, EXECUTING, OBSERVING, LEARNING, REPLANNING, ESCALATED, COMPLETED, STOPPED. Missing: OBSERVE, HYPOTHESIZE, FEASIBILITY_CHECK, AUTHORITY_CHECK, RISK_CHECK, WAIT, EVALUATE.

### 5.6 CRITICAL: FSM Missing States

**Spec (§11):** Payment states: CREATED, INITIATED, AUTHORIZING, AUTHORIZED, CAPTURED, SETTLED, FAILED, UNKNOWN, RECONCILING, REVERSED, REFUNDED.

**Reality:** `simulator/models.py` has: CREATED, AUTHORIZED, CAPTURED, SETTLED, FAILED, UNKNOWN, REVERSED. Missing: **INITIATED, AUTHORIZING, RECONCILING, REFUNDED**.

### 5.7 CRITICAL: Counterfactual Contamination Risk

**Spec (§29):** "Never expose baseline_outcome, treatment_outcome, incremental_recovery to ULTRON before it acts."

**Reality:** No counterfactual engine exists at all.

### 5.8 Reconciliation References Non-Existent Symbols

`financial/reconciliation.py` imports `FinancialFSM` from `financial.fsm`, but the actual class is named `PaymentFSM`. It also calls `world.update_payment()` which does not exist — the method is `world.update_payment_status()`. **Broken at import time.**

### 5.9 Simulator API References Non-Existent Methods

`backend/simulator_api.py` calls `clock.tick()`, `world.subscriptions`, and `world.create_payment()` — none of which exist. **Broken at import time.**

### 5.10 Duplicate Audit Systems

Three separate audit implementations exist with incompatible interfaces.

### 5.11 Duplicate Metrics Systems

Two metrics implementations exist — one in-memory, one Supabase-dependent.

### 5.12 Frontend Technology Mismatch

**Spec (§34):** "Next.js + React + Tailwind." **Reality:** Vite + React (no Tailwind, no Next.js, no routing).

---

## 6. MISSING INTERFACES

| Interface (Spec §) | Required Signature | Status |
|---|---|---|
| `LLMProvider.generate()` (§8) | `async def generate(prompt, context) -> str` | ❌ |
| `LLMProvider.structured()` (§8) | `async def structured(prompt, schema) -> dict` | ❌ |
| `LLMProvider.health()` (§8) | `async def health() -> bool` | ❌ |
| `VirtualClock.schedule()` (§15) | `def schedule(time, callback)` | ❌ |
| `VirtualClock.cancel()` (§15) | `def cancel(event_id)` | ❌ |
| `VirtualClock.next_event()` (§15) | `def next_event() -> Event` | ❌ |
| `VirtualClock.run_until()` (§15) | `def run_until(time)` | ❌ |
| `FailureNormalizer` (§12) | Normalize raw failure codes to canonical codes | ❌ |
| `FailureClassifier` (§12) | Classify to 7 categories | ❌ |
| `RetryabilityResolver` (§12) | Determine retryability from classification | ❌ |
| `ReconciliationResolver` (§12) | Resolve UNKNOWN → authoritative state | ❌ |
| `EconomicEngine.calculate_nev()` (§23) | `ExpectedRecovery - ActionCost - RelationshipCost - RiskCost` | ❌ |
| `RevenueEpisode.aggregate()` (§16) | Combine payment/checkout/invoice into episode | ❌ |
| `CounterfactualEvaluator.fork()` (§28) | Create control + treatment worlds from identical state | ❌ |
| `CounterfactualEvaluator.evaluate()` (§28) | `treatment_outcome - control_outcome` | ❌ |
| `AuditLedger.log()` (§33) | Hash-chained event logging | ❌ |

---

## 7. IMPLEMENTATION DEPENDENCIES

### 7.1 Python Dependencies (Current)

```text
pydantic, networkx, fastapi, uvicorn, openai, dashscope
```

### 7.2 Required Python Dependencies (From Spec)

| Dependency | Purpose | Spec Section |
|---|---|---|
| `pydantic` | Schema validation, structured output | §6 |
| `fastapi` | API server | §13 |
| `uvicorn` | ASGI server | §13 |
| `httpx` | Async HTTP client for HF inference | §8-9 |
| `huggingface_hub` | HF Inference API client | §8-9 |
| `networkx` | Interference graph | §27 |
| `pytest` | Testing framework | §38 |
| `python-dotenv` | Environment configuration | §9 |

### 7.3 Dependencies to REMOVE

| Dependency | Reason |
|---|---|
| `openai` | Spec requires HF Inference + local Qwen, not OpenAI |
| `dashscope` | Alibaba Cloud SDK — not in spec |
| `supabase` (implied) | Spec says SQLite initially |

---

## 8. TESTING DEPENDENCIES

### 8.1 Required Test Layers (Spec §38)

| Layer | Spec Requirement | Current Status |
|---|---|---|
| **Unit** | FSM, policy, risk, economics, clock, memory, classifier | ⚠️ FSM and safety tests exist; economics, clock, classifier tests missing |
| **Integration** | agent → tool → simulator | ⚠️ Agent runtime test exists but tests hardcoded demo flow |
| **Scenario** | payment failure, unknown state, gateway outage, checkout abandonment, invoice overdue | ❌ No scenario tests |
| **Adversarial** | LLM malformed JSON, LLM timeout, duplicate action, invalid transition, future-data leakage, infinite loop, policy bypass, tool failure | ❌ No adversarial tests |

### 8.2 Critical Tests Required (Spec §39-42)

| Test | Spec Section | Status |
|---|---|---|
| `test_agent_cannot_access_future_outcome()` | §39 | ❌ |
| `test_unknown_payment_blocks_duplicate_action()` | §40 | ❌ |
| `test_chaos_causes_replan()` | §41 | ❌ |
| `test_recovery_metric_is_counterfactual()` | §42 | ❌ |

---

## 9. RUNTIME LLM DEPENDENCIES

### 9.1 Spec Requirements (§8-10)

| Component | Requirement | Status |
|---|---|---|
| Primary LLM | HuggingFace Inference Provider | ❌ Not implemented |
| Fallback LLM | Local Qwen3-4B via OpenAI-compatible API | ❌ Not implemented |
| Router | AUTO → HF → local fallback | ❌ Not implemented |
| Fallback Logging | JSON event on every fallback | ❌ |
| Configuration | `ULTRON_LLM_PROVIDER`, `HF_TOKEN`, `HF_MODEL`, `LOCAL_LLM_URL`, `LOCAL_LLM_MODEL` | ❌ |
| Provider Abstraction | `LLMProvider` base class | ❌ |
| Hardware Constraint | 16GB RAM, GTX 1650 4GB VRAM — small quantized model | Acknowledged |

---

## 10. SIMULATOR DEPENDENCIES

### 10.1 World Model Entities (Spec §13)

| Entity | Status | Gap |
|---|---|---|
| Customer | ✅ Exists | Missing relationship signals (§25) |
| Payment | ✅ Exists | Missing `rail`, `gateway_id`, `attempt` tracking |
| PaymentAttempt | ❌ MISSING | Not modeled |
| Invoice | ✅ Exists | Minimal fields |
| CheckoutSession | ✅ Exists | Minimal fields |
| Gateway | ❌ MISSING | No gateway entity or health model |
| RecoveryAction | ❌ MISSING | Actions are not persisted as entities |
| Communication | ❌ MISSING | No communication tracking |
| Mission | ✅ Exists | Missing spec-required fields |
| Event | ⚠️ PARTIAL | Exists as dicts in event bus, not typed domain entities |

### 10.2 Virtual Clock (Spec §15)

| Method | Status |
|---|---|
| `now()` | ✅ (`get_time()`) |
| `advance()` | ✅ |
| `schedule()` | ❌ |
| `cancel()` | ❌ |
| `next_event()` | ❌ |
| `run_until()` | ❌ |

The clock falls back to `time.time()` when `current_time == 0`, mixing real and virtual time.

### 10.3 Chaos Engine (Spec §31)

7 chaos events required. Only random payment failure is implemented. None of the named event types exist.

### 10.4 Data Generation (Spec §36-37)

Only 1 customer scenario exists (Ananya Textiles). Spec requires 200 customers, 2000 payments, 300 invoices, 500 checkout sessions with deterministic seeding.

---

## 11. FINANCIAL FSM REQUIREMENTS

### 11.1 Payment FSM (Spec §11)

**Required States:** CREATED, INITIATED, AUTHORIZING, AUTHORIZED, CAPTURED, SETTLED, FAILED, UNKNOWN, RECONCILING, REVERSED, REFUNDED

**Current States:** CREATED, AUTHORIZED, CAPTURED, SETTLED, FAILED, UNKNOWN, REVERSED

**Missing:** INITIATED, AUTHORIZING, RECONCILING, REFUNDED

### 11.2 FSM Enforcement

FSM validation fires only on explicit world update methods. No enforcement on Checkout status transitions. FSM classes do not emit events on transition.

---

## 12. COUNTERFACTUAL EVALUATOR REQUIREMENTS

This is the **most critical missing subsystem** (Spec §28-29, §42).

### 12.1 Required Architecture

```text
WORLD STATE (snapshot)
    │
    ├──────────────┐
    ▼              ▼
CONTROL          TREATMENT
No action        ULTRON action
    │              │
    ▼              ▼
Outcome          Outcome
    │              │
    └──────┬───────┘
           ▼
   Incremental Recovery = Treatment - Control
```

### 12.2 Current State

No counterfactual evaluator exists. The baseline agent is not a proper control — it is a separate simplified agent running independently without world-state forking or deterministic seeds.

---

## 13. BLOCKERS FOR IMPLEMENTATION

### P0 — Must Resolve Before Any Phase

1. Eliminate dual entry points — consolidate to single `main.py`
2. Remove dead code (`database/`, `backend/simulator_api.py`, `backend/audit/engine.py`, `backend/metrics/engine.py`, `static/`, `check_size.py`, `download_qwen.py`, `qwen_test.py`)
3. Fix broken imports (`financial/reconciliation.py`, `backend/simulator_api.py`)
4. Resolve duplicate audit and metrics systems
5. Establish proper Python package structure

### P1 — Must Resolve Before Agent Core

1. Complete Payment FSM with all 11 states
2. Implement Virtual Clock with schedule/cancel/run_until
3. Implement typed Domain Event model
4. Create Gateway, PaymentAttempt, RecoveryAction, Communication entities

### P2 — Must Resolve Before Demo

1. Implement LLM Provider architecture (§8-10)
2. Implement Counterfactual Evaluator (§28-29) — completely isolated from agent
3. Implement Economic Engine (§23)
4. Implement all 7 Chaos event types (§31)
5. Implement hash-chained Audit Ledger (§33)

---

## 14. RISK ASSESSMENT

| Risk | Severity | Mitigation |
|---|---|---|
| Counterfactual engine not existing | **CRITICAL** | Implement in isolated module before agent integration |
| LLM being a hardcoded script | **CRITICAL** | Implement proper LLM provider with HF + local fallback |
| No test for future-data leakage | **HIGH** | Write `test_agent_cannot_access_future_outcome()` immediately after counterfactual engine |
| Broken imports in production files | **HIGH** | Fix before any further development |
| Real `time.time()` fallback in virtual clock | **HIGH** | Remove real-time fallback from clock |
| Database client depending on Supabase | **MEDIUM** | Replace with SQLite |
| Frontend uses wrong technology stack | **MEDIUM** | Decide: keep Vite or migrate to Next.js |
