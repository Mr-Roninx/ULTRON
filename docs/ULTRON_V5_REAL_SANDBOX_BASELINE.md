# ULTRON v5.0 Real Sandbox Verification Baseline
**Document ID: ULTRON_V5_REAL_SANDBOX_BASELINE**  
**Date: 2026-08-29**  
**Status: COMPLETED (Forensic Audit Gate)**

---

## 1. Executive Summary
This document establishes the scientific forensic baseline for verifying the Real Execution Plane of **ULTRON v5.0**.

### Core Environment Classification Matrix:
- **`HF_TOKEN`**: Not configured (`LLM_FALLBACK_ACTIVE = True`)
- **`RAZORPAY_KEY_ID`**: Not configured in local environment (`EVIDENCE_CLASS = FIXTURE_AND_SANDBOX_EMULATION`)
- **`STRIPE_SECRET_KEY`**: Not configured in local environment (`EVIDENCE_CLASS = NOT_CONFIGURED / FIXTURE_ONLY`)
- **`ADYEN_API_KEY`**: Not configured in local environment (`EVIDENCE_CLASS = NOT_CONFIGURED / FIXTURE_ONLY`)
- **`SWU Engine`**: Fully active & verified (390 tests passed across SWU-1.0 to SWU-1.5)
- **`Provider Adapters`**: 18 unit, security, and E2E tests verified in `tests/providers/`

---

## 2. Test Baseline & Evidence Classification Mapping
| Component | Existing Tests | Evidence Class | Verified Execution Path |
| :--- | :--- | :--- | :--- |
| **SWU Core** | 390 tests | `SWU` | Persistent economic civilization, causal DAG, CRN, feedback loops |
| **Provider Contracts** | 3 tests | `FIXTURE` | Capability sets, registry discovery, adapter interfaces |
| **Monetary Models** | 2 tests | `FIXTURE` | Canonical payment integer minor units (paise/cents) |
| **Webhook Gateway** | 3 tests | `FIXTURE` | HMAC-SHA256 verification, event deduplication, canonical normalization |
| **Reconciliation** | 2 tests | `FIXTURE` | Direct external truth query, reconciliation-first error policy |
| **Provider Health** | 2 tests | `FIXTURE` | Latency EMA tracking, timeout detection, health telemetry |
| **Safety Gates** | 3 tests | `FIXTURE` | Production execution gate fail-closed, kill switch, shadow mode |
| **Security Hardening** | 1 test | `FIXTURE` | Forged signatures, SQL injection, balance mutations blocked |
| **E2E Payment Link** | 2 tests | `FIXTURE` | Payment link generation, simulated webhook settlement, ledger balance |

---

## 3. Strict Truth Invariants
1. We will **NEVER** claim live production execution.
2. We will **NEVER** label mocked or fixture responses as `PROVIDER_SANDBOX_VERIFIED` unless actual external network traffic occurred.
3. Every step in the 24-stage trace will be linked via `correlation_id` and hashed for tamper-proof verification.
4. Monetary integrity will strictly enforce:
   $$\text{Provider Minor Units} == \text{Canonical Minor Units} == \text{Reconciled Minor Units} == \text{Ledger Minor Units}$$
