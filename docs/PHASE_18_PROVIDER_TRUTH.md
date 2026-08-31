# ULTRON v4.0 — Phase 18: Live Provider Truth & Failover Audit

## 1. Executive Summary
ULTRON enforces absolute transparency regarding LLM provider availability.
- **Configured Remote Provider**: `Qwen/Qwen3.8-2.4T-A95B:novita` via Hugging Face Router.
- **Failover Ladder**: `Hugging Face Router → Local Qwen → Safe Deterministic Policy`.
- **Status Classification**:
  - `AVAILABLE`: Live remote inference operational.
  - `CREDIT_EXHAUSTED`: HTTP 402 returned (Depleted monthly quota). Failover triggered seamlessly.
  - `RATE_LIMITED`: HTTP 429 returned.
  - `TIMEOUT`: Soft timeout (5s) or Hard timeout (10s) triggered.

---

## 2. Invariant
Under credit exhaustion, fallback execution output is never misrepresented as live Hugging Face generation. Recorded in `results/phase18/live_provider_truth.json`.
