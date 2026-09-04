# ULTRON-AGENT Master Engineering Upgrade Plan (v2)

## Overview
This plan defines the end-to-end engineering architecture and implementation steps to upgrade the local **ULTRON** system from a deterministic Razorpay recovery control plane into a genuine, measurable, bounded, tool-using, memory-enabled, planning and replanning **AI Agent**—while strictly maintaining the invariant that **deterministic ULTRON remains the sole financial authority**.

---

## Non-Negotiable Invariants & Safety Guardrails
1. **AI = Intelligence, Deterministic ULTRON = Authority, Razorpay = External Payment Truth**.
2. **Zero Agent Financial Authority**: No agent can execute Razorpay write APIs, mark an opportunity as `AUTHORIZED`, modify Action Authority compliance checks, or write directly to financial ledger tables.
3. **Deterministic Economics Authority**: Expected Incremental Value (`IVEN`) and net economic value formulas are strictly computed by deterministic algorithms. LLM-generated semantic signals (bounded $0.0 \le s \le 1.0$) are calibrated into bounded economic modifiers; final economics is always computed deterministically.
4. **Kill Switch Propagation**: When the kill switch is engaged, it halts financial execution *and* terminates all active agent loops, tool invocations, agent proposals, autonomous replanning, and outreach generation.
5. **Temporal & Memory Firewall**: Only facts, events, and memories with timestamps $T_{event} \le T_{decision}$ are ever exposed to the agent context.
6. **No Phantom Claims**: Every probability shown is labeled `model-estimated`. Every claim in the "Why?" explainer maps to a real, stored record in SQLite. All LLM causal effects are empirically measured (`POSITIVE_EFFECT`, `NEGATIVE_EFFECT`, or `NO_EFFECT`).
7. **Local Isolation**: Only local workspace code, tests, and database files are used. No external git pulls, no fake webhooks in real webhook pathways, and zero secret leakage.

---

## Target Architecture

```
                         RAZORPAY (Test Mode)
                                  │
                                  ▼
                          EVENT / WEBHOOK
                                  │
                                  ▼
                           EVENT FABRIC
                                  │
                                  ▼
                         AGENT ORCHESTRATOR
                                  │
                ┌─────────────────┼──────────────────┐
                │                 │                  │
                ▼                 ▼                  ▼
           PERCEPTION        STRATEGY/          COMPLIANCE
             AGENT           CALIBRATION          COPILOT
                │              AGENT                 │
                │                 │                  │
                └─────────────────┼──────────────────┘
                                  │
                                  ▼
                         AGENT PROPOSAL BUS
                                  │
                                  ▼
                       DETERMINISTIC ECONOMICS
                                  │
                             IVEN / NEV
                                  │
                                  ▼
                          RECOVERY MARKET
                                  │
                                  ▼
                         ACTION AUTHORITY
                                  │
                             AUTHORIZED?
                             /        \
                           NO          YES
                           │            │
                          STOP          ▼
                                   EXECUTION
                                       │
                                       ▼
                                    RAZORPAY
                                       │
                                       ▼
                               PROVIDER TRUTH
                               /             \
                          WEBHOOK            POLLER
                               \             /
                                ▼           ▼
                                RECONCILIATION
                                       │
                                       ▼
                                    OUTCOME
                                       │
                                       ▼
                                  AGENT LEARN
                                       │
                                       ▼
                                    MEMORY
                                       │
                                       └────→ NEXT CYCLE
```

---

## Phased Implementation Roadmap

### Phase 0: Baseline Verification & Environment Inspection
- Validate current database schema, existing test scripts, and test mode status.
- Document baseline performance metrics (latency, IVEN calculations, compliance checks).

