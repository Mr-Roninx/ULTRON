# ULTRON v5.0 LLM & Provider Boundary Isolation

## 1. Absolute Demarcation
- The LLM functions strictly as a semantic diagnostic advisor.
- The LLM has **zero direct access** to:
  - Razorpay API keys or webhook secrets
  - Outbound HTTP clients
  - Action execution without `ActionDecisionAuthority` and `ActionRegistry`
  - Internal database or ledger tables
- When `HF_TOKEN` is absent, the deterministic local fallback operates cleanly with zero hallucination.
