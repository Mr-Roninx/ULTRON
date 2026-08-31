# ULTRON-SWU-1.5 Forensic Baseline & Architecture Plan
**Document ID: SWU_1_5_BASELINE_FORENSIC**  
**Date: 2026-08-29**  
**Status: COMPLETED (Phase A Gate)**

---

## 1. Executive Summary
This document establishes the verified baseline for transitioning from **ULTRON-SWU-1.4 (Emergent Population Economy)** to **ULTRON-SWU-1.5 (Economic Adversarial Reality & Causal Attribution Engine)**.

### Baseline Status:
- **Test Suite**: 366 tests passed, 0 failures, 0 regressions.
- **Persistence**: SQLite WAL database with relational integrity, double-entry ledger, and streaming chunk generation.
- **Temporal Engine**: Priority queue ordered by `(timestamp, sequence_index)`.
- **Causal Architecture**: Structural Causal Model DAG, Common Random Numbers, 5-branch world forking.
- **Firewall & Security**: Recursive observation firewall blocking future timestamps and latent variables.
- **Action Authority**: ActionRegistry and ActionGuard fail-closed; LLM possesses 0 direct financial authority.

---

## 2. Core Evolution from SWU-1.4 to SWU-1.5
In SWU-1.4, payment demand emerged organically and feedback loops A–F were modeled.
In SWU-1.5:
1. **Adversarial Interventions**: Unnecessary outreach induces contact fatigue, opt-out, and churn.
2. **Natural Recovery Competition**: Counterfactual natural recovery is measured; if payment self-heals, ULTRON receives ₹0 incremental credit.
3. **Gateway Externalities**: Switching traffic into an already-loaded gateway causes cross-merchant congestion.
4. **Long-Term LTV Tracking**: 30-day, 90-day, and 365-day repeat revenue is modeled; aggressive dunning that recovers ₹5,000 today but destroys ₹150,000 in future LTV is penalized.
5. **Multi-Tier Attribution**: Direct, Probable, Downstream, Non-Incremental, and Negative Externality tiers.
6. **11 Competing Policies**: Evaluates bad policies (`ALWAYS_RETRY`, `AGGRESSIVE_DUNNING`, `ALWAYS_SWITCH_GATEWAY`) alongside standard baselines.