### Phase 1: Agent Database, State Machine, Gate & Telemetry
- **Database Schema Extensions** (`src/db/database.ts`):
  - `agent_runs`: Stores mission lifecycle, status, start/end times, goal type, budgets, token usage.
  - `agent_states`: Persisted state machine states for active & historical missions.
  - `agent_steps`: Granular step-by-step trace of observations, thoughts, tool requests, and transitions.
  - `agent_tool_calls`: Log of every tool call, hashed inputs/outputs, latency, status, permission check.
  - `agent_plans`: Persisted initial and replanned plans, validity assumptions, candidate actions.
  - `agent_hypotheses`: Structured failure diagnoses and confidence levels.
  - `agent_proposals`: Proposals submitted to the deterministic bus (cannot directly mutate financial state).
  - `agent_memories`: Working, episodic, and semantic memory items with timestamps and provenance.
  - `agent_outcomes`: Post-reconciliation outcome evaluation, predicted vs actual, error metrics.
  - `agent_authority_checks`: Security audit of every agent operation against the Agent Authority Gate.
  - `llm_invocations`: Raw telemetry (model, prompt hash, completion hash, latency, tokens, error).
  - `outreach_drafts`: Proposed communication drafts (always status `PENDING_REVIEW`).
  - `perception_annotations`: Semantic labels enriched by the Perception Agent.
- **Agent State Machine** (`src/agents/state_machine.ts`):
  - 21 explicit states: `IDLE`, `TRIGGERED`, `OBSERVE`, `INVESTIGATE`, `DIAGNOSE`, `HYPOTHESIZE`, `PLAN`, `VALIDATE_PLAN`, `PROPOSE`, `WAIT_AUTHORITY`, `EXECUTE`, `WAIT`, `WAKE`, `OBSERVE_OUTCOME`, `PLAN_INVALIDATED`, `REPLAN`, `LEARN`, `MEMORY_UPDATE`, `COMPLETE`, `ABORTED`, `HUMAN_REVIEW`.
  - Deterministic state transition guards and validation.
- **Agent Authority Gate** (`src/agents/gate.ts`):
  - 9 mandatory checks: `kill_switch_check`, `agent_identity_check`, `tool_scope_check`, `mission_budget_check`, `rate_limit_check`, `write_boundary_check`, `environment_check`, `injection_taint_check`, `loop_guard_check`.
- **Budgets & Loop Guard** (`src/agents/budget.ts`, `src/agents/loop_guard.ts`):
  - Enforce `max_llm_calls` (8), `max_tool_calls` (20), `max_replans` (3), `max_steps` (40), `max_wall_clock_ms` (30000).
  - Tool/plan fingerprinting to prevent repetitive loops.

### Phase 2: Tool Registry & Structured AgentIntent
- **Agent Tool Registry** (`src/agents/tool_registry.ts`):
  - Tool permissions: `READ`, `ANALYZE`, `PROPOSE`, `APPROVE`, `EXECUTE`, `FINANCIAL_WRITE`.
  - Strictly limits LLM agents to `READ`, `ANALYZE`, `PROPOSE`.
  - 14 Read-only tools:
    - `get_opportunity`
    - `get_payment_context`
    - `get_customer_history`
    - `get_payment_attempts`
    - `get_failure_history`
    - `get_gateway_state`
    - `get_contact_history`
    - `get_market_state`
    - `get_recovery_capacity`
    - `get_reconciliation_state`
    - `get_provider_status`
    - `get_full_audit_trail`
    - `get_similar_cases`
    - `get_agent_memory`
  - 4 Proposal tools:
    - `create_agent_proposal`
    - `create_perception_annotation`
    - `create_strategy_proposal`
    - `create_outreach_draft`
- **Structured AgentIntent & Schemas** (`src/agents/types.ts`, `src/agents/schema.ts`):
  - Enforce Zod/JSON-Schema validation for all agent outputs and tool calls.

### Phase 3: LLM Provider, Context Builder & Structured Reasoning
- **LLM Provider Abstraction** (`src/agents/llm_provider.ts`):
  - Primary: NVIDIA NIM API (`nvidia/nemotron-3.5-lightning-30b-a3b` or `openai/gpt-oss-120b`).
  - Fallback: Secondary models or deterministic ULTRON rule-based policy.
  - Zero crashes on 429/5xx/timeouts/malformed responses.
- **Context Builder** (`src/agents/context_builder.ts`):
  - Temporal firewall: Strips any data where $T_{obs} > T_{now}$.
  - PII / Secret Sanitization: Strips PAN, CVV, webhook secrets, authorization headers.

