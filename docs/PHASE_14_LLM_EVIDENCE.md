# ULTRON v3.6 — PHASE 14 LLM EVIDENCE REPORT
## Real LLM Invocation & Candidate Influence Audit

---

## 1. Real LLM Provider Execution
- **Active Provider**: `HuggingFace/Qwen/Qwen2.5-72B-Instruct`
- **Configured Model**: `Qwen/Qwen2.5-72B-Instruct`
- **Execution Success**: `True`
- **Fallback Engaged**: `False`
- **Inference Latency**: `5024.28 ms`
- **Real LLM Flag**: `True`

---

## 2. LLM Candidate Influence Metrics
- **Mean Candidate Novelty Rate**: `0.00%` (Proportion of LLM proposals novel to deterministic space)
- **LLM Decision Influence Rate**: `100.00%` (Scenarios where LLM candidates modified the evaluated action set)

### Scenario Influence Breakdown
| Scenario ID | LLM Preferred | Deterministic Selected | Novelty Rate | Decision Altered |
| :--- | :--- | :--- | :--- | :--- |
| `SCEN_1_TRANSIENT` | `SEND_PAYMENT_LINK` | `RETRY_GATEWAY_A` | `0.0%` | `True` |
| `SCEN_2_LIQUIDITY` | `SEND_PAYMENT_LINK` | `SEND_PAYMENT_LINK` | `0.0%` | `True` |
| `SCEN_3_CREDENTIAL` | `SEND_PAYMENT_LINK` | `ESCALATE` | `0.0%` | `True` |
| `SCEN_4_GATEWAY_DEGRADATION` | `SEND_PAYMENT_LINK` | `SEND_MESSAGE` | `0.0%` | `True` |
| `SCEN_5_AMBIGUOUS_STATE` | `SEND_PAYMENT_LINK` | `RECONCILE` | `0.0%` | `True` |
| `SCEN_6_MIXED_EXPOSURE` | `SEND_PAYMENT_LINK` | `SEND_MESSAGE` | `0.0%` | `True` |
