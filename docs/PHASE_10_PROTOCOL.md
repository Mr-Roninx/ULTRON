# ULTRON v3.2 — Phase 10 Benchmark Protocol

**Protocol Version:** 1.0.0  
**Evaluation Standard:** Controlled Simulation Benchmark  
**Author:** Senior ML & Fintech Systems Evaluation Engineer  
**Date:** 2026-08-28

---

## 1. Objective

The objective of Phase 10 is to build a scientifically defensible benchmark framework to evaluate whether the REAL ULTRON agent produces measurable, statistically significant incremental recovered revenue compared with credible non-ULTRON recovery strategies.

---

## 2. Experimental Architecture

### 2.1 Same Initial World Snapshot
Every strategy in the benchmark starts from the exact same immutable synthetic world snapshot:
```
generate_world(seed)
        │
        ▼
immutable_snapshot
        │
   ┌────┴────┐
   │         │
CONTROL   TREATMENT
   │         │
Baseline   ULTRON
   │         │
   └────┬────┘
        │
        ▼
Counterfactual Evaluation
```
Under no circumstances are independent random worlds generated for comparison.

### 2.2 Seed Management & Partitions
Deterministic pseudo-random world generation is partitioned as follows:
- **Development Partition:** Seeds 1–60
- **Validation Partition:** Seeds 61–80
- **Final Evaluation Partition:** Seeds 81–180

Seeds are strictly recorded in machine-readable output.

### 2.3 Simulated Horizons
- **Primary Benchmark Horizon:** 30 simulated days (2,592,000 seconds)
- **Sensitivity Horizons:** 7, 14, 30, and 60 days.

---

## 3. Evaluated Strategies

1. **NoAction (Control):**
   - Zero recovery interventions. Measures natural organic baseline recovery.
2. **FixedRetry:**
   - Conventional scheduled retries at T+4h, T+24h, T+48h. Respects FSM, policy, and unknown-payment protections.
3. **TraditionalDunning:**
   - Day 1 (T+24h) Email → Day 3 (T+72h) Reminder → Day 7 (T+168h) Escalation. Configuration-driven.
4. **RuleBasedRecovery:**
   - Credible deterministic business rules (transient → retry, liquidity → payment link, expired → credential update, overdue invoice → reminder, enterprise exposure → escalation). No LLM or dynamic replanning.
5. **REAL ULTRON (Treatment):**
   - Full 13-state agent loop (`OBSERVE` → `INVESTIGATE` → `HYPOTHESIZE` → `PLAN` → `FEASIBILITY` → `AUTHORITY` → `RISK` → `EXECUTE` → `WAIT` → `EVALUATE` → `LEARN` → `REPLAN` → `COMPLETE`). Complete cryptographic audit trace.

---

## 4. Trust Boundary & Future Information Firewall

The agent and its observation pipelines are strictly isolated by the `FutureInformationFirewall`.
Forbidden keys include:
- `control_outcome`, `treatment_outcome`, `baseline_outcome`
- `incremental_recovery`, `actual_recovery`, `counterfactual_recovery`
- `future_payment_status`, `future_customer_behavior`, `hidden_simulator_state`, `evaluator_state`

Any temporal query attempting to peek at $t > clock.now()$ or future clock queue events raises an immediate `FutureInformationLeakageError`.