### Phase 4: Working, Episodic, and Semantic Memory
- **Memory Store** (`src/agents/memory.ts`):
  - Working Memory: Mission-scoped active context with memory compaction/summarization.
  - Episodic Memory: Historical episode records with failure type, action, predicted vs actual outcome.
  - Semantic Memory: Generalized domain knowledge with provenance and confidence scores.
  - Temporal Memory Firewall (`src/agents/temporal_firewall.ts`): Prevents oracle leakage by only querying episodes finalized at or before $T_{mission}$.

### Phase 5: Planning, Waiting, Wake-up & Replanning
- **Planner** (`src/agents/planner.ts`):
  - Explicit goals (`RECOVER_PAYMENT`, `CALIBRATE_STRATEGY`, `INVESTIGATE_FAILURE`).
  - Candidate generation: Deterministic candidates $\cup$ Validated LLM candidates.
  - Assumption generation: Sets explicit preconditions (e.g. gateway health $\ge 0.75$, status = pending, capacity available).
- **Wait & Wake Engine** (`src/agents/wait_wake.ts`):
  - Durable persisted waiting states (`wake_at`, `wake_condition`).
  - Wake triggers on timers, provider status changes, or webhooks.
- **Replan Engine** (`src/agents/replan_engine.ts`):
  - Assumption re-evaluation on wake.
  - If invalid $\to$ `PLAN_INVALIDATED` $\to$ `REPLAN` within bounded replan budget.

### Phase 6: Intelligence $\to$ Economics Bridge
- **Bridge** (`src/agents/bridge.ts`):
  - Translates validated semantic signals ($0.0 \le s \le 1.0$) into calibrated incremental probability and cost modifiers.
  - Feeds into deterministic `calculateScore` in `src/economics/scorer.ts`.
  - Invariant assertion: Economic value is strictly computed deterministically.

### Phase 7: Outcome Evaluation & Learning
- **Learning Engine** (`src/agents/learning.ts`):
  - Evaluates provider truth vs prediction error upon payment settlement or expiration.
  - Persists outcome into `agent_outcomes` and records new episodic memory.
  - Proposes strategy calibration updates when evidence threshold $\ge 30$ outcomes is met.

### Phase 8: Specialist Agents & Master Orchestrator
- **Specialist Implementations** (`src/agents/specialists/`):
  - `perception_agent.ts`: Semantic annotations for unstructured reason strings.
  - `strategy_agent.ts`: Proposes probability updates and allocator tuning.
  - `outreach_agent.ts`: Generates email/SMS/WhatsApp drafts with mandatory compliance footers.
  - `compliance_copilot.ts`: Answers audit queries using stored tables only.
  - `merchant_copilot.ts`: Natural language analytics for operators.
- **Agent Orchestrator** (`src/agents/orchestrator.ts`):
  - Dispatches specialist agents, coordinates state machine, enforces budgets, triggers wait/replan loops.

### Phase 9: Causal Experiments & Benchmarking
- **Causal Evaluation Suite** (`scripts/run_causal_experiments.ts`):
  - `LLM_OFF` vs `LLM_ON`
  - `MEMORY_OFF` vs `MEMORY_ON`
  - `REPLAN_OFF` vs `REPLAN_ON`
  - `TOOLS_OFF` vs `TOOLS_ON`
  - `FULL_AGENT` with paired synthetic seeds.
  - Structured output written to `results/agent/*.json`.

### Phase 10: Razorpay Test Mode End-to-End Integration & API Routes
- **Agent API Routes** (`src/routes/agents.ts`):
  - Endpoints for missions, runs, state inspect, tool calls, replan triggers, memory query, telemetry.
- **End-to-End Test & Demo** (`scripts/demo_agent_recovery.ts`):
  - Full pipeline: Failed payment $\to$ Agent investigation $\to$ Diagnosis $\to$ Plan $\to$ Economic scoring $\to$ Market allocation $\to$ Authority check $\to$ Razorpay execution $\to$ Wait/Wake $\to$ Reconcile $\to$ Outcome evaluation $\to$ Learning $\to$ Memory update.

### Phase 11: Comprehensive Test Suite, Documentation & Frontend Control Center
- **Test Suite** (`tests/agent/`):
  - 20+ unit and integration test files covering state machine, gate, budgets, loop guard, memory, firewall, schemas, prompt injection, tool injection, economic safety, replanning, learning, trace, and kill switch.
- **Documentation**:
  - 11 architectural documents in `docs/`
  - Master report: `ULTRON_AI_AGENT_MASTER_REPORT.md`
