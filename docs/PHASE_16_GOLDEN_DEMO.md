# ULTRON v3.8 — Phase 16: Golden Demo Specification

## 1. Primary Golden Demo: Ananya Textiles
- **Scenario ID**: `DEMO_04_GATEWAY_CHAOS`
- **Customer**: Ananya Textiles Pvt Ltd (Segment: `B2B_ENTERPRISE`)
- **Payment Amount**: ₹24,700.00
- **Failure Code**: ISO 91 (`ISSUER_UNAVAILABLE`)

## 2. Interactive Execution Steps
```bash
python -m backend.demo.demo_runner --scenario DEMO_04_GATEWAY_CHAOS
```

### Flow
1. **World Setup**: Account seeded with ₹24,700 failed card payment.
2. **LLM Invocation #1**: Model reasons and proposes `[WAIT, RETRY_GATEWAY_A, SEND_PAYMENT_LINK]`.
3. **Deterministic NEV Ranking**: Action Authority selects `RETRY_GATEWAY_A` (₹10,926.49 expected yield).
4. **Execution & Wait**: Retry scheduled; agent enters `WAIT`.
5. **Chaos Injection**: At T+2h, Gateway A drops to 10% health.
6. **Wake & Replan**: Agent wakes, invalidates plan, and triggers `LLM INVOCATION #2`.
7. **Adaptive Resolution**: Alternate channel executed; outcome observed; episode recorded in memory.
