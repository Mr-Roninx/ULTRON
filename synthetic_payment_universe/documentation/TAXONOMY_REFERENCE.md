# ULTRON Failure Taxonomy Reference Guide

## 1. Normalized Failure Categories
- **TRANSIENT**: System or issuer switch temporary inoperation (e.g. ISO 91, Timeout). Recoverable via temporal backoff / retry.
- **CUSTOMER_ACTION_REQUIRED**: Insufficient funds (ISO 51), expired credentials (ISO 14, 54), or 3DS auth issues. Recoverable via dynamic checkout link.
- **HARD_DECLINE**: Stolen or blocked card (ISO 41). Requires human finance intervention or mission stop.
- **LIMIT**: Velocity or withdrawal caps exceeded (ISO 61, 65). Recoverable via alternate authorized rail (e.g. UPI / Net Banking).
- **AMBIGUOUS**: Clearing pending or dropped webhooks. Requires active reconciliation inquiry (`RECONCILE`).

---

## 2. Root Cause Disambiguation Matrix
| Observed Code | Normalized Category | Possible Latent Root Causes (Hidden Oracle) | Recommended Action |
| :--- | :--- | :--- | :--- |
| **91** | `TRANSIENT` | `ISSUER_CORE_BANKING_REBOOT`, `SWITCH_NETWORK_INTERRUPTION`, `GATEWAY_INTERNAL_TIMEOUT` | `WAIT` or `RETRY` |
| **51** | `CUSTOMER_ACTION_REQUIRED` | `PAYDAY_TIMING_LAG`, `TEMPORARY_PREAUTH_HOLD`, `ACCOUNT_DRAINED` | `SEND_PAYMENT_LINK` |
| **14** | `CUSTOMER_ACTION_REQUIRED` | `CARD_EXPIRED`, `TOKEN_REVOKED`, `TYPO_IN_CARD_NUMBER` | `SWITCH_PERMITTED_RAIL` |
| **41** | `HARD_DECLINE` | `CARD_REPORTED_LOST`, `FRAUDULENT_CARD_BLOCK` | `ESCALATE` / `STOP` |
| **TO** | `TIMEOUT` | `INGRESS_LATENCY_SPIKE`, `GATEWAY_DEGRADATION` | `SWITCH_GATEWAY` |
| **AMBIGUOUS** | `AMBIGUOUS` | `WEBHOOK_DROPPED_IN_FLIGHT`, `ASYNCHRONOUS_CLEARING_LAG` | `RECONCILE` |
