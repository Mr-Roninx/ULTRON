# ULTRON v3.9 — Phase 17: Forensic Baseline Audit

## 1. Executive Summary & Problem Formulation
In Phase 16, ULTRON v3.8 established:
- **Candidate Novelty**: 90.0%
- **Candidate Pool Influence**: 100.0%
- **Preference Influence**: 66.7%
- **Final Decision Influence**: 0.0%
- **Deterministic Action Authority Invariant**: PROVEN (100% enforcement)

Phase 17 investigates the fundamental architectural causality:
> *"Why does high candidate novelty (90%) and candidate pool influence (100%) collapse to 0% final decision influence under the deterministic Net Expected Value (NEV) engine?"*

---

## 2. End-to-End Decision Pipeline Anatomy

The longitudinal lifecycle is structured as follows:

```text
WORLD STATE
  ↓
OBSERVE (investigation_tools & telemetry)
  ↓
INVESTIGATE (diagnose payment failure, ISO normalizer, rail health)
  ↓
HYPOTHESIZE (failure reason formulation)
  ↓
PLAN (bounded context_builder, LLM reasoner, AgentIntent generation)
  ↓
CANDIDATE ACTION GENERATOR (action_registry validation & union)
  ↓
FEASIBILITY & POLICY FILTER (customer tier, authority level, policy bounds)
  ↓
ECONOMIC RANKER (deterministic Net Expected Value formula)
  ↓
ACTION DECISION AUTHORITY (strict argmax NEV selection)
  ↓
FSM TRANSITION & EXECUTE (tool execution & simulator outcome)
  ↓
WAIT / SLEEP (VirtualClock backoff)
  ↓
EVALUATE / REPLAN (Observer detects state change or chaos)
  ↓
LEARN (Prediction error calculation & episodic memory store)
```

---

## 3. Forensic Analysis: Where LLM Information Enters & Neutralizes

### A. Point of Entry: `PLAN` Phase
1. `context_builder.build_optimized_prompt(context, feasible_actions)` packages current observable facts (failure ISO code, exposure, rail health, customer segment, past memory).
2. `LLMRouter` (or `HuggingFaceProvider`) returns an `AgentIntent`:
   - `candidate_actions`: e.g. `["WAIT", "RETRY_GATEWAY_A", "SEND_PAYMENT_LINK", "REQUEST_CUSTOMER_ACTION"]`
   - `preferred_action`: e.g. `"WAIT"`
   - `reasoning`: e.g. `"Issuer is temporarily down, recommend backoff."`

### B. Point of Union & Feasibility Filtering
In `AgentLoop.PLAN`:
```python
deterministic_feasible = registry.decision.get_feasible_actions(customer_id, max_risk, authority)
valid_llm_candidates, rejected = action_registry.reject_unauthorized_proposals(raw_llm_candidates, segment)
union_actions = list(set(valid_llm_candidates + deterministic_feasible))
filtered_actions = [a for a in union_actions if a in deterministic_feasible]
```
- **Entry Result**: The LLM successfully expands the candidate set beyond standard rule defaults (Metric A = 90%, Metric B = 100%).

### C. Point of Neutralization: `ActionRanker` & `EconomicEngine`
1. `rank_actions(filtered_actions, context)` scores every candidate using the deterministic NEV equation:
   $$\text{NEV} = \text{ExpectedRecovery} + \text{DownstreamValue} - \text{FinancialCost} - \text{OperationalCost} - \text{RelationshipCost} - \text{RiskCost}$$
2. For an ISO 91 transient failure:
   - `RETRY_GATEWAY_A`: Recoverability (0.70) × Gateway Health (0.96) × Exposure (₹24,700) = **₹10,926.49**
   - `SEND_PAYMENT_LINK`: Downstream factor (0.40) × Exposure (₹24,700) = **₹5,830.00**
   - `WAIT`: 5% exposure base = **₹1,235.00**
3. `best_action = candidate_scores[0]` (**`RETRY_GATEWAY_A`**)
4. **ActionDecisionAuthority** sets `chosen_intent.action_type = best_action.action`.

### D. Why Final Decision Influence Was 0%
1. **Deterministic Generator Overlap**: The deterministic feasible generator (`get_feasible_actions`) already generates the primary canonical actions (`RETRY`, `RETRY_GATEWAY_A`, `WAIT`, `SEND_PAYMENT_LINK`, `ESCALATE`).
2. **Dominant NEV Disparity**: In standard benchmark scenarios, the mathematically optimal action (e.g. `RETRY_GATEWAY_A` during transient outages) dominates alternatives by ₹5,000+ NEV. Thus, even when the LLM suggests `WAIT` or `SEND_PAYMENT_LINK`, the NEV ranker deterministically selects `RETRY_GATEWAY_A`.
3. **Absence of Semantic Ambiguity in Standard Scenarios**: In clear-cut test scenarios, ISO codes unambiguously map to high recoverability, rendering LLM semantic nuance unutilized at the final execution layer.

---

## 4. Phase 17 Research Hypothesis
If scenarios contain **near-tied NEVs**, **semantic ambiguity** (e.g. customer fatigue, disputed PO, clearing delays), or **semantic failure diagnosis**, does LLM intelligence produce non-zero information value ($\Delta\text{NEV} > 0$), improved diagnosis, or lower regret?

Phase 17 builds the causal measurement machinery to empirically verify this hypothesis.
