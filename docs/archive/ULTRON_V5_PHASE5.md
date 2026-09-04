# ULTRON v5.0 — Phase 5: Planner, WAIT, WAKE, Plan Validation & Replanning

**Phase Objective**: Build ONLY the Planner, `WAIT`, `WAKE`, structured plan validation, and replanning engine. Demonstrate the full autonomous adaptation lifecycle: `FAILURE` $\to$ `PLAN` $\to$ `WAIT` $\to$ `ENVIRONMENT CHANGES` $\to$ `WAKE` $\to$ `PLAN INVALIDATED` $\to$ `REPLAN`.

---

## 1. Replanning Architecture ([`src/agents/replan_engine.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/replan_engine.ts))

The planning and replanning engine operates as a stateful, bounded feedback loop:

```
┌────────────────────────────────────────────────────────┐
│             Initial Plan Creation (v1)                 │
│         (Sets Explicit Validity Assumptions)           │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│               WAIT State (Suspended)                   │
│          (Awaiting Timer, Gateway Tick, or Poller)     │
└───────────────────────────┬────────────────────────────┘
                            │ Environment Degrades
                            ▼
┌────────────────────────────────────────────────────────┐
│               WAKE State (Resumed)                     │
│         (Evaluates Live Assumptions vs Environment)    │
└───────────────────────────┬────────────────────────────┘
                            │ Assumption Broken
                            ▼
┌────────────────────────────────────────────────────────┐
│            PLAN_INVALIDATED State                      │
│     (Marks Plan v1 INVALIDATED in `agent_plans`)       │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 REPLAN Engine                          │
│   (Consumes Replan Budget, Enforces Anti-Recursion)    │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             Revised Plan Creation (v2)                 │
│       (Selects Deferral / Revised Action Strategy)     │
└────────────────────────────────────────────────────────┘
```

---

## 2. Demonstrated Lifecycle Trace

| Step | State Machine State | Event / Environmental Condition | System Action |
| :--- | :--- | :--- | :--- |
| **1. Failure** | `TRIGGERED` $\to$ `OBSERVE` | Soft decline (`insufficient_funds`, amount: ₹2,500). | Initialized opportunity mission. |
| **2. Plan v1** | `PLAN` $\to$ `VALIDATE_PLAN` | Gateway health = $0.95$, Capacity = $5$. | Generated Plan v1 (`preferred_action='SEND_PAYMENT_LINK'`). |
| **3. Enter Wait** | `PROPOSE` $\to$ `WAIT_AUTHORITY` $\to$ `WAIT` | Suspended for execution window or timer. | Saved state in SQLite `agent_states` table. |
| **4. Environment Changes** | `WAIT` | Gateway health degrades to $0.40$ (below $0.75$ threshold). | External condition divergence detected. |
| **5. Wake** | `WAKE` | Wake tick triggered. | Agent wakes and re-evaluates active plan assumptions. |
| **6. Plan Invalidated** | `PLAN_INVALIDATED` | Assumption `gateway_health >= 0.75` failed ($0.40$). | Marked Plan v1 as `INVALIDATED`. |
| **7. Replan** | `REPLAN` $\to$ `PLAN` | Replan budget checked ($1 / 3$ consumed). | Synthesized Plan v2 (`preferred_action='WAIT'`, revised steps). |

---

## 3. Plan Validity Assumptions ([`src/agents/planner.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/planner.ts))

Every generated `AgentPlanRecord` contains structured, machine-checkable hypotheses:

```typescript
export interface PlanValidityAssumption {
  id: string;
  parameter: string; // 'gateway_health' | 'attempt_count' | 'capacity_available'
  condition: string; // '>=' | '<' | '>'
  expected_value: any;
  current_value: any;
  is_valid: boolean;
}
```

---

## 4. Safety & Loop Bounds Enforced

- **Hard Replan Budget**: Strictly limited to a maximum of 3 replans per mission (`max_replans = 3`). Exceeding this budget immediately aborts the mission or escalates to `HUMAN_REVIEW`.
- **Anti-Loop Protection**: `LoopGuard` computes plan step hashes to prevent oscillating back and forth between identical candidate plans.
- **Zero Financial Bypass**: Replanning only alters proposed strategies; all financial execution remains strictly gated behind Action Authority.

---

## 5. Test Verification Results

- **Replanning Lifecycle Tests (`test_agent_replanning.ts`)**: ✅ PASS (Demonstrated `FAILURE` $\to$ `PLAN` $\to$ `WAIT` $\to$ `ENVIRONMENT CHANGES` $\to$ `WAKE` $\to$ `PLAN INVALIDATED` $\to$ `REPLAN`).
- **Master Agent Suite (`npm run test:agent`)**: **20 PASSED / 0 FAILED**.
- **Deterministic Core Hardening (`npm run test:core`)**: **5 PASSED / 0 FAILED**.
- **Hardened Infrastructure (`npm run test:infra`)**: **3 PASSED / 0 FAILED**.
