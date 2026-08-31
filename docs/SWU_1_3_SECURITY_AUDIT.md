# ULTRON-SWU-1.3 Security Audit

## 1. Security Defenses & Invariants
- **Non-Financial Authority Invariant**: The LLM generates candidate semantic signals; financial mutation occurs only through `CivilizationDoubleEntryLedger`.
- **ActionRegistry Validation**: Unpermitted actions (`DROP TABLE`, `TRANSFER_MONEY`, `UPDATE_BALANCE`) fail-closed.
- **Lookahead & Oracle Protection**: `CivilizationObservationFirewall` strictly rejects future timestamps and strips latent variables.
- **Agent Capacity Guard**: Prevents contact abuse by enforcing customer contact rate limits.
