# ULTRON v5.0 Sandbox Autonomous Mode

## 1. Autonomous Execution Safeguards
Under `SANDBOX_AUTONOMOUS` mode:
- Restricted strictly to provider test/sandbox keys (`rzp_test_...`, `sk_test_...`).
- Autonomous actions are strictly limited to non-financial mutation actions (`WAIT`, `RETRY`, `SEND_PAYMENT_LINK`).
- Rate limits, customer fatigue limits, and kill-switch checks are continuously active.
