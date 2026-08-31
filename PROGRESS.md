# ULTRON Build Progress

Autonomous Economic Control Plane for Failed-Payment Recovery on Razorpay.

---

## Build Order Status

- [x] **Feature 1: Event Fabric** (Completed)
- [x] **Feature 2: Perception** (Completed)
- [ ] **Feature 3: Economic Reasoning**
- [ ] **Feature 4: Recovery Market**
- [ ] **Feature 5: Action Authority**
- [ ] **Feature 6: Execution**
- [ ] **Feature 7: Truth Engine + Dashboard**

---

## Feature 2: Perception — Summary

### What Was Built
1. **Perception Normalization Engine (`src/perception/normalizer.ts`)**:
   - Deterministic taxonomy classification (`classifyDeclineTaxonomy`):
     - **Hard**: `stolen_card`, `lost_card`, `pickup_card`, `restricted_card`, `card_stolen_lost`, `BAD_REQUEST_PAYMENT_CARD_STOLEN_OR_LOST`
     - **Soft**: `insufficient_funds`, `expired_card`, `generic_decline`, `do_not_honor`, `bank_gateway_timeout`, `network_timeout`, `payment_authentication_failed`, `transaction_not_permitted`, `limit_exceeded`, `BAD_REQUEST_PAYMENT_INSUFFICIENT_FUNDS`, `BAD_REQUEST_PAYMENT_CARD_EXPIRED`
     - **Unknown**: Fallback for any unmapped code without throwing errors.
   - Normalization pipeline (`normalizeOpportunity`):
     - Maps raw payment entities into clean fields (`reason_code`, `decline_type`, `attempt_count`, `customer_id`, `customer_trust_score`, `amount_paise`, `currency`, `raw_payload_ref`).
2. **Customers Table & Trust Scoring (`src/db/database.ts`)**:
   - `customers` table (`id`, `trust_score`, `created_at`, `updated_at`).
   - Default trust score of `0.65` automatically assigned for unseen customers upon ingestion.
   - Dynamic attempt count computation (`countPriorAttempts`) calculating sequential failures per customer/order context.
3. **Pipeline Ingestion Integration (`src/webhooks/razorpay.ts`)**:
   - Automatic execution of Perception normalization directly inside the webhook ingestion path.
4. **Enhanced Opportunities API (`src/routes/opportunities.ts`)**:
   - `GET /opportunities/:id` returns normalized opportunity, customer profile with trust score, and ledger audit trail.

### What Was Verified
- **Taxonomy Unit Rules**: All hard decline codes classified as `hard`, all soft codes classified as `soft`, and unmapped codes classified as `unknown`.
- **15 Seeded Opportunities**: 100% classification accuracy against the taxonomy contract.
- **Unmapped Error Code Resiliency**: Unmapped exotic code (`unmapped_custom_issuer_code_999`) safely stored as `decline_type=unknown` without exceptions.
- **Default Trust Score**: Unseen customer automatically receives `0.65` trust score.
- **API Inspection**: `GET /opportunities/:id` verified with structured JSON return.
- **TypeScript Integrity**: `npx tsc --noEmit` clean with 0 errors.

### What Was Deferred (As per Specification)
- Probability scoring (Feature 3: Economic Reasoning).
- Portfolio market allocation (Feature 4: Recovery Market).
