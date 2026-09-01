# ULTRON v5.0 — Phase 8: Specialist Capabilities & Orchestrator Integration

**Phase Objective**: Implement all 5 specialist agent capabilities (Perception Agent, Strategy Agent, Outreach Agent, Compliance Copilot, Merchant Copilot) coordinated through the Master Orchestrator, with strict permission enforcement ensuring zero direct financial execution and draft/review-only outreach governance.

---

## 1. Specialist Delegation Architecture ([`src/agents/orchestrator.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/orchestrator.ts))

All specialist capabilities are orchestrated via the central mission coordinator:

```
┌────────────────────────────────────────────────────────┐
│                   Agent Orchestrator                   │
│        (21-State Autonomous Mission Coordinator)       │
└───────────────────────────┬────────────────────────────┘
                            │ Delegates Tasks
                            ▼
┌────────────────────────────────────────────────────────┐
│               Specialist Intelligence Layer            │
├───────────────────────────┬────────────────────────────┤
│ 1. Perception Agent       │ • Semantic decline analysis│
│                           │ • Urgency & risk scoring   │
├───────────────────────────┼────────────────────────────┤
│ 2. Strategy Agent         │ • Empirical calibration    │
│                           │ • Strategy proposals (N≥30)│
├───────────────────────────┼────────────────────────────┤
│ 3. Outreach Agent         │ • Multi-channel drafts     │
│                           │ • PENDING_REVIEW only      │
├───────────────────────────┼────────────────────────────┤
│ 4. Compliance Copilot     │ • Forensic 'Why?' audit    │
│                           │ • Reads stored records only│
├───────────────────────────┼────────────────────────────┤
│ 5. Merchant Copilot       │ • Market capacity queries  │
│                           │ • Gateway health insights  │
└───────────────────────────┴────────────────────────────┘
                            │ Mandatory Tool Invocation
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Agent Authority Gate                   │
│         * BLOCKS FINANCIAL_WRITE / EXECUTE *           │
└────────────────────────────────────────────────────────┘
```

---

## 2. Implemented Specialist Capabilities

### 1. Perception Agent ([`src/agents/specialists/perception_agent.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/specialists/perception_agent.ts))
- Evaluates raw decline codes, past payment attempts, and customer history.
- Produces `PerceptionAnnotationRecord` containing `failure_intent`, `customer_urgency_score`, and `merchant_risk_score`.
- Enforces hard decline override: fraud/stolen codes immediately assign `risk_score = 0.95`, `urgency_score = 0.1`.

### 2. Strategy Agent ([`src/agents/specialists/strategy_agent.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/specialists/strategy_agent.ts))
- Evaluates empirical recovery performance against baseline models.
- Generates `create_strategy_proposal` records when empirical evidence threshold ($N \ge 30$) is satisfied.

### 3. Outreach Agent ([`src/agents/specialists/outreach_agent.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/specialists/outreach_agent.ts))
- Drafts personalized customer messages across `SMS`, `WHATSAPP`, and `EMAIL`.
- **Draft/Review Only**: Emits records with status strictly set to `PENDING_REVIEW`.
- **Mandatory Compliance Footer**: Attaches opt-out and merchant identity footer to every draft.
- **Zero Direct Dispatch**: Prohibited from making direct messaging or communication dispatch calls.

### 4. Compliance Copilot ([`src/agents/specialists/compliance_copilot.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/specialists/compliance_copilot.ts))
- Answers forensic audit questions by reading stored database tables (`recovery_opportunities`, `scores`, `allocation_decisions`, `authority_checks`, `ledger_entries`).
- Formulates structured 3-part explanations without generating ungrounded rationales.

### 5. Merchant Copilot ([`src/agents/specialists/merchant_copilot.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/specialists/merchant_copilot.ts))
- Answers operator queries regarding recovery market capacity, active shadow prices, and live Razorpay gateway health metrics.

---

## 3. Safety & Permission Governance

| Specialist | Allowed Permissions | Blocked Permissions | Financial Authority Status |
| :--- | :--- | :--- | :--- |
| **Perception Agent** | `READ`, `ANALYZE`, `PROPOSE` | `FINANCIAL_WRITE`, `EXECUTE` | ✅ Zero financial authority |
| **Strategy Agent** | `READ`, `ANALYZE`, `PROPOSE` | `FINANCIAL_WRITE`, `EXECUTE` | ✅ Zero financial authority |
| **Outreach Agent** | `READ`, `ANALYZE`, `PROPOSE` | `FINANCIAL_WRITE`, `EXECUTE` | ✅ Draft / Review only |
| **Compliance Copilot** | `READ` | `FINANCIAL_WRITE`, `EXECUTE` | ✅ Zero financial authority |
| **Merchant Copilot** | `READ` | `FINANCIAL_WRITE`, `EXECUTE` | ✅ Zero financial authority |

---

## 4. Test Verification Results

- **Specialist Capabilities Test Suite (`test_agent_specialists.ts`)**: ✅ PASS (All 5 specialists verified).
- **Master Agent Safety Suite (`npm run test:agent`)**: **21 PASSED / 0 FAILED**.
- **Deterministic Core Hardening (`npm run test:core`)**: **5 PASSED / 0 FAILED**.
- **Hardened Infrastructure (`npm run test:infra`)**: **3 PASSED / 0 FAILED**.
