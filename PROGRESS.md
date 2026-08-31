# ULTRON Build Progress

Autonomous Economic Control Plane for Failed-Payment Recovery on Razorpay.

---

## Build Order Status

- [x] **Feature 1: Event Fabric** (Completed)
- [x] **Feature 2: Perception** (Completed)
- [x] **Feature 3: Economic Reasoning** (Completed)
- [x] **Feature 4: Recovery Market** (Completed)
- [ ] **Feature 5: Action Authority**
- [ ] **Feature 6: Execution**
- [ ] **Feature 7: Truth Engine + Dashboard**

---

## Feature 4: Recovery Market (Allocation) — Summary

### What Was Built
1. **Recovery Market Allocator (`src/market/allocator.ts`)**:
   - Greedy portfolio capacity allocator enforcing configurable limits (`MAX_LINKS_PER_RUN`, default 5).
   - Pre-ranking filter: Opportunities with `confidence === 'low'` or non-positive IVEN ($\le 0$) route immediately to `decision = 'ABSTAIN'` (`rank_in_batch = 0`) without consuming recovery capacity.
   - IVEN Ranking: Eligible opportunities sorted strictly by expected incremental value descending.
   - Capacity Cutoff & Shadow Price:
     - Top $K$ items receive `decision = 'ACT'`.
     - Remaining items receive `decision = 'WAIT'`.
     - $\text{Shadow Price} = \text{IVEN of the marginal } (K\text{-th}) \text{ accepted opportunity}$.
     - Stamped onto all decisions in the run with detailed human-readable rationales.
2. **Database Integration (`src/db/database.ts`)**:
   - `allocation_decisions` table storing `opportunity_id, decision [ACT|WAIT|ABSTAIN], rank_in_batch, shadow_price_paise_at_decision, reason`.
   - Opportunity status transitions (`allocated`, `deferred`, `abstained`).
3. **Market API Endpoints (`src/routes/market.ts`)**:
   - `GET /market/run?capacity=N` and `POST /market/run`: Runs portfolio allocation with dynamic capacity and returns structured rankings and shadow prices.
   - `GET /market/decisions`: Returns current allocation decisions.

### What Was Verified
- **Cap = 5 Allocation**: Exactly 5 opportunities allocated `ACT`. Hard declines and low-confidence retry-cap cases excluded to `ABSTAIN`. Shadow price computed at ₹2,396.00.
- **Cap = 3 Shift (Core Demo Moment)**:
  - Exactly 3 opportunities allocated `ACT`.
  - Opportunities ranked #4 (`synth_07_high_val_enterprise`) and #5 (`synth_12_mid_val_retainer`) shifted from `ACT` to `WAIT`.
  - Reasons on deferred items explicitly cite the higher marginal cutoff: `"deferred — below this run's marginal value of ₹6,196.00 (rank #4 vs cap 3)"`.
  - Shadow price rose from ₹2,396.00 to ₹6,196.00.
- **TypeScript Integrity**: `npx tsc --noEmit` passing with 0 errors.

### What Was Deferred (As per Specification)
- Deterministic compliance veto gate (Feature 5: Action Authority).
- Real payment link generation (Feature 6: Execution).
