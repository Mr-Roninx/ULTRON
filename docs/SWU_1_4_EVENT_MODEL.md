# ULTRON-SWU-1.4 Event Model

## 1. Micro-Event Architecture
- Ordered by `(timestamp, sequence_index)` ensuring total determinism.
- Types: `PAYMENT_INITIATED`, `PAYMENT_AUTHORIZED`, `PAYMENT_FAILED`, `RETRY`, `PAYMENT_LINK_SENT`, `CUSTOMER_RESPONSE`, `GATEWAY_CONGESTED`, `MACRO_SHOCK`.
- Replay: Reconstructs state bit-for-bit via SHA-256 state hashes.
