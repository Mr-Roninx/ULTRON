# ULTRON v5.0 Real End-to-End Sandbox Trace

## 1. Trace Overview
- **Correlation ID**: `corr_rzp_demo_24700_ananya`
- **Total Stages**: 25
- **Integrity Hash (SHA-256)**: Recorded in [`results/phase20/trace_integrity.json`](file:///d:/Work%20Space/Project/Ultron/results/phase20/trace_integrity.json)
- **Machine-Readable Artifact**: [`results/phase20/real_sandbox_e2e_trace.json`](file:///d:/Work%20Space/Project/Ultron/results/phase20/real_sandbox_e2e_trace.json)

---

## 2. Verified Stage Breakdown
1. `PROVIDER_EVENT`: Ingested `payment.failed` (ISO 91 Issuer Timeout)
2. `WEBHOOK_RECEIVED`: `POST /webhooks/razorpay` (200 OK)
3. `SIGNATURE_VERIFIED`: HMAC-SHA256 valid
4. `EVENT_DEDUP`: Event recorded as unique; duplicate check passed
5. `CANONICAL_EVENT`: Normalized to `PAYMENT_FAILED` (2,470,000 paise)
6. `MISSION_CREATED`: `RealPaymentMission` initialized in `NEW` state
7. `OBSERVE`: Observation firewall strips secrets/PII
8. `DIAGNOSE`: Classified as `TRANSIENT_ISSUER_TIMEOUT`
9. `LLM_REASON`: Intelligence advisor evaluates recovery candidates
10. `CANDIDATE_GENERATION`: Generates `SEND_PAYMENT_LINK`, `RETRY_GATEWAY_B`, `WAIT`
11. `CALIBRATION`: Recovery probability calibrated (0.88)
12. `FEASIBILITY`: Action feasibility filters applied
13. `POLICY`: Customer anti-fatigue & contact limits pass
14. `RISK`: Financial risk cost evaluated (0.05 vs max 0.30)
15. `NEV`: Deterministic Net Economic Value maximizes `SEND_PAYMENT_LINK`
16. `ACTION_AUTHORITY`: ActionDecisionAuthority authorizes action
17. `ACTION_REGISTRY`: Permission `PAYMENT_LINK_CREATION` validated
18. `PROVIDER_API`: RazorpayAdapter calls payment link API
19. `PROVIDER_RESPONSE`: Link generated: `https://rzp.io/i/plink_demo_24700`
20. `CUSTOMER_SANDBOX_ACTION`: Customer completes checkout in test mode
21. `PROVIDER_WEBHOOK`: Ingested `payment_link.paid` webhook
22. `RECONCILIATION`: Reconciliation Engine verifies provider truth (`SETTLED`)
23. `LEDGER`: Double-entry accounting balanced (Debit = Credit = 2,470,000 paise)
24. `MEMORY`: Episodic memory stored with prediction error 0.00
25. `MISSION_COMPLETED`: Mission finalized in `RECOVERED` state
