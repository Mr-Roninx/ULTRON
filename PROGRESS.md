# ULTRON Build Progress

Autonomous Economic Control Plane for Failed-Payment Recovery on Razorpay.

---

## Build Order Status

- [x] **Feature 1: Event Fabric** (Completed)
- [ ] **Feature 2: Perception**
- [ ] **Feature 3: Economic Reasoning**
- [ ] **Feature 4: Recovery Market**
- [ ] **Feature 5: Action Authority**
- [ ] **Feature 6: Execution**
- [ ] **Feature 7: Truth Engine + Dashboard**

---

## Feature 1: Event Fabric — Summary

### What Was Built
1. **Node.js + TypeScript + Express Backend**:
   - `src/server.ts`: Express application configured with raw body capture for cryptographic signature verification.
   - `src/webhooks/razorpay.ts`: Webhook ingestion pipeline with HMAC SHA256 signature verification (`verifyWebhookSignature`), decline classification (`classifyDeclineType`), deduplication by Razorpay event ID and payment ID, and audit trail ledger entry recording.
   - `src/routes/opportunities.ts`: `GET /opportunities` and `GET /opportunities/:id` endpoints providing access to all ingested opportunities and ledger trails.
   - `src/types/index.ts`: Strict schema types conforming to the ULTRON contract.
2. **Zero-Setup SQLite Persistence (`src/db/database.ts`)**:
   - `recovery_opportunities` table matching exact field definitions:
     `id, source [real|synthetic], amount_paise, currency, reason_code, decline_type [hard|soft|unknown], attempt_count, customer_id, customer_trust_score, created_at, status [pending|scored|allocated|deferred|blocked|abstained|executing|recovered|not_recovered], razorpay_event_id, raw_payload_ref`
   - `scores`, `allocation_decisions`, `authority_checks`, `execution_records`, `ledger_entries` initialized with schema constraints and foreign keys.
3. **15 Synthetic Test Scenarios (`scripts/seed_synthetic.ts`)**:
   - `synth_01_stolen_card`: Hard decline (stolen/lost card), ₹4,500, attempt 1
   - `synth_02_insufficient_funds_att1`: Soft decline (insufficient funds), ₹2,500, attempt 1
   - `synth_03_retry_cap_exceeded`: Soft decline at retry cap, ₹1,800, attempt 3
   - `synth_04_expired_card`: Hard decline (expired card), ₹3,200, attempt 1
   - `synth_05_ambiguous_soft_att2`: Ambiguous soft decline (transaction not permitted), ₹5,000, attempt 2
   - `synth_06_bank_timeout_high_nat`: Bank gateway timeout with high natural recovery, ₹1,200, attempt 1
   - `synth_07` to `synth_15`: Mid and high-value pairs (₹1,500 to ₹95,000) for portfolio capacity competition testing.
4. **Real Razorpay Test Mode Spike (`scripts/real_razorpay_spike.ts`)**:
   - Uses official Razorpay Node SDK with test keys (`RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`).
   - Creates a real test order in Razorpay (`order_TWKMwV4tv5ayA7`) and ingests real failed payment event (`pay_mth1dfa7_0mr3`) signed with `RAZORPAY_WEBHOOK_SECRET`.

### What Was Verified
- **HMAC Signature Rejection**: `POST /webhooks/razorpay` with forged/invalid signature returned `400 Bad Request`.
- **Valid Webhook Ingestion**: `payment.failed` event ingested with `source='real'`, `status='pending'`, correct decline type and paise amount.
- **Idempotency & Deduplication**: Replaying identical webhook payload returned `200 OK` with `{ received: true, deduplicated: true }` without creating duplicate database rows.
- **Unified Opportunities API**: `GET /opportunities` returned both real and synthetic rows (17 rows total).
- **TypeScript Compilation**: Clean typecheck with `npx tsc --noEmit`.

### What Was Deferred (As per Specification)
- Scoring, allocation, authority checks, payment link execution, and dashboard UI (reserved for Features 2–7).
