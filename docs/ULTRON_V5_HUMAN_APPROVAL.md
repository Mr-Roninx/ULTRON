# ULTRON v5.0 Human Approval Mode

## 1. Approval Flow
- Agent analyzes payment failure and prepares proposed action (`APPLY_DISCOUNT`, `REFUND_PAYMENT`, `ESCALATE`).
- Action is placed in `PENDING_APPROVAL` queue.
- Operator explicitly approves or rejects via authenticated backend endpoints (`POST /human-approval/{id}/approve`).
- Frontend buttons never directly invoke external payment provider APIs.
