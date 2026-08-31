# ULTRON v3.5 — PHASE 13 SPECIFICATION
## Payment Intelligence & Real Revenue Recovery Environment

---

## 1. Executive Summary

ULTRON v3.5 introduces deep Payment Intelligence and a high-fidelity multi-opportunity financial simulation environment. ULTRON models the financial world not as generic API pings, but as an interplay of banking networks, gateway degradation, customer friction fatigue, issuer failure codes, and multi-opportunity cross-channel revenue missions.

---

## 2. Core Architectural Principle: Non-Negotiable LLM Safety Boundary

```
[WORLD STATE / TELEMETRY]
           │
           ▼
[INVESTIGATION & DIAGNOSIS ENGINE] ── (Normalized Taxonomy, Gateway Health, Rail Health)
           │
           ▼
[LLM REASONER (Qwen/Qwen2.5-72B-Instruct)]
           │
           ▼
[AgentIntent (Hypothesis, Candidate Actions, Preferred Action, Yield, Reasoning)]
           │
           ▼
[DETERMINISTIC FEASIBLE ACTION GENERATOR]
           │
           ▼
[UNION POOL = UNION(LLM Candidates, Deterministic Actions)]
           │
           ▼
[FAIL-CLOSED POLICY, FSM & RISK ENGINE] ── (Prohibitions, Limits, Auth Tiers)
           │
           ▼
[ECONOMIC ENGINE: NET EXPECTED VALUE (NEV)]
  NEV = ExpectedRecovery + DownstreamValue - FinancialCost - OperationalCost - RelationshipCost - RiskCost
           │
           ▼
[ACTION DECISION AUTHORITY] ── (Authoritative Selection & Execution)
           │
           ▼
[TOOL EXECUTION ──> VIRTUAL CLOCK WAIT ──> CHAOS MONITOR ──> REPLAN ──> EPISODIC LEARNING]
```

---

## 3. Sub-System Implementations

### 3.1 Failure Taxonomy & Normalization (`backend/payment_intelligence/`)
- Standardized failure taxonomy across 5 categories:
  1. `TRANSIENT` (e.g., Issuer unavailable, network timeout, rate limit)
  2. `CUSTOMER_ACTION_REQUIRED` (e.g., Insufficient funds, 3DS expired, CVV incorrect)
  3. `HARD_DECLINE` (e.g., Stolen card, closed account, fraudulent transaction)
  4. `CONFIGURATION` (e.g., Currency unsupported, merchant MID inactive)
  5. `INFRASTRUCTURE` (e.g., Gateway 502/504, rail outage)
- Raw error code normalization across Gateway A (UPI/Stripe), Gateway B (Cards/Adyen), Gateway C (ACH/Razorpay) to unified ISO/ULTRON schemas.

### 3.2 Rail & Gateway Health Telemetry (`rail_health.py`)
- Real-time tracking of success probabilities, p95 latencies, error burst rates, and degradation status.
- Dynamically throttles retry eligibility when gateway health falls below 70%.

### 3.3 Multi-Opportunity Customer Revenue Missions (`backend/mission/`)
- Aggregates multi-opportunity financial exposures per customer:
  - Active Recurring Subscriptions
  - Overdue Invoices
  - Abandoned Checkouts
- Computes unified total customer exposure and multi-opportunity cross-channel interference.

### 3.4 Economic Engine & Relationship Fatigue Calibration (`backend/economics/`)
- Formulates Net Expected Value (NEV):
  $$\text{NEV} = \text{Recovery} + \text{Downstream LTV} - \text{Financial Cost} - \text{Operational Cost} - \text{Relationship Friction Cost} - \text{Risk Cost}$$
- Exponential fatigue scaling prevents customer spam:
  $$\text{Cost} = \text{Base Channel Cost} \times (1.8)^{\text{recent contacts}} \times \text{Segment Sensitivity} \times \text{Recency Factor}$$
- Infinitary cost barrier ($+\infty$) for opted-out customers ensures absolute non-contact compliance.

### 3.5 Real Outcome Simulator (`backend/payment_simulator/`)
- Non-deterministic yet seed-reproducible outcome dynamics for retries, payment links, messaging, and customer responses.
- Generates realistic payment datasets (200 diverse customer accounts, 2,000+ realistic events).

### 3.6 Benchmark & Ablation Engine (`backend/benchmark/`)
- Extended with `disable_payment_intelligence` ablation testing.
- Counterfactual regret calculation isolates exact financial delta contributed by payment intelligence.

---

## 4. Verification & Golden Demo Summary
- **Golden Demo Scenario**: *Ananya Textiles* (₹24,700 total exposure).
  - T0: Transient failure (`91` Issuer Unavailable) $\rightarrow$ LLM proposes `SEND_PAYMENT_LINK`, Action Authority overrides with `RETRY_GATEWAY_B` (NEV = ₹18,017).
  - T+2h: Chaos injection degrades Gateway B to 20% health $\rightarrow$ Invalidation observed on wake $\rightarrow$ Agent triggers `REPLAN` $\rightarrow$ Selects alternate high-NEV route (`SEND_PAYMENT_LINK`).
  - Learning: Outcome observed, prediction error recorded into episodic memory.
