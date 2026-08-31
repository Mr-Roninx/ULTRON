# ULTRON v3.6 — PHASE 14 FORENSIC REPOSITORY AUDIT
## Architectural Integrity, Component Mapping & Reusability Audit

---

## 1. Executive Summary

This forensic audit catalogues existing ULTRON v3.5 subsystems, verified contracts, reusable components, and architectural boundaries before implementing Phase 14 Evidence & Reality Audit.

---

## 2. Core Architectural Components & Interfaces

| Component | File Path | Core Interfaces & Responsibilities | Reusability in Phase 14 |
| :--- | :--- | :--- | :--- |
| **Virtual Clock** | `simulator/clock.py` | `now()`, `advance(seconds)`, `advance_to(timestamp)`, `schedule(timestamp, cb)`, `reset()` | **Authoritative Temporal Anchor**. Used for deterministic time simulation across all experiments. |
| **World State** | `simulator/world.py` | `add_customer()`, `add_payment()`, `add_invoice()`, `add_checkout()`, `update_payment_status()`, `snapshot()`, `restore_from()` | **World Ground Truth**. Isolated deep copies used for counterfactual branches. |
| **Agent Loop** | `backend/agent/loop.py` | `tick()`, `wake()`, `fsm`, `chosen_intent`, `feasible_actions`, `replan_count`, `context` | **Autonomous Agent Lifecycle**. Executes 13-state FSM from OBSERVE to LEARN. |
| **LLM Router & Providers** | `backend/llm/provider.py` | `HuggingFaceProvider`, `LocalQwenProvider`, `MockProvider`, `LLMRouter.generate_intent()` | **Provider Hierarchy & Failover**. Primary (HF) $\rightarrow$ Fallback (Local) $\rightarrow$ Safe Deterministic Fallback. |
| **Action Ranker & Decision Authority** | `backend/agent/action_ranker.py`, `financial/authority.py` | `rank_actions(feasible_actions, context)`, `ActionDecisionAuthority.validate()` | **Deterministic Authority**. Enforces NEV ranking and overrides LLM intent safely. |
| **Economic Engine** | `backend/economics/engine.py`, `relationship.py` | `calculate_nev()`, `evaluate_action()`, `RelationshipModel.calculate_relationship_cost()` | **Net Expected Value (NEV)**. Evaluates expected recovery, downstream LTV, costs, and contact fatigue. |
| **Policy & Risk Engines** | `financial/policy.py`, `financial/risk.py` | `policy_engine.validate()`, `risk_engine.validate()` | **Fail-Closed Safety Gates**. Prevents invalid state mutations or excessive risk. |
| **Temporal Observation Firewall** | `backend/benchmark/firewall.py` | `TemporalObservationFirewall.enforce(context, current_time)` | **Anti-Lookahead Firewall**. Throws `FutureInformationLeakageError` on future data access. |
| **Episodic Memory** | `memory/episodic.py` | `MemoryStore.store_episode()`, `search()`, `get_similar()` | **Learning & Prediction Error**. Stores `(failure_type, action, prediction_error)` and informs future planning. |
| **Payment Intelligence** | `backend/payment_intelligence/` | `failure_normalizer`, `failure_classifier`, `recoverability_scorer`, `rail_health_engine` | **Diagnosis & Rail Telemetry**. Normalizes 5 failure classes, ISO codes, and gateway health. |
| **Customer Revenue Missions** | `backend/mission/` | `RevenueMissionBuilder.build_or_update_mission()`, `RevenueMission` | **Multi-Opportunity Aggregator**. Consolidates Subscriptions, Checkouts, and Invoices. |
| **Chaos Engine** | `simulator/chaos.py` | `chaos_engine.trigger("GATEWAY_DEGRADATION", ...)` | **Dynamic Environmental Perturbation**. Mutates gateway health and payment state during sleep. |
| **Audit Ledger & Telemetry** | `backend/audit/ledger.py`, `backend/agent/telemetry.py` | `audit_ledger.log()`, `telemetry.log_event()`, `log_decision_differential()` | **Immutable Trace Recording**. Logs structured event history without private secrets. |

---

## 3. Files Requiring Creation (Phase 14 Evidence Architecture)

1. `backend/evidence/`
   - `__init__.py`
   - `models.py`: Pydantic evidence schemas, experiment manifests, metric containers.
   - `instrumentation.py`: Deterministic state hashers, secret scrubbers, execution timers.
   - `scenarios.py`: 6 standard failure scenarios with fixed initial worlds.
   - `llm_evidence.py`: Real LLM provider check, candidate influence & novelty calculations.
   - `mechanism_evidence.py`: Controlled ablations for Payment Intelligence, Memory, Replanning, and Chaos.
   - `economic_evidence.py`: Multi-seed paired counterfactual benchmark runner.
   - `statistical_analysis.py`: Bootstrap 95% confidence intervals, mean/median/std dev, effect sizes.
   - `anti_gaming.py`: Static and dynamic repository scanner detecting benchmark gaming.
   - `report_generator.py`: Evidence artifact builder producing JSON and Markdown reports.
   - `experiment.py`: Master CLI runner `python -m backend.evidence.experiment --all`.

2. `tests/evidence/`
   - `test_llm_live_path.py`
   - `test_llm_candidate_influence.py`
   - `test_payment_intelligence_effect.py`
   - `test_memory_effect.py`
   - `test_replanning_effect.py`
   - `test_chaos_effect.py`
   - `test_economic_lift.py`
   - `test_experiment_isolation.py`
   - `test_evidence_integrity.py`
   - `test_statistical_analysis.py`

3. `frontend/src/components/ProofModePanel.tsx`

---

## 4. Protected Files (Must NOT Be Modified)

- `financial/fsm.py` (Standardized financial payment/invoice state machines)
- `tests/test_phase1.py` - `tests/test_phase8.py` (Historical phase contracts)
- `backend/benchmark/firewall.py` (Authoritative Temporal Observation Firewall)

---

## 5. Verification Commands

- Master Evidence Experiment: `python -m backend.evidence.experiment --all`
- Evidence Test Suite: `pytest -q tests/evidence/`
- Full Repository Regression: `pytest -q`
