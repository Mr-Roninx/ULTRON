# ULTRON v5.0 Forensic Baseline & Migration Plan
**Document ID: ULTRON_V5_BASELINE_FORENSIC**  
**Date: 2026-08-29**  
**Status: COMPLETED (Phase 0 Audit Gate)**

---

## 1. Executive Summary & Test Baseline
This document establishes the authoritative baseline for transitioning the ULTRON autonomous revenue recovery platform from a purely synthetic research simulation (SWU-1.0 through SWU-1.5) to a **real payment provider platform** operating against **TEST/SANDBOX** environments (Razorpay, Stripe, Adyen).

### Verified Baseline:
- **Total Test Suite**: **390 tests passed in 102.47s (0 failures, 0 regressions)**
- **SWU Generations Maintained**: SWU-1.0, SWU-1.1, SWU-1.2, SWU-1.3, SWU-1.4, SWU-1.5
- **Deterministic Authority**: Non-authoritative LLM bound by ActionRegistry, ActionDecisionAuthority, PolicyEngine, RiskEngine, and DoubleEntryLedger.

---

## 2. Forensic Architectural Inventory

### 2.1 Reusable Components (Core Plane)
1. **Agent Loop & FSM** (`backend/agent/loop.py`, `state_machine.py`): Monolithic state machine supporting `OBSERVE`, `DIAGNOSE`, `HYPOTHESIZE`, `PLAN`, `FEASIBILITY`, `POLICY`, `RISK`, `NEV`, `ACTION_AUTHORITY`, `EXECUTE`, `WAIT`, `EVALUATE`, `REPLAN`, `LEARN`.
2. **Action Registry & Guard** (`backend/agent/action_registry.py`): Fail-closed schema with risk classification, permissions, customer tiers, and zero direct financial mutations.
3. **Deterministic NEV & Economics** (`backend/economics/nev.py`, `relationship.py`): True mathematical net economic value optimization.
4. **Payment Intelligence** (`backend/payment_intelligence/`): Failure taxonomy, code classification (ISO 8583 / network codes), gateway telemetry.
5. **Episodic Memory** (`memory/episodic.py`): Experience storage and semantic retrieval across missions.
6. **Observation Firewall** (`backend/benchmark/firewall.py`): Strict lookahead and secret isolation.
7. **Adversarial Double-Entry Ledgers** (`backend/audit/ledger.py`, `synthetic_payment_universe/world_v15/ledger/`): Conservation of balance ($\sum \text{Debits} == \sum \text{Credits}$).

### 2.2 Payment Abstractions & Discrepancy Analysis
- **Existing Synthetic State Models**: `simulator/models.py` (`PaymentStatus`: `CREATED`, `INITIATED`, `AUTHORIZING`, `AUTHORIZED`, `CAPTURED`, `SETTLED`, `FAILED`, `UNKNOWN`, `RECONCILING`, `REVERSED`, `REFUNDED`).
- **Required v5.0 Canonical Contract**: `backend/providers/models.py` defining provider-independent `CanonicalPayment`, `CanonicalPaymentAttempt`, `CanonicalPaymentEvent`, `CanonicalPaymentLink`, `CanonicalSettlement`, `CanonicalRefund`, `CanonicalCustomer`.
- **Payment Identity**: Must implement `PaymentIdentityMap` linking internal IDs (`pmt_internal_...`) with provider-native IDs (`pay_...`, `pi_...`, `ps_...`).

### 2.3 Financial Mutation & Risk Points
- **Unchecked API Assumptions**: Never assume HTTP 200 = money settled.
- **Ambiguous Timeout States**: Network drop / gateway 5xx must transition to `UNKNOWN` $\rightarrow$ `RECONCILE` (lookup provider truth) before taking any further action.
- **Webhook Replay & Tampering**: Must enforce HMAC-SHA256 signature verification and event-ID deduplication before state mutation.
- **Floating Point Arithmetic**: All monetary quantities must use integer minor units (paise / cents) or exact decimals.

---

## 3. Migration Plan: "One Agent, Two Environments"

```
                         ┌────────────────────────────┐
                         │       ULTRON CORE          │
                         │                            │
                         │ AgentLoop / FSM            │
                         │ Payment Intelligence       │
                         │ LLM Intelligence           │
                         │ Policy / Risk / NEV        │
                         │ Action Decision Authority  │
                         │ Episodic Memory            │
                         └──────────────┬─────────────┘
                                        │
                              PaymentEnvironment
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
               RealProviderEnvironment       SyntheticWorldEnvironment
                         │                             │
             ┌───────────┼───────────┐                 │
             ▼           ▼           ▼                 ▼
          Razorpay     Stripe      Adyen              SWU
           (TEST)      (TEST)      (TEST)          (Simulation)
```

### 3.1 Files to Create (New Architecture)
- `backend/providers/`: `base.py`, `models.py`, `registry.py`, `capabilities.py`, `errors.py`, `health.py`, `environment.py`
- `backend/providers/razorpay/`: `client.py`, `adapter.py`, `mapper.py`, `webhook.py`, `capabilities.py`, `errors.py`, `health.py`
- `backend/providers/stripe/`: `client.py`, `adapter.py`, `mapper.py`, `webhook.py`, `capabilities.py`, `errors.py`, `health.py`
- `backend/providers/adyen/`: `client.py`, `adapter.py`, `mapper.py`, `webhook.py`, `capabilities.py`, `errors.py`, `health.py`
- `backend/integrations/webhooks/`: `router.py`, `verifier.py`, `normalizer.py`, `deduplicator.py`, `event_store.py`, `dispatcher.py`
- `backend/reconciliation/`: `engine.py`, `state_machine.py`, `provider_fetch.py`, `mismatch.py`, `policy.py`, `scheduler.py`
- `backend/missions/`: `payment_mission.py`, `lifecycle.py`, `persistence.py`
- `backend/comms/`: `dispatcher.py`, `policy.py`, `templates.py`, `email.py`, `sms.py`, `whatsapp.py`
- `backend/environments/`: `environment.py`, `synthetic.py`, `real_provider.py`, `registry.py`
- `backend/safety/production_gate.py`: Fail-closed execution gate (`production_enabled=False` by default)
- `backend/readiness/`: `checks.py`, `report.py`, `levels.py`
- `backend/evidence/real_to_swu.py`: Sanitized fixture generator

---

## 4. Acceptance Invariants Checklist
- [x] Baseline 390 tests verified passing
- [x] Non-authoritative LLM boundary strictly maintained
- [x] Zero floating-point arithmetic on monetary balances (minor units / decimal)
- [x] SWU preserved as research/counterfactual laboratory
- [x] Real execution plane isolated to TEST/SANDBOX environments
