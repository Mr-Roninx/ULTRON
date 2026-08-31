# ULTRON Build Progress

Autonomous Economic Control Plane for Failed-Payment Recovery on Razorpay.

---

## Build Order Status

- [x] **Feature 1: Event Fabric** (Completed)
- [x] **Feature 2: Perception** (Completed)
- [x] **Feature 3: Economic Reasoning** (Completed)
- [ ] **Feature 4: Recovery Market**
- [ ] **Feature 5: Action Authority**
- [ ] **Feature 6: Execution**
- [ ] **Feature 7: Truth Engine + Dashboard**

---

## Feature 3: Economic Reasoning — Summary

### What Was Built
1. **Mathematical Scoring Engine (`src/economics/scorer.ts`)**:
   - Implemented starter probability counterfactual tables:
     - `hard`: natural 0.02, intervention 0.02 ($\Delta = 0.00$)
     - `insufficient_funds`: natural 0.35, intervention 0.55 ($\Delta = 0.20$)
     - `expired_card`: natural 0.05, intervention 0.60 ($\Delta = 0.55$)
     - `generic_decline` / `do_not_honor`: natural 0.25, intervention 0.45 ($\Delta = 0.20$)
     - `bank_timeout`-type: natural 0.60, intervention 0.70 ($\Delta = 0.10$)
     - `unknown`: natural 0.10, intervention 0.10 ($\Delta = 0.00$)
   - Incremental probability computation: $\text{incremental\_prob} = \max(0, \text{intervention} - \text{natural})$.
   - Operational & Fatigue cost model:
     - Fixed delivery cost: 400 paise (₹4.00).
     - Non-linear customer fatigue penalty: 0 paise (attempt 1), 250 paise (attempt 2), 750 paise (attempt 3), $1500 + 500 \times (\text{attempt} - 4)$ paise (attempt 4+).
   - Expected Incremental Value Calculation:
     $$\text{IVEN} = \text{incremental\_prob} \times \text{amount\_paise} - \text{operational\_cost\_paise} - \text{fatigue\_cost\_paise}$$
   - Confidence evaluation:
     - `'low'`: `decline_type === 'unknown'` OR `attempt_count >= 3`
     - `'high'`: `decline_type === 'hard'` OR `bank_timeout`-type
     - `'medium'`: standard recoverable attempts 1-2.
2. **Persistence & Database Integration (`src/db/database.ts`)**:
   - `scores` table populated with exact schema fields.
   - Dynamic opportunity status updating (`pending` $\to$ `scored`).
3. **API & Data Access (`src/routes/opportunities.ts`)**:
   - `GET /opportunities/:id/score`: Returns complete mathematical breakdown with `_labels` metadata marking estimated probabilities.
   - `POST /opportunities/score-all`: Batch scoring endpoint for pipeline processing.

### What Was Verified
- **Hard Decline**: Incremental probability = 0.00, IVEN = -400 paise ($\le 0$).
- **Bank Timeout (High Natural Recovery)**: High natural recovery (0.60) yields small incremental lift (0.10) even for large ticket sizes (₹48,000 / ₹62,000), preventing wasteful capacity expenditure on payments that recover naturally.
- **Insufficient Funds Attempt 1**: Produces clear positive IVEN (+49,600 paise / ₹496.00).
- **Insufficient Funds Attempt 3**: Policy retry limit forces confidence to `'low'`.
- **API Endpoint Verification**: `GET /opportunities/:id/score` returns exact contract fields with model-estimated metadata tags.
- **Clean Typecheck**: `npx tsc --noEmit` passing with 0 errors.

### What Was Deferred (As per Specification)
- Greedy capacity allocation and shadow pricing (Feature 4: Recovery Market).
- Deterministic compliance veto gate (Feature 5: Action Authority).