- **Frontend Agent Control Center** (`frontend/src/app/page.tsx`):
  - Live Agent State Machine graph and state badge.
  - Active Mission tracker with goals, budgets, and step timeline.
  - Tool Invocation monitor showing input/output hashes and latency.
  - Plan & Replanning tab with assumption validity status.
  - Semantic Signals & Economics bridge visualizer.
  - Episodic & Semantic Memory explorer.
  - Outreach Drafts review panel.
  - Causal Experiment benchmark dashboard.
  - Forensic "Why?" explainability inspector based strictly on stored records.

---

## Proposed File Changes

### Backend Core & Agents
- `[MODIFY]` [database.ts](file:///d:/Work%20Space/Project/Ultron/src/db/database.ts) (Add agent tables, indexes, and query methods)
- `[MODIFY]` [types/index.ts](file:///d:/Work%20Space/Project/Ultron/src/types/index.ts) (Add agent types, state enums, tool interfaces)
- `[NEW]` [src/agents/types.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/types.ts)
- `[NEW]` [src/agents/schema.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/schema.ts)
- `[NEW]` [src/agents/state_machine.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/state_machine.ts)
- `[NEW]` [src/agents/gate.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/gate.ts)
- `[NEW]` [src/agents/budget.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/budget.ts)
- `[NEW]` [src/agents/loop_guard.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/loop_guard.ts)
- `[NEW]` [src/agents/tool_registry.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/tool_registry.ts)
- `[NEW]` [src/agents/tools/read_tools.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/tools/read_tools.ts)
- `[NEW]` [src/agents/tools/proposal_tools.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/tools/proposal_tools.ts)
- `[NEW]` [src/agents/llm_provider.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/llm_provider.ts)
- `[NEW]` [src/agents/context_builder.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/context_builder.ts)
- `[NEW]` [src/agents/temporal_firewall.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/temporal_firewall.ts)
- `[NEW]` [src/agents/memory.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/memory.ts)
- `[NEW]` [src/agents/planner.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/planner.ts)
- `[NEW]` [src/agents/wait_wake.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/wait_wake.ts)
- `[NEW]` [src/agents/replan_engine.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/replan_engine.ts)
- `[NEW]` [src/agents/bridge.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/bridge.ts)
- `[NEW]` [src/agents/learning.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/learning.ts)
- `[NEW]` [src/agents/telemetry.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/telemetry.ts)
- `[NEW]` [src/agents/orchestrator.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/orchestrator.ts)
- `[NEW]` [src/agents/specialists/perception_agent.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/specialists/perception_agent.ts)
- `[NEW]` [src/agents/specialists/strategy_agent.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/specialists/strategy_agent.ts)
- `[NEW]` [src/agents/specialists/outreach_agent.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/specialists/outreach_agent.ts)
- `[NEW]` [src/agents/specialists/compliance_copilot.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/specialists/compliance_copilot.ts)
- `[NEW]` [src/agents/specialists/merchant_copilot.ts](file:///d:/Work%20Space/Project/Ultron/src/agents/specialists/merchant_copilot.ts)
- `[NEW]` [src/routes/agents.ts](file:///d:/Work%20Space/Project/Ultron/src/routes/agents.ts)
- `[MODIFY]` [src/server.ts](file:///d:/Work%20Space/Project/Ultron/src/server.ts) (Mount agents router)
- `[MODIFY]` [package.json](file:///d:/Work%20Space/Project/Ultron/package.json) (Add test and experiment script commands)

### Test Suite (`tests/agent/`)
- `[NEW]` `tests/agent/test_agent_state_machine.ts`
- `[NEW]` `tests/agent/test_agent_orchestrator.ts`
- `[NEW]` `tests/agent/test_agent_tool_registry.ts`
- `[NEW]` `tests/agent/test_agent_gate.ts`
- `[NEW]` `tests/agent/test_agent_budget.ts`
- `[NEW]` `tests/agent/test_agent_loop_guard.ts`
- `[NEW]` `tests/agent/test_agent_memory.ts`
- `[NEW]` `tests/agent/test_agent_temporal_firewall.ts`
- `[NEW]` `tests/agent/test_agent_schema.ts`
- `[NEW]` `tests/agent/test_agent_prompt_injection.ts`
- `[NEW]` `tests/agent/test_agent_tool_injection.ts`
- `[NEW]` `tests/agent/test_agent_semantic_signals.ts`
- `[NEW]` `tests/agent/test_agent_economic_bridge.ts`
- `[NEW]` `tests/agent/test_agent_authority_boundary.ts`
- `[NEW]` `tests/agent/test_agent_execution_boundary.ts`
- `[NEW]` `tests/agent/test_agent_replanning.ts`
- `[NEW]` `tests/agent/test_agent_learning.ts`
- `[NEW]` `tests/agent/test_agent_llm_fallback.ts`
- `[NEW]` `tests/agent/test_agent_trace.ts`
- `[NEW]` `tests/agent/test_agent_kill_switch.ts`
- `[NEW]` `tests/agent/run_all_agent_tests.ts`

### Causal Experiments & Evidence Artifacts
- `[NEW]` `scripts/run_causal_experiments.ts`
- `[NEW]` `scripts/demo_agent_recovery.ts`
- `[NEW]` `results/agent/*.json` (17 JSON evidence artifacts)

### Frontend Control Center
- `[MODIFY]` [frontend/src/app/page.tsx](file:///d:/Work%20Space/Project/Ultron/frontend/src/app/page.tsx) (Integrate dedicated Agent Control Center view, real-time mission lifecycle monitor, memory inspector, replanning debugger, and empirical experiment cards)

### Documentation
- `[NEW]` `docs/ULTRON_AGENT_ARCHITECTURE.md`
- `[NEW]` `docs/ULTRON_AGENT_STATE_MACHINE.md`
- `[NEW]` `docs/ULTRON_AGENT_ORCHESTRATOR.md`
- `[NEW]` `docs/ULTRON_AGENT_TOOLS.md`
- `[NEW]` `docs/ULTRON_AGENT_MEMORY.md`
- `[NEW]` `docs/ULTRON_AGENT_REPLANNING.md`
- `[NEW]` `docs/ULTRON_AGENT_LLM.md`
- `[NEW]` `docs/ULTRON_AGENT_ECONOMIC_BRIDGE.md`
- `[NEW]` `docs/ULTRON_AGENT_SECURITY.md`
- `[NEW]` `docs/ULTRON_AGENT_EVIDENCE.md`
- `[NEW]` `docs/ULTRON_AGENT_LIMITATIONS.md`
- `[NEW]` `ULTRON_AI_AGENT_MASTER_REPORT.md`

---

## Verification Plan

### Automated Tests
1. **Agent Unit & Safety Tests**:
   - `npx tsx tests/agent/run_all_agent_tests.ts`
   - Verifies 20 test suites: state machine, gate, loop guard, injection tests, financial authority boundaries, memory isolation, schema validation, replanning, and kill switch.
2. **Regression Tests**:
   - `npx tsx scripts/test_perception.ts`
   - `npx tsx scripts/test_economics.ts`
   - `npx tsx scripts/test_market.ts`
   - `npx tsx scripts/test_authority.ts`
   - `npx tsx scripts/test_execution.ts`
   - `npx tsx scripts/test_truth_engine.ts`
   - `npx tsx scripts/verify_no_fake_webhooks.ts`
3. **Causal Experiments**:
   - `npx tsx scripts/run_causal_experiments.ts`
   - Validates paired experiments (LLM ON/OFF, Memory ON/OFF, Replan ON/OFF, Tools ON/OFF) and generates all 17 evidence JSON files.
4. **End-to-End Demo**:
   - `npx tsx scripts/demo_agent_recovery.ts`
   - Verifies full mission from failed payment $\to$ agent investigation $\to$ plan $\to$ market $\to$ authority $\to$ execution $\to$ wait/wake $\to$ reconcile $\to$ outcome $\to$ learning $\to$ episodic memory.

### Manual / Visual Verification
1. Launch backend (`npm run dev`) and frontend (`npm run dev` in `frontend`).
2. Verify all tabs in Agent Control Center: State Machine graph, Active Mission trace, Tool Execution logs, Replanning timeline, Episodic Memory table, and the "Why?" Forensic Inspector.
3. Test kill switch toggle and verify immediate agent shutdown in UI.
