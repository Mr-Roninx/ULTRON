# ULTRON v5.0 — Phase 2: Agent Tool Registry & Structured AgentIntent System

**Phase Objective**: Build ONLY the Agent Tool Registry and structured `AgentIntent` system establishing tool metadata, strict schema validation, server-side permission enforcement (`READ` and `PROPOSE` only), and complete isolation of financial write APIs.

---

## 1. Demonstrated Permission Boundaries

| Invocation Scenario | Target Tool / Action | Permission Requested | Server Gate Verdict | Proven Result |
| :--- | :--- | :--- | :--- | :--- |
| **READ tool** | `get_opportunity`, `get_gateway_state` | `READ` | **ALLOWED** | Returns structured entity data safely. |
| **PROPOSE tool** | `create_perception_annotation`, `create_agent_proposal` | `PROPOSE` | **ALLOWED** | Inserts structured proposal record for deterministic review. |
| **EXECUTE tool** | `execute_recovery_link` | `EXECUTE` | **DENIED** | Blocked by `tool_scope_check` (Exceeds allowed scope). |
| **FINANCIAL_WRITE tool** | `direct_financial_charge` | `FINANCIAL_WRITE` | **DENIED** | Blocked by `tool_scope_check` / `write_boundary_check`. |
| **Razorpay SDK Client** | `rzpClient.paymentLink.create()` | N/A | **INACCESSIBLE** | Zero agent tool handlers import or expose SDK methods. |

---

## 2. Agent Tool Registry ([`src/agents/tool_registry.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/tool_registry.ts))

The registry manages 18 server-permissioned tools divided into two strictly bounded categories:

### A. Read-Only Investigation Tools (14 Tools)
1. `get_opportunity`: Retrieves recovery opportunity details.
2. `get_payment_context`: Retrieves payment amount, currency, decline code, and attempt count.
3. `get_customer_history`: Retrieves customer historical transactions and trust score.
4. `get_payment_attempts`: Retrieves all past payment attempts for the opportunity.
5. `get_failure_history`: Retrieves historical failure rate and decline pattern for the reason code.
6. `get_gateway_state`: Retrieves real-time simulated/observed Razorpay gateway health metrics.
7. `get_contact_history`: Retrieves past outreach communications to the customer.
8. `get_market_state`: Retrieves portfolio recovery capacity and current shadow price.
9. `get_recovery_capacity`: Retrieves remaining payment link capacity in the current run window.
10. `get_reconciliation_state`: Retrieves current settlement reconciliation status.
11. `get_provider_status`: Retrieves provider-side verification status from Razorpay API.
12. `get_full_audit_trail`: Retrieves all stored event records for the opportunity.
13. `get_similar_cases`: Retrieves similar historical recovery cases.
14. `get_agent_memory`: Retrieves working, episodic, or semantic memory filtered by temporal boundary.

### B. Proposal Tools (4 Tools)
1. `create_agent_proposal`: Submits a strategy proposal (`ACT`, `WAIT`, `ABSTAIN`) to the deterministic market.
2. `create_perception_annotation`: Submits structured failure intent, customer urgency, and merchant risk scores.
3. `create_strategy_proposal`: Submits an alternative payment method recommendation.
4. `create_outreach_draft`: Submits a customer notification draft (`SMS`, `WHATSAPP`, `EMAIL`) with mandatory compliance footer.

---

## 3. Structured AgentIntent Schema ([`src/agents/schema.ts`](file:///d:/Work%20Space/Project/Ultron/src/agents/schema.ts))

The `AgentSchemaValidator` parses, validates, and bounds raw agent outputs into a strictly typed `AgentIntent`:

```typescript
export interface AgentIntent {
  intent_id: string;
  run_id: string;
  opportunity_id: string;
  diagnosis: {
    failure_category: string;
    root_cause: string;
    confidence: number; // Clamped 0.0 to 1.0
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    recoverability_assessment: 'HIGH' | 'MODERATE' | 'POOR' | 'IMPOSSIBLE';
  };
  observations: string[];
  hypotheses: string[];
  candidate_actions: string[];
  semantic_signals: SemanticSignal[]; // Clamped 0.0 to 1.0
  proposed_plan: {
    plan_version: number;
    goal: string;
    steps: string[];
    validity_assumptions: PlanValidityAssumption[];
    candidate_actions: string[];
    preferred_action: string;
    estimated_duration_sec: number;
  };
  uncertainty: 'LOW' | 'MEDIUM' | 'HIGH';
  requested_tools: { tool_name: string; params: Record<string, any> }[];
  rationale_summary: string;
  created_at: string;
}
```

---

## 4. Test Verification Results

- **Tool Registry Tests (`test_agent_tool_registry.ts`)**: ✅ PASS (18 tools, READ allowed, PROPOSE allowed, EXECUTE denied, FINANCIAL_WRITE denied, SDK inaccessible).
- **Agent Schema Validator Tests (`test_agent_schema.ts`)**: ✅ PASS (clamping, error handling, structured intent parsing).
- **Tool Injection Tests (`test_agent_tool_injection.ts`)**: ✅ PASS (unauthorized tools & agents safely rejected).
- **Full Agent Test Suite (`npm run test:agent`)**: **20 PASSED / 0 FAILED**.
