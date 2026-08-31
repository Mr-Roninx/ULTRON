# ULTRON v5.0 Evidence Conflicts Log

## 1. Conflict Identification & Resolution Table

| Conflict ID | Documented Claim | Runtime Finding | Conflict Nature | Resolution / Corrected Truth |
| :--- | :--- | :--- | :--- | :--- |
| **CONF-01** | `Razorpay PROVIDER_SANDBOX_VERIFIED` | `RAZORPAY_KEY_ID` not in environment | Overstated external network claim | **Downgraded to `FIXTURE_ONLY (SANDBOX EMULATION)`** |
| **CONF-02** | `LLM_REASON: Qwen-2.5 LIVE` | `HF_TOKEN` not exported in environment | Neural model labeled when fallback ran | **Reconciled to `FALLBACK_VERIFIED`** |
| **CONF-03** | `204 ms Live API Latency` | Measured in synthetic emulation test harness | Test harness latency vs live internet | **Marked as `EMULATED_BENCHMARK`** |

---

## 2. Integrity Rule
All historical claims have been reconciled in [`results/phase20/reconciled/evidence_reconciliation.json`](file:///d:/Work%20Space/Project/Ultron/results/phase20/reconciled/evidence_reconciliation.json).
