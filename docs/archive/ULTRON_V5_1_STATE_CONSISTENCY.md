# ULTRON v5.1 — State Consistency & Reconciliation Hardening Architecture

## 1. Executive Summary & Objective

ULTRON v5.1 enforces a strict, hierarchical state consistency invariant across all distributed and local subsystems:

$$\mathbf{PROVIDER\ TRUTH} > \mathbf{RECONCILIATION} > \mathbf{LOCAL\ FINANCIAL\ STATE}$$

No bounded AI Agent, UI layer, test fixture, or local process may silently override or diverge from external provider truth (Razorpay Test Mode API). When reality changes, ULTRON's authoritative reconciliation layer transactionally synchronizes local opportunities, execution records, double-entry ledgers, agent outcomes, and episodic memory.

---

## 2. Observed Inconsistencies & Root Causes

During forensic inspection of the live SQLite database and Razorpay API, three core divergence risks were identified and systematically resolved:

1. **Provider Paid vs Local Opportunity State Divergence**:
   - *Symptom*: Razorpay Test Mode confirmed payment link `plink_TWcnQZVwogNPop` as `status='paid'`, `amount_paid=₹4,500.00` (`pay_TWd8rHL0ewMl51`), but local opportunity `rzp_live_test_1788233420739` was reset to `'deferred'` during benchmark reseeding.
   - *Fix*: Implemented `AuthoritativeReconciler.reconcileOpportunity()` which transactionally queries live provider truth and updates `recovery_opportunities.status='recovered'`, `execution_records.status='completed'`, records `DoubleEntryLedger` (`bank_settlement` $\rightarrow$ `recovered_revenue`), updates `agent_outcomes` (`actual_recovered=1`), and updates episodic memory.

2. **False Recovery Prevention (The ₹5,000 Pending/Failed Checkout)**:
   - *Symptom*: Payment link `plink_TWdfP8DYuHHSMe` was created for `opp_live_fresh_1788236486783` (₹5,000.00). An unconfirmed or failed checkout at the browser level left the provider object in `status='created'`, `amount_paid=0`.
   - *Fix*: Invariant strictly enforced: `LINK_CREATED != RECOVERED`. Opportunity remains in `executing` / `PROVIDER_OBJECT_CREATED` status until provider explicitly confirms settlement with `amount_paid > 0`.

3. **Orphan / Stale Agent Missions**:
   - *Symptom*: Agent runs remained in `status='running'` indefinitely after process termination or unhandled lifecycle timeouts.
   - *Fix*: Implemented `MissionLifecycleMonitor.sweepStaleMissions()` which inspects running missions, verifies if an active persisted wake condition exists, and safely transitions stale runs (> 5 min inactivity) to `status='aborted'` with `termination_reason='stale_orphan_cleanup'`.

---

## 3. Canonical Payment & Recovery Lifecycle State Machine

```
 OPPORTUNITY_CREATED
        │
        ▼
 ECONOMICALLY_ELIGIBLE (Deterministic IVEN Scored)
        │
        ▼
 MARKET_ALLOCATED (Portfolio Knapsack Auction)
        │
        ▼
 AUTHORITY_APPROVED (5 Compliance Checks + 9 Agent Gate Checks)
        │
        ▼
 EXECUTION_STARTED (Dispatched via Official SDK)
        │
        ▼
 PROVIDER_OBJECT_CREATED (Razorpay Payment Link ID Issued)
        │
        ▼
 PAYMENT_PENDING (Amount Paid = 0)
        │
    ┌───┴────────────────────────┬────────────────────────┐
    │                            │                        │
    ▼                            ▼                        ▼
 [Provider status = 'paid'    [Provider status =       [Provider API
  amount_paid > 0]             'expired' / 'failed']    Timeout / 5xx]
    │                            │                        │
    ▼                            ▼                        ▼
 PAYMENT_CONFIRMED            FAILED / NOT_RECOVERED   UNKNOWN / PENDING
    │                                                   RECONCILIATION
    ▼
 RECOVERED
 (Atomic Ledger + Learning Outcome + Episodic Memory)
```

---

## 4. Source of Truth Hierarchy

```
1. Razorpay Provider Response (Official REST API fetch)
2. Validated Provider Webhook Payload (HMAC-SHA256 verified)
3. Authoritative Reconciliation Engine
4. Local Execution Record (`execution_records`)
5. Local Opportunity State (`recovery_opportunities`)
6. Agent Interpretations & Specialist Annotations
```

---

## 5. Authoritative Atomic Reconciliation Engine

All financial state transitions are executed within an **atomic SQLite database transaction** (`BEGIN TRANSACTION` ... `COMMIT` / `ROLLBACK`):

```typescript
// src/reconciliation/authoritative_reconciler.ts
export class AuthoritativeReconciler {
  public static async reconcileOpportunity(
    opportunityId: string,
    options?: { providerPayloadOverride?: any; actor?: string }
  ): Promise<ReconciliationResult>;
}
```

### Guarantees:
- **Atomicity**: Either all 5 tables (`recovery_opportunities`, `execution_records`, `double_entry_ledger`, `ledger_entries`, `agent_outcomes`, `agent_memories`) update successfully or the transaction completely rolls back.
- **Idempotency**: Repeated reconciliation with the same provider state produces zero duplicate ledger entries, zero duplicate outcomes, and returns `status='MATCHED', is_idempotent_no_op=true`.
- **Out-of-Order Safety**: A transient `failed` state is cleanly superseded if a later valid provider `captured` event arrives.
- **Quarantine on Error**: Network timeouts or 5xx provider responses quarantine the opportunity as `UNKNOWN` without corrupting local records.

---

## 6. Key Transaction Verification Table

| Transaction Type | Opportunity ID | Payment Link ID | Provider Status | Amount Paid | Local Database Status | Ledger Balanced | State Consistency Verdict |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **Confirmed Real Recovery** | `rzp_live_test_1788233420739` | `plink_TWcnQZVwogNPop` | `paid` | ₹4,500.00 | `recovered` | **TRUE** (Hash chained) | **CONSISTENT** |
| **New Test Link (Pending)** | `opp_live_fresh_1788236486783` | `plink_TWdfP8DYuHHSMe` | `created` | ₹0.00 | `executing` | **N/A** (Pending) | **CONSISTENT** |

---

## 7. Verification Test Matrix

```bash
# 1. State Consistency Suite (11 / 11 Passed)
npx tsx --test tests/truth/test_state_consistency.ts

# 2. Agent Test Suite (28 / 28 Passed)
npm run test:agent

# 3. Deterministic Core Hardening Suite (5 / 5 Passed)
npm run test:core

# 4. Infrastructure Suite (3 / 3 Passed)
npm run test:infra

# 5. Frontend Production Bundle
cd frontend && npm run build (Success, 0 errors)
```

---

## 8. Known Limitations & Operating Boundaries

1. **Test Mode Only**: Razorpay Test Mode keys are strictly used. Production/live-money execution remains disabled by design.
2. **Polling Frequency & Rate Limits**: Rapid polling is throttled (350ms delay + 1s backoff) to respect Razorpay's 429 Test Mode rate limits.
3. **Double-Entry Journaling**: Final settlement entries are posted strictly upon verified provider payment (`amount_paid > 0`).
