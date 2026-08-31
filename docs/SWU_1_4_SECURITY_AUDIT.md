# ULTRON-SWU-1.4 Security Audit

## 1. Safety Guardrails & Invariants
- **Non-Financial Authority**: LLM never mutates balances or issues transfers.
- **Fail-Closed Action Guard**: Unpermitted actions (`DROP TABLE`, `UPDATE_BALANCE`) are rejected instantly.
- **Recursive Observation Firewall**: Deeply scans all payload dictionaries, stripping all oracle keys and raising `FutureInformationLeakageError` on any $timestamp > t$.
