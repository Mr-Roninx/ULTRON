# ULTRON v5.0 Observability & Performance Tracking

## 1. Latency Decomposition
Independently measured latency metrics:
- `LLM Reasoning Latency`: Time elapsed in semantic hypothesis generation.
- `Provider API Latency`: External HTTP latency to payment gateway.
- `Webhook Ingestion Latency`: Time from HTTP arrival to normalized dispatch.
- `Reconciliation Latency`: Time to fetch and verify authoritative ledger status.
- `End-to-End Mission Latency`: Full elapsed time from failure ingestion to settlement.
