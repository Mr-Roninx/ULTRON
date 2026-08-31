# ULTRON v3.2 — MASTER IMPLEMENTATION PLAN

**Specification Source:** [ULTRON_MASTER_SPEC.md](file:///d:/Work%20Space/Project/Ultron/docs/ULTRON_MASTER_SPEC.md)  
**Architecture Review:** [ARCHITECTURE_FINAL.md](file:///d:/Work%20Space/Project/Ultron/docs/ARCHITECTURE_FINAL.md)  
**Created:** 2026-08-28  

---

## PLAN STRUCTURE

This plan divides the ULTRON v3.2 build into **8 independent phases**, ordered by dependency. Each phase is self-contained: it can be tested, validated, and accepted before the next phase begins.

The phases consolidate the spec's 21 development phases (§43) into logical implementation units while preserving dependency order.

```text
Phase 0: Foundation Cleanup & Repository Structure
    ↓
Phase 1: Financial World (Models, FSM, Clock, Events)
    ↓
Phase 2: Failure Intelligence & Tools
    ↓
Phase 3: Agent Core (State Machine, Loop, Economics, Memory)
    ↓
Phase 4: LLM Provider Architecture
    ↓
Phase 5: Simulator (Data Generation, Chaos Engine, Counterfactual Evaluator)
    ↓
Phase 6: API & Audit
    ↓
Phase 7: Frontend Command Center
```

---

# PHASE 0: FOUNDATION CLEANUP & REPOSITORY STRUCTURE

## Objective

Eliminate dead code, broken imports, duplicate systems, and establish the correct project structure required by spec §8, §45, §46. After this phase, every file in the repository compiles and passes import checks.

## Dependencies

- None. This phase has no external dependencies.

## Files to Create

| File | Purpose |
|---|---|
| `pyproject.toml` | Python package configuration, dependency management |
| `.env.example` | Environment variable template (§9) |
| `backend/__init__.py` | Update with proper package marker |
| `backend/config.py` | Centralized configuration loaded from env vars |
| `backend/llm/__init__.py` | LLM package marker |
| `backend/tools/__init__.py` | Tools package marker |
| `backend/economics/__init__.py` | Economics package marker |
| `backend/episodes/__init__.py` | Episodes package marker |
| `evaluator/__init__.py` | Counterfactual evaluator package marker |
| `.agents/rules/ultron-core.md` | Core development rules (§45) |
| `.agents/rules/financial-safety.md` | Financial safety rules (§45) |
| `.agents/rules/agent-development.md` | Agent development rules (§45) |
| `.agents/rules/testing.md` | Testing rules (§45) |
| `.agents/rules/frontend.md` | Frontend rules (§45) |
| `.agents/workflows/ultron-phase.md` | Phase workflow (§46) |

## Files to Modify

| File | Change |
|---|---|
| `requirements.txt` | Remove `openai`, `dashscope`. Add `httpx`, `huggingface_hub`, `pytest`, `python-dotenv`. Keep `pydantic`, `networkx`, `fastapi`, `uvicorn`. |
| `backend/__init__.py` | Clean up |

## Files to Delete

| File | Reason |
|---|---|
| `database/client.py` | Dead code — Supabase dependency, not used by runtime |
| `database/schema.sql` | Dead code — Supabase schema |
| `backend/simulator_api.py` | Broken imports — references non-existent methods |
| `backend/audit/engine.py` | Duplicate — Supabase-dependent audit |
| `backend/metrics/engine.py` | Duplicate — Supabase-dependent metrics |
| `backend/baselines/fixed_workflow.py` | Dead code — unused 5-line stub |
| `backend/demo/golden_scenario.py` | Dead code — hardcoded demo script |
| `backend/agent/llm.py` | Duplicate — OpenAI-specific, to be replaced by `backend/llm/` |
| `backend/agent/planner.py` | Dead code — unused deterministic planner |
| `static/app.js` | Dead code — legacy static demo |
| `static/index.html` | Dead code — legacy static demo |
| `static/style.css` | Dead code — legacy static demo |
| `check_size.py` | Utility script — not part of application |
| `download_qwen.py` | Utility script — can be recreated if needed |
| `qwen_test.py` | Utility script — not a proper test |
| `intelligence/llm.py` | Hardcoded demo LLM — to be replaced by `backend/llm/` |

## Interfaces

```python
# backend/config.py
class UltronConfig:
    llm_provider: str         # "auto" | "huggingface" | "local"
    hf_token: str | None
    hf_model: str | None
    local_llm_url: str        # default: "http://localhost:8000/v1"
    local_llm_model: str | None
    db_url: str               # default: "sqlite:///ultron.db"
    debug: bool
```

## Data Structures

None introduced in this phase.

## Implementation Sequence

1. Create `pyproject.toml` with dependency list
2. Create `.env.example` with all required env vars from spec §9
3. Create `backend/config.py` with `UltronConfig` dataclass
4. Delete all dead code files (listed above)
5. Create empty package `__init__.py` files for new packages
6. Fix `financial/reconciliation.py` — correct import names
7. Consolidate entry points: delete root `main.py`, keep `backend/main.py` as sole entry
8. Remove `database/` directory entirely
9. Create `.agents/rules/` with five rule files from spec §45
10. Create `.agents/workflows/ultron-phase.md` from spec §46
11. Update `task.md` to reflect new phase structure
12. Run `python -c "import backend; import financial; import simulator; import intelligence; import memory"` to verify all imports succeed

## Tests

```text
test_all_imports_succeed()          # Every package imports without error
test_config_loads_from_env()        # UltronConfig reads env vars correctly
test_config_defaults()              # UltronConfig has sensible defaults
```

## Adversarial Tests

```text
test_config_missing_hf_token()      # Graceful handling when HF_TOKEN not set
test_config_invalid_provider()      # Rejects unknown provider names
```

## Acceptance Criteria

- [ ] All files in the repository import without error
- [ ] No references to Supabase, OpenAI, or dashscope remain in application code
- [ ] `pyproject.toml` exists with correct dependencies
- [ ] `.env.example` exists with all spec-required env vars
- [ ] `.agents/rules/` contains 5 rule files
- [ ] `.agents/workflows/` contains the phase workflow
- [ ] `pytest tests/` runs with 0 import errors

## Definition of Done

Every Python module in the repository imports successfully. The project has a single entry point. No dead code remains. The package structure matches the specification target. All 5 Antigravity workspace rules exist.

---

# PHASE 1: FINANCIAL WORLD (MODELS, FSM, CLOCK, EVENTS)

## Objective

Build the complete financial world model per spec §11-15. This is the deterministic substrate on which the agent operates. After this phase, the simulator can represent the full payment lifecycle, advance simulated time with scheduled events, and produce typed domain events from every state transition.

## Dependencies

- Phase 0 complete (clean repository structure)

## Files to Create

| File | Purpose |
|---|---|
| `simulator/models.py` | **REWRITE** — All domain entities: Customer, Payment, PaymentAttempt, Invoice, CheckoutSession, Gateway, RecoveryAction, Communication, Mission, Event |
| `simulator/events.py` | Typed domain event model (§14) |
| `simulator/gateway.py` | Gateway entity with health model |
| `financial/failure_intelligence.py` | FailureNormalizer, FailureClassifier, RetryabilityResolver, ReconciliationResolver (§12) |
| `financial/failure_codes.py` | Provider-specific failure code mappings (configuration data, §12) |

## Files to Modify

| File | Change |
|---|---|
| `simulator/models.py` | Add INITIATED, AUTHORIZING, RECONCILING, REFUNDED to PaymentStatus. Add PaymentAttempt, Gateway, RecoveryAction, Communication models. Add relationship signals to Customer. Add `rail`, `gateway_id` to Payment. |
| `simulator/clock.py` | Add `schedule()`, `cancel()`, `next_event()`, `run_until()`. Remove `time.time()` fallback. |
| `simulator/world.py` | Add gateways dict. Add `update_checkout_status()`. Use FSM enforcement on all transitions. Add deep-copy `snapshot()` method for counterfactual forking. |
| `simulator/event_bus.py` | Produce typed `DomainEvent` objects instead of raw dicts. |
| `financial/fsm.py` | Add missing states (INITIATED, AUTHORIZING, RECONCILING, REFUNDED). Add CheckoutFSM. Complete transition maps. Add event emission on transition. |
| `financial/reconciliation.py` | Fix broken imports. Use correct class/method names. Wire through RECONCILING state. |

## Interfaces

```python
# simulator/models.py
class PaymentStatus(str, Enum):
    CREATED = "CREATED"
    INITIATED = "INITIATED"
    AUTHORIZING = "AUTHORIZING"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    SETTLED = "SETTLED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    RECONCILING = "RECONCILING"
    REVERSED = "REVERSED"
    REFUNDED = "REFUNDED"

class FailureCategory(str, Enum):
    TRANSIENT = "TRANSIENT"
    CUSTOMER_ACTION_REQUIRED = "CUSTOMER_ACTION_REQUIRED"
    CREDENTIAL_PROBLEM = "CREDENTIAL_PROBLEM"
    LIQUIDITY_RELATED = "LIQUIDITY_RELATED"
    GATEWAY_PROBLEM = "GATEWAY_PROBLEM"
    UNKNOWN = "UNKNOWN"
    NON_RETRYABLE = "NON_RETRYABLE"

# simulator/clock.py
class VirtualClock:
    def now(self) -> int: ...
    def advance(self, seconds: int) -> int: ...
    def schedule(self, at_time: int, callback: Callable) -> str: ...
    def cancel(self, event_id: str) -> bool: ...
    def next_event(self) -> tuple[int, Callable] | None: ...
    def run_until(self, target_time: int) -> None: ...
    def reset(self, start_time: int = 0) -> None: ...

# simulator/events.py
class DomainEvent(BaseModel):
    event_id: str
    event_type: str
    entity_type: str         # "PAYMENT", "INVOICE", "CHECKOUT"
    entity_id: str
    customer_id: str
    timestamp: int
    previous_state: str | None
    new_state: str
    payload: dict

# simulator/world.py
class FinancialWorld:
    def snapshot(self) -> "FinancialWorld": ...  # Deep copy for counterfactual fork

# financial/failure_intelligence.py
class FailureNormalizer:
    def normalize(self, raw_code: str, gateway_id: str) -> str: ...

class FailureClassifier:
    def classify(self, normalized_code: str) -> FailureCategory: ...

class RetryabilityResolver:
    def is_retryable(self, category: FailureCategory) -> bool: ...

class ReconciliationResolver:
    def resolve(self, payment_id: str) -> PaymentStatus: ...
```

## Data Structures

```python
# Gateway
class Gateway(BaseModel):
    id: str
    name: str
    health: float              # 0.0 to 1.0
    supported_rails: list[str]
    failure_rate: float        # current failure rate

# PaymentAttempt
class PaymentAttempt(BaseModel):
    id: str
    payment_id: str
    gateway_id: str
    status: PaymentStatus
    failure_code: str | None
    timestamp: int

# RecoveryAction
class RecoveryAction(BaseModel):
    id: str
    mission_id: str
    customer_id: str
    action_type: str
    status: str                # PENDING, EXECUTED, BLOCKED, FAILED
    expected_value: float
    observed_value: float | None
    timestamp: int

# Communication
class Communication(BaseModel):
    id: str
    customer_id: str
    channel: str               # EMAIL, SMS, PUSH
    message_type: str
    sent_at: int
    response: str | None       # OPENED, CLICKED, IGNORED, None
```

## Implementation Sequence

1. Rewrite `simulator/models.py` with all entities and complete enums
2. Rewrite `simulator/clock.py` with event scheduling (using a min-heap priority queue)
3. Create `simulator/events.py` with `DomainEvent` model
4. Create `simulator/gateway.py` with Gateway model
5. Rewrite `financial/fsm.py` with complete state machines and event emission
6. Create `financial/failure_intelligence.py` with all 4 components
7. Create `financial/failure_codes.py` with configuration-driven mappings
8. Update `simulator/world.py` with new entities, `snapshot()`, and complete FSM enforcement
9. Update `simulator/event_bus.py` to use typed `DomainEvent`
10. Fix `financial/reconciliation.py` with correct imports and RECONCILING flow
11. Update `simulator/seed.py` to use new models (keep Ananya Textiles scenario working)

## Tests

```text
# Unit Tests
test_payment_fsm_all_valid_transitions()
test_payment_fsm_all_invalid_transitions()
test_payment_fsm_unknown_to_reconciling()
test_invoice_fsm_valid_transitions()
test_checkout_fsm_valid_transitions()
test_clock_advance()
test_clock_schedule_and_fire()
test_clock_cancel_scheduled_event()
test_clock_run_until()
test_clock_next_event_ordering()
test_domain_event_created_on_transition()
test_failure_normalizer()
test_failure_classifier_all_categories()
test_retryability_resolver()
test_reconciliation_flow()
test_world_snapshot_creates_independent_copy()
test_world_snapshot_same_state()
```

## Adversarial Tests

```text
test_fsm_rejects_settled_to_created()
test_fsm_rejects_failed_to_captured()
test_clock_negative_advance_rejected()
test_clock_schedule_in_past_rejected()
test_world_update_nonexistent_payment()
test_world_update_nonexistent_invoice()
test_failure_normalizer_unknown_code()
test_failure_normalizer_unknown_gateway()
```

## Acceptance Criteria

- [ ] PaymentStatus has exactly 11 states matching spec §11
- [ ] All valid and invalid FSM transitions tested
- [ ] VirtualClock has schedule/cancel/next_event/run_until
- [ ] VirtualClock never calls `time.time()` in simulation mode
- [ ] Domain events are typed Pydantic models
- [ ] Every state transition in world produces a DomainEvent
- [ ] FinancialWorld.snapshot() creates a deep, independent copy
- [ ] FailureClassifier classifies into all 7 categories from spec §12
- [ ] ReconciliationResolver correctly flows UNKNOWN → RECONCILING → terminal state
- [ ] 30-day simulation runs in under 2 seconds

## Definition of Done

The financial world model is complete and spec-compliant. Every entity from §13 exists. The FSM enforces all transitions from §11. The clock supports discrete-event simulation per §15. All state transitions produce typed events per §14. The failure intelligence pipeline from §12 is functional. The world can be snapshot for counterfactual evaluation.

---

# PHASE 2: FAILURE INTELLIGENCE & TOOLS

## Objective

Implement the complete tool surface (§20-21), recovery strategy set (§24), relationship state tracking (§25), and economic engine (§23). After this phase, the agent has a fully validated tool gateway that enforces the trust boundary (§6) for every action.

## Dependencies

- Phase 1 complete (world model, FSM, clock, events)

## Files to Create

| File | Purpose |
|---|---|
| `backend/tools/investigation.py` | 8 investigation tools from spec §20 |
| `backend/tools/decision.py` | `get_feasible_actions`, `calculate_action_value` from spec §20 |
| `backend/tools/execution.py` | 6 execution tools from spec §20, each following tool contract §21 |
| `backend/tools/registry.py` | Tool registration and discovery |
| `backend/economics/engine.py` | NetExpectedValue calculator (§23) |
| `backend/economics/relationship.py` | Relationship state and cost proxy (§25) |
| `backend/episodes/engine.py` | Revenue Episode aggregator (§16) |

## Files to Modify

| File | Change |
|---|---|
| `financial/feasible_actions.py` | Expand to 9 action types from spec §24 (WAIT, RECONCILE, RETRY, REQUEST_CUSTOMER_ACTION, SEND_PAYMENT_LINK, SEND_MESSAGE, REGISTER_PTP, ESCALATE, STOP). Integrate economic engine. |
| `financial/authority.py` | Map all 9 action types to authority levels |
| `financial/policy.py` | Add policy rules for new action types |
| `financial/risk.py` | Add risk profiles for all 9 action types |
| `financial/idempotency.py` | No change expected |
| `simulator/customer_state.py` | Add relationship signals from §25 |

## Files to Delete

| File | Reason |
|---|---|
| `backend/agent/tools.py` | Replaced by `backend/tools/` package |
| `backend/agent/investigation.py` | Replaced by `backend/tools/investigation.py` |
| `backend/agent/execution.py` | Replaced by `backend/tools/execution.py` |

## Interfaces

```python
# backend/tools/investigation.py (§20)
class InvestigationTools:
    def get_customer_context(customer_id: str) -> dict: ...
    def get_payment(payment_id: str) -> dict: ...
    def get_payment_attempts(payment_id: str) -> list[dict]: ...
    def get_invoice(invoice_id: str) -> dict: ...
    def get_checkout_session(session_id: str) -> dict: ...
    def get_gateway_health(gateway_id: str) -> dict: ...
    def get_related_events(customer_id: str, window: int) -> list[DomainEvent]: ...
    def get_previous_episodes(customer_id: str) -> list[dict]: ...

# backend/tools/decision.py (§20)
class DecisionTools:
    def get_feasible_actions(context: dict, authority: AuthorityLevel, max_risk: float) -> list[dict]: ...
    def calculate_action_value(action_type: str, context: dict) -> dict: ...

# backend/tools/execution.py (§20-21)
# Every tool follows: validate input → validate state → validate authority → execute → emit event → return structured result
class ExecutionTools:
    def reconcile_payment(mission_id: str, payment_id: str) -> ToolResult: ...
    def schedule_retry(mission_id: str, payment_id: str, delay: int) -> ToolResult: ...
    def generate_payment_link(mission_id: str, customer_id: str, items: list[str]) -> ToolResult: ...
    def send_customer_message(mission_id: str, customer_id: str, channel: str, message_type: str) -> ToolResult: ...
    def register_ptp(mission_id: str, customer_id: str, promise_date: int) -> ToolResult: ...
    def escalate_to_human(mission_id: str, reason: str) -> ToolResult: ...

class ToolResult(BaseModel):
    success: bool
    action_id: str
    state_change: str | None
    message: str

# backend/economics/engine.py (§23)
class EconomicEngine:
    def calculate_nev(
        expected_recovery: float,
        action_cost: float,
        relationship_cost: float,
        risk_cost: float
    ) -> float: ...

    def evaluate_action(action_type: str, context: dict) -> dict: ...
    # Returns: { net_expected_value, expected_recovery, action_cost, relationship_cost, risk_cost }

# backend/episodes/engine.py (§16)
class RevenueEpisode(BaseModel):
    episode_id: str
    customer_id: str
    payments: list[str]        # payment IDs
    invoices: list[str]        # invoice IDs
    checkouts: list[str]       # checkout session IDs
    total_exposure: float
    created_at: int

class EpisodeEngine:
    def create_episode(customer_id: str) -> RevenueEpisode: ...
    def get_episodes(customer_id: str) -> list[RevenueEpisode]: ...
```

## Data Structures

```python
# backend/economics/relationship.py (§25)
class RelationshipState(BaseModel):
    customer_id: str
    recent_contacts: int           # contacts in last 30 days
    recent_responses: int          # responses to contacts
    successful_prior_recoveries: int
    customer_value: float          # LTV
    complaints: int
    opt_out: bool
    silence_duration: int          # seconds since last response

    def relationship_cost_proxy(self) -> float: ...
    # Deterministic calculation from observable signals
```

## Implementation Sequence

1. Create `backend/economics/engine.py` with NEV calculator
2. Create `backend/economics/relationship.py` with relationship state
3. Create `backend/episodes/engine.py` with Revenue Episode
4. Update `simulator/customer_state.py` with relationship signals
5. Expand `financial/feasible_actions.py` to 9 action types
6. Update `financial/authority.py`, `financial/policy.py`, `financial/risk.py` for all 9 actions
7. Create `backend/tools/investigation.py` with 8 tools
8. Create `backend/tools/decision.py` with 2 tools (integrating economic engine)
9. Create `backend/tools/execution.py` with 6 tools following tool contract
10. Create `backend/tools/registry.py`
11. Delete old tool/investigation/execution files

## Tests

```text
# Unit
test_nev_calculation_basic()
test_nev_negative_when_cost_exceeds_recovery()
test_relationship_cost_proxy_high_complaints()
test_relationship_cost_proxy_opt_out()
test_revenue_episode_aggregates_all_channels()
test_feasible_actions_excludes_unauthorized()
test_feasible_actions_excludes_risky()
test_feasible_actions_excludes_policy_violations()
test_tool_contract_validate_input()
test_tool_contract_validate_state()
test_tool_contract_validate_authority()
test_tool_contract_emit_event()
test_tool_contract_structured_result()

# Integration
test_investigation_tools_return_world_state()
test_execution_tool_modifies_world()
test_reconcile_payment_flows_through_fsm()
test_schedule_retry_uses_virtual_clock()
```

## Adversarial Tests

```text
test_tool_rejects_invalid_payment_id()
test_tool_rejects_retry_on_unknown_payment()
test_tool_rejects_duplicate_action()
test_nev_with_zero_recovery()
test_episode_with_no_exposure()
test_feasible_actions_returns_empty_when_all_blocked()
```

## Acceptance Criteria

- [ ] All 9 recovery actions from spec §24 exist in the feasible action set
- [ ] All 14 tools from spec §20 are implemented
- [ ] Every execution tool follows the 6-step contract from §21
- [ ] Economic engine calculates NEV with explicit units (§23)
- [ ] Relationship state uses observable signals only, no invented scores (§25)
- [ ] Revenue episodes aggregate across payment/checkout/invoice channels (§16)
- [ ] `test_tool_rejects_retry_on_unknown_payment()` passes (§40 prerequisite)

## Definition of Done

The tool gateway is complete. Every tool enforces the trust boundary. The economic engine provides deterministic action valuation. Revenue episodes exist. The feasible action set covers all spec-defined recovery strategies.

---

# PHASE 3: AGENT CORE (STATE MACHINE, LOOP, MEMORY)

## Objective

Build the agent state machine (§18), bounded agent loop (§19), prediction-error replanning (§30), and episodic memory (§26). After this phase, ULTRON can observe, investigate, hypothesize, plan, validate, execute, observe outcomes, detect prediction errors, replan, and learn — all within bounded loops.

## Dependencies

- Phase 2 complete (tools, economics, episodes)

## Files to Create

| File | Purpose |
|---|---|
| `backend/agent/state_machine.py` | Agent FSM with 13 states from spec §18 |
| `backend/agent/schemas.py` | Pydantic schemas for LLM intent validation (trust boundary §6) |
| `backend/agent/loop.py` | Bounded agent loop (§19) |

## Files to Modify

| File | Change |
|---|---|
| `backend/agent/state.py` | Replace with spec-compliant 13 states (OBSERVE, INVESTIGATE, HYPOTHESIZE, PLAN, FEASIBILITY_CHECK, AUTHORITY_CHECK, RISK_CHECK, EXECUTE, WAIT, EVALUATE, LEARN, REPLAN, ESCALATE, COMPLETE) |
| `backend/agent/runtime.py` | Complete rewrite — implement proper agent loop using new state machine, new tools, Pydantic-validated LLM output |
| `backend/agent/observation.py` | Integrate into runtime properly. Use prediction error threshold from spec §30. |
| `backend/agent/circuit_breakers.py` | Update limits: MAX_STEPS=12, MAX_REPLANS=5, MAX_IDENTICAL_FAILURES=2 (§19) |
| `memory/episodic.py` | Upgrade to use virtual clock timestamps, structured memory records, exact episodic retrieval |
| `backend/missions/models.py` | Add spec-required fields: observations, hypotheses, plans, actions, results, prediction_errors, replans, final_outcome (§17) |

## Interfaces

```python
# backend/agent/schemas.py (§6 — Trust Boundary)
class AgentIntent(BaseModel):
    action_type: str                # Must match recovery strategy enum
    reasoning: str
    expected_yield: float
    payload: dict                   # Action-specific parameters

    @validator("action_type")
    def validate_action_type(cls, v): ...

# backend/agent/state_machine.py (§18)
class AgentPhase(str, Enum):
    OBSERVE = "OBSERVE"
    INVESTIGATE = "INVESTIGATE"
    HYPOTHESIZE = "HYPOTHESIZE"
    PLAN = "PLAN"
    FEASIBILITY_CHECK = "FEASIBILITY_CHECK"
    AUTHORITY_CHECK = "AUTHORITY_CHECK"
    RISK_CHECK = "RISK_CHECK"
    EXECUTE = "EXECUTE"
    WAIT = "WAIT"
    EVALUATE = "EVALUATE"
    LEARN = "LEARN"
    REPLAN = "REPLAN"
    ESCALATE = "ESCALATE"
    COMPLETE = "COMPLETE"

class AgentStateMachine:
    VALID_TRANSITIONS: dict[AgentPhase, set[AgentPhase]]
    def transition(self, target: AgentPhase) -> None: ...
    def current(self) -> AgentPhase: ...

# backend/agent/loop.py (§19)
class AgentLoop:
    MAX_STEPS: int = 12
    MAX_REPLANS: int = 5
    MAX_IDENTICAL_FAILURES: int = 2

    def run(self, mission: Mission, customer_id: str) -> MissionResult: ...

# memory/episodic.py (§26)
class EpisodeRecord(BaseModel):
    customer_id: str
    failure_type: str
    action_taken: str
    result: str                     # RECOVERED, FAILED, ESCALATED
    recovery_amount: float
    timestamp: int                  # virtual clock time

class EpisodicMemory:
    def store(self, record: EpisodeRecord) -> None: ...
    def retrieve(self, customer_id: str, failure_type: str) -> list[EpisodeRecord]: ...
```

## Data Structures

```python
# backend/missions/models.py (§17) — Extended Mission
class Mission(BaseModel):
    mission_id: str
    objective: str
    starting_state: dict
    observations: list[dict]
    hypotheses: list[str]
    plans: list[dict]
    actions: list[dict]
    results: list[dict]
    prediction_errors: list[dict]
    replans: list[dict]
    final_outcome: dict | None
    goal: MissionGoal
    deadline: int
    constraints: MissionConstraints
    authority: str
    status: MissionStatus
    recovered_amount: float
```

## Implementation Sequence

1. Update `backend/agent/state.py` with 13 spec-compliant states
2. Create `backend/agent/state_machine.py` with transition validation
3. Create `backend/agent/schemas.py` with `AgentIntent` Pydantic model
4. Update `backend/agent/circuit_breakers.py` with spec limits (12/5/2)
5. Update `backend/missions/models.py` with full mission fields
6. Upgrade `memory/episodic.py` with structured records and virtual clock
7. Rewrite `backend/agent/runtime.py` with proper loop:
   - OBSERVE: poll world for relevant events
   - INVESTIGATE: call investigation tools
   - HYPOTHESIZE: LLM forms hypothesis
   - PLAN: LLM chooses from feasible actions (via Pydantic schema)
   - FEASIBILITY_CHECK → AUTHORITY_CHECK → RISK_CHECK: deterministic validation
   - EXECUTE: call execution tool
   - WAIT: schedule follow-up via virtual clock
   - EVALUATE: compare prediction vs reality (§30)
   - LEARN: store episode to memory
   - REPLAN: if prediction error exceeds threshold
   - ESCALATE: if bounds exceeded
   - COMPLETE: mission done
8. Create `backend/agent/loop.py` — orchestrator that manages iteration counts
9. Integrate `backend/agent/observation.py` into the EVALUATE phase
10. Wire memory retrieval into INVESTIGATE phase

## Tests

```text
# Unit
test_agent_state_machine_valid_transitions()
test_agent_state_machine_invalid_transitions()
test_agent_intent_pydantic_validation()
test_agent_intent_rejects_invalid_action_type()
test_circuit_breaker_max_steps_12()
test_circuit_breaker_max_replans_5()
test_circuit_breaker_max_identical_failures_2()
test_prediction_error_triggers_replan()
test_prediction_error_below_threshold_completes()
test_episodic_memory_store_and_retrieve()
test_mission_tracks_observations()
test_mission_tracks_prediction_errors()

# Integration
test_agent_full_cycle_observe_to_complete()
test_agent_replan_on_prediction_error()
test_agent_escalate_on_max_replans()
test_agent_memory_influences_subsequent_plan()
```

## Adversarial Tests

```text
test_agent_handles_llm_malformed_json()
test_agent_handles_llm_timeout()
test_agent_prevents_infinite_loop()
test_agent_rejects_invalid_state_transition()
test_agent_escalates_on_identical_failures()
test_agent_intent_rejects_unknown_action()
```

## Acceptance Criteria

- [ ] Agent has exactly 13 states from spec §18
- [ ] Agent loop bounded by MAX_STEPS=12, MAX_REPLANS=5, MAX_IDENTICAL_FAILURES=2 (§19)
- [ ] LLM output validated through Pydantic `AgentIntent` before reaching executor (§6)
- [ ] Prediction error triggers REPLAN when above threshold (§30)
- [ ] Same action failing twice triggers ESCALATE (§19)
- [ ] Mission records observations, hypotheses, plans, prediction_errors, replans (§17)
- [ ] Episodic memory stores and retrieves exact records (§26)

## Definition of Done

The agent core implements the full spec §18 state machine with bounded loops, trust-boundary enforcement, prediction-error replanning, and episodic memory. The agent can run a complete mission from OBSERVE to COMPLETE (or ESCALATE).

---

# PHASE 4: LLM PROVIDER ARCHITECTURE

## Objective

Implement the LLM provider abstraction (§8), HuggingFace provider (§9), local Qwen fallback (§10), and auto-routing with fallback logging. After this phase, ULTRON uses a real LLM for investigation, hypothesis formation, and plan selection — with a tested fallback chain.

## Dependencies

- Phase 3 complete (agent core with Pydantic schemas)

## Files to Create

| File | Purpose |
|---|---|
| `backend/llm/base.py` | `LLMProvider` abstract base class (§8) |
| `backend/llm/huggingface.py` | `HuggingFaceProvider` using HF Inference API (§9) |
| `backend/llm/local_qwen.py` | `LocalQwenProvider` via OpenAI-compatible API (§10) |
| `backend/llm/router.py` | Auto-router with fallback and logging (§8) |
| `backend/llm/schemas.py` | Response schemas for structured output |

## Files to Modify

| File | Change |
|---|---|
| `backend/agent/runtime.py` | Replace direct LLM calls with `LLMRouter` |
| `backend/config.py` | Wire LLM configuration to router |

## Interfaces

```python
# backend/llm/base.py (§8)
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: dict | None = None) -> str: ...

    @abstractmethod
    async def structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel: ...

    @abstractmethod
    async def health(self) -> bool: ...

# backend/llm/router.py (§8)
class LLMRouter:
    def __init__(self, config: UltronConfig): ...

    async def generate(self, prompt: str, context: dict | None = None) -> str: ...
    async def structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel: ...

    # Internal: tries primary, falls back, logs fallback event
    # Emits: {"event": "LLM_PROVIDER_FALLBACK", "from": "...", "to": "...", "reason": "..."}
```

## Data Structures

```python
# backend/llm/schemas.py
class LLMPlanResponse(BaseModel):
    action_type: str
    reasoning: str
    expected_yield: float
    payload: dict

class LLMHypothesisResponse(BaseModel):
    hypothesis: str
    confidence: float
    evidence: list[str]

class LLMFallbackEvent(BaseModel):
    event: str = "LLM_PROVIDER_FALLBACK"
    from_provider: str
    to_provider: str
    reason: str
    timestamp: int
```

## Implementation Sequence

1. Create `backend/llm/base.py` with `LLMProvider` ABC
2. Create `backend/llm/schemas.py` with response models
3. Create `backend/llm/huggingface.py` — call HF Inference API via `httpx` or `huggingface_hub`
4. Create `backend/llm/local_qwen.py` — call local OpenAI-compatible endpoint
5. Create `backend/llm/router.py` — auto-routing with fallback chain and logging
6. Wire router into `backend/agent/runtime.py`
7. Update `backend/config.py` to pass config to router

## Tests

```text
# Unit
test_hf_provider_health_check()
test_local_qwen_provider_health_check()
test_router_uses_primary_when_healthy()
test_router_falls_back_on_failure()
test_router_logs_fallback_event()
test_structured_output_validates_schema()

# Integration (requires mock or stub)
test_router_generates_valid_plan()
test_router_generates_valid_hypothesis()
```

## Adversarial Tests

```text
test_router_handles_both_providers_down()
test_router_handles_malformed_response()
test_router_handles_timeout()
test_router_handles_rate_limit()
test_structured_rejects_invalid_schema()
```

## Acceptance Criteria

- [ ] `LLMProvider` ABC exists with `generate()`, `structured()`, `health()` (§8)
- [ ] `HuggingFaceProvider` calls HF Inference API (§9)
- [ ] `LocalQwenProvider` calls OpenAI-compatible local endpoint (§10)
- [ ] Router auto-selects primary and falls back with logging (§8)
- [ ] Every fallback produces a JSON event (§8)
- [ ] Configuration driven by env vars: `ULTRON_LLM_PROVIDER`, `HF_TOKEN`, `HF_MODEL`, `LOCAL_LLM_URL`, `LOCAL_LLM_MODEL` (§9)
- [ ] Agent runtime uses `LLMRouter`, never a direct provider

## Definition of Done

ULTRON has a pluggable LLM backend. The HuggingFace provider is the primary. The local Qwen model is the fallback. Every fallback is logged. The agent never directly couples to a specific LLM provider. Configuration is entirely environment-driven.

---

# PHASE 5: SIMULATOR (DATA GENERATION, CHAOS, COUNTERFACTUAL)

## Objective

Build the deterministic data generator (§36-37), full chaos engine (§31), and the counterfactual evaluator (§28-29). This is the most architecturally critical phase — the counterfactual evaluator must be completely isolated from the agent (§29).

## Dependencies

- Phase 1 complete (world model with `snapshot()`)
- Phase 3 complete (agent loop)

## Files to Create

| File | Purpose |
|---|---|
| `simulator/generator.py` | Seeded data generator for 200 customers, 2000 payments, 300 invoices, 500 checkouts (§36-37) |
| `evaluator/__init__.py` | Package marker |
| `evaluator/engine.py` | Counterfactual evaluator — forks world, runs control + treatment (§28-29) |
| `evaluator/control.py` | Control runner — no ULTRON intervention |
| `evaluator/isolation.py` | Isolation guard — ensures agent cannot access evaluator state (§29) |

## Files to Modify

| File | Change |
|---|---|
| `simulator/chaos.py` | Complete rewrite — implement all 7 chaos event types from §31 (UPI_DEGRADATION, GATEWAY_TIMEOUT, WEBHOOK_DELAY, GATEWAY_RECOVERY, MASS_CHECKOUT_ABANDONMENT, CUSTOMER_SILENCE, PAYMENT_STATE_AMBIGUITY). Each must modify actual simulated world state. |
| `simulator/seed.py` | Keep Ananya Textiles scenario. Add ability to generate full dataset using deterministic seed. |

## Interfaces

```python
# simulator/generator.py (§36-37)
class WorldGenerator:
    def __init__(self, seed: int = 42): ...
    def generate(self) -> FinancialWorld: ...
    # Produces: 200 customers, 2000 payments, 300 invoices, 500 checkouts
    # All from deterministic seed

# simulator/chaos.py (§31)
class ChaosEventType(str, Enum):
    UPI_DEGRADATION = "UPI_DEGRADATION"
    GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"
    WEBHOOK_DELAY = "WEBHOOK_DELAY"
    GATEWAY_RECOVERY = "GATEWAY_RECOVERY"
    MASS_CHECKOUT_ABANDONMENT = "MASS_CHECKOUT_ABANDONMENT"
    CUSTOMER_SILENCE = "CUSTOMER_SILENCE"
    PAYMENT_STATE_AMBIGUITY = "PAYMENT_STATE_AMBIGUITY"

class ChaosEngine:
    def inject(self, event_type: ChaosEventType, severity: float) -> DomainEvent: ...
    # Must modify actual world state, not just UI values

# evaluator/engine.py (§28-29)
class CounterfactualEvaluator:
    def evaluate(
        self,
        world: FinancialWorld,
        mission_config: dict,
        agent_factory: Callable,
        seed: int
    ) -> EvaluationResult: ...

class EvaluationResult(BaseModel):
    control_outcome: float          # Revenue recovered without ULTRON
    treatment_outcome: float        # Revenue recovered with ULTRON
    incremental_recovery: float     # treatment - control
    control_events: list[dict]
    treatment_events: list[dict]

# evaluator/isolation.py (§29)
class IsolationGuard:
    @staticmethod
    def verify_agent_context_clean(agent_context: dict) -> bool: ...
    # Ensures context does not contain:
    #   baseline_outcome, actual_recovery, counterfactual_recovery,
    #   control_outcome, treatment_outcome, incremental_recovery
```

## Data Structures

```python
# evaluator/engine.py
class EvaluationResult(BaseModel):
    evaluation_id: str
    seed: int
    control_outcome: float
    treatment_outcome: float
    incremental_recovery: float
    control_trace: list[dict]      # What happened in control world
    treatment_trace: list[dict]    # What happened in treatment world
    timestamp: int
```

## Implementation Sequence

1. Create `simulator/generator.py` with seeded data generation
2. Rewrite `simulator/chaos.py` with 7 event types that modify world state
3. Create `evaluator/isolation.py` with context verification
4. Create `evaluator/control.py` — runs simulation with no agent intervention
5. Create `evaluator/engine.py`:
   a. Snapshot current world state
   b. Fork into control world (deep copy) and treatment world (deep copy)
   c. Run control: advance time, let events resolve naturally (no agent)
   d. Run treatment: advance time, let ULTRON agent act
   e. Compare outcomes: `incremental = treatment - control`
   f. Return EvaluationResult
6. Update `simulator/seed.py` to support both single-scenario and full-dataset modes
7. Verify isolation: write test that attempts to leak evaluator data to agent context

## Tests

```text
# Unit
test_generator_seed_42_deterministic()
test_generator_produces_200_customers()
test_generator_produces_2000_payments()
test_chaos_upi_degradation_modifies_gateway()
test_chaos_gateway_timeout_modifies_world()
test_chaos_mass_checkout_abandonment()
test_chaos_payment_state_ambiguity()
test_counterfactual_control_has_no_agent_actions()
test_counterfactual_treatment_has_agent_actions()
test_counterfactual_incremental_equals_treatment_minus_control()
test_isolation_guard_clean_context()
test_isolation_guard_rejects_contaminated_context()

# Integration
test_full_evaluation_with_seed_42()
test_chaos_then_evaluation()
```

## Adversarial Tests

```text
# THE MOST IMPORTANT TESTS (§39-42)
test_agent_cannot_access_future_outcome()       # §39
test_unknown_payment_blocks_duplicate_action()   # §40
test_chaos_causes_replan()                       # §41
test_recovery_metric_is_counterfactual()         # §42

# Additional adversarial
test_counterfactual_worlds_independent_after_fork()
test_control_world_no_modifications_by_agent()
test_chaos_event_not_just_ui_change()
```

## Acceptance Criteria

- [ ] `World(seed=42)` produces identical world on every run (§37)
- [ ] Generator produces 200 customers, 2000 payments, 300 invoices, 500 checkouts (§36)
- [ ] All 7 chaos event types from §31 modify actual simulated world
- [ ] Counterfactual evaluator forks world into control + treatment from identical state (§28)
- [ ] Agent never sees control outcome before acting (§29)
- [ ] `incremental = treatment_outcome - control_outcome` (§42)
- [ ] `test_agent_cannot_access_future_outcome()` passes (§39)
- [ ] `test_unknown_payment_blocks_duplicate_action()` passes (§40)
- [ ] `test_chaos_causes_replan()` passes (§41)
- [ ] `test_recovery_metric_is_counterfactual()` passes (§42)
- [ ] 30-day simulation of 200 customers runs in under 10 seconds

## Definition of Done

The simulator generates realistic, reproducible financial worlds. The chaos engine injects 7 types of real-world disruptions. The counterfactual evaluator proves incremental recovery through isolated control/treatment comparison. All 4 critical tests from the spec pass.

---

# PHASE 6: API & AUDIT

## Objective

Build the Mission API (§34 backend), hash-chained audit ledger (§33), and agent trace system (§35). After this phase, the complete backend is accessible via REST API, every action is tamper-evidently logged, and the agent's decision trace is queryable.

## Dependencies

- Phase 3 complete (agent core)
- Phase 5 complete (counterfactual evaluator)

## Files to Create

| File | Purpose |
|---|---|
| `backend/audit/ledger.py` | Hash-chained tamper-evident audit trail (§33) |
| `backend/audit/trace.py` | Agent trace formatter for UI (§35) |
| `backend/api/missions.py` | Mission CRUD + trigger endpoints |
| `backend/api/evaluation.py` | Counterfactual evaluation endpoints |
| `backend/api/simulator.py` | Simulator control endpoints (reset, tick, state, chaos) |
| `backend/api/memory.py` | Memory query endpoints |
| `backend/api/system.py` | System health, LLM status endpoints |

## Files to Modify

| File | Change |
|---|---|
| `backend/main.py` | Complete rewrite — single FastAPI app with all routers, CORS, WebSocket |
| `backend/api/agent.py` | Rewrite to use new agent runtime |
| `backend/api/chaos.py` | Rewrite to use new chaos engine with 7 event types |
| `backend/api/audit.py` | Rewrite to use hash-chained ledger |
| `backend/api/customers.py` | Rewrite to use new world model |
| `backend/missions/audit.py` | **DELETE** — replaced by `backend/audit/ledger.py` |

## Interfaces

```python
# backend/audit/ledger.py (§33)
class AuditEvent(BaseModel):
    event_id: str
    mission_id: str
    timestamp: int
    actor: str                    # "ULTRON", "CHAOS", "HUMAN", "SYSTEM"
    event_type: str
    input_hash: str
    previous_hash: str
    current_hash: str             # HASH(event + previous_hash)
    payload: dict

class AuditLedger:
    def log(self, mission_id: str, actor: str, event_type: str, payload: dict) -> AuditEvent: ...
    def get_trace(self, mission_id: str) -> list[AuditEvent]: ...
    def verify_chain(self, mission_id: str) -> bool: ...

# backend/audit/trace.py (§35)
class TraceEntry(BaseModel):
    timestamp: int
    phase: str                    # AgentPhase value
    description: str
    details: dict | None

class AgentTracer:
    def format_trace(self, mission_id: str) -> list[TraceEntry]: ...
```

## Data Structures

The `AuditEvent` hash chain:
```text
Event N:
  current_hash = SHA256(event_data + previous_hash)
  previous_hash = Event(N-1).current_hash

Event 0:
  previous_hash = "GENESIS"
```

## Implementation Sequence

1. Create `backend/audit/ledger.py` with hash-chaining logic
2. Create `backend/audit/trace.py` with trace formatter
3. Wire audit ledger into agent runtime (every state transition logged)
4. Create `backend/api/missions.py`
5. Create `backend/api/evaluation.py`
6. Create `backend/api/simulator.py`
7. Create `backend/api/memory.py`
8. Create `backend/api/system.py`
9. Rewrite `backend/main.py` as the sole entry point
10. Rewrite existing API routers to use new subsystems
11. Delete `backend/missions/audit.py`

## Tests

```text
# Unit
test_audit_hash_chain_integrity()
test_audit_verify_chain_detects_tampering()
test_audit_genesis_event()
test_trace_format_matches_spec_35()

# Integration
test_api_create_mission()
test_api_get_mission_trace()
test_api_trigger_chaos()
test_api_get_evaluation_result()
test_api_get_system_health()

# E2E
test_api_full_mission_lifecycle()
```

## Adversarial Tests

```text
test_audit_chain_tamper_detection()
test_api_invalid_mission_id()
test_api_chaos_invalid_event_type()
test_api_evaluation_before_mission()
```

## Acceptance Criteria

- [ ] Audit ledger creates hash-chained events (§33)
- [ ] Chain tampering is detectable via `verify_chain()` (§33)
- [ ] Agent trace formatted per §35 with timestamped phase entries
- [ ] API serves all backend functionality via REST endpoints
- [ ] Single `backend/main.py` entry point
- [ ] WebSocket support for real-time trace updates

## Definition of Done

The API layer is complete. Every agent action is tamper-evidently audited. The decision trace is queryable. The system is fully controllable via REST API.

---

# PHASE 7: FRONTEND COMMAND CENTER

## Objective

Build the ULTRON Command Center UI (§34) with all required pages, real-time agent trace visualization, chaos controls, and counterfactual display. The frontend must display data generated from the simulation — no hardcoded numbers (§34).

## Dependencies

- Phase 6 complete (API)

## Files to Create/Modify

The frontend will be built in the existing `frontend/` directory using Vite + React + Tailwind (or the team's chosen stack decision from the architecture review).

### Pages Required (Spec §34)

| Route | Purpose |
|---|---|
| `/dashboard` | Revenue at risk, recovery, incremental, active missions, replans, escalations |
| `/missions` | Mission list |
| `/missions/:id` | Mission detail with agent trace (§35) |
| `/customers/:id` | Customer view with revenue episode |
| `/chaos` | Chaos injection controls (§31, §32) |
| `/evaluation` | Counterfactual results (§28) |
| `/audit` | Hash-chained audit trail (§33) |
| `/memory` | Episodic memory viewer (§26) |
| `/system` | LLM health, system status |

### Key Components

| Component | Purpose |
|---|---|
| `DashboardPage` | KPI cards with live data from simulation |
| `MissionTimeline` | Real-time agent trace visualization (§35) |
| `ChaosPanel` | 7 chaos event buttons that modify the actual world (§31-32) |
| `CounterfactualDisplay` | Control vs Treatment vs Incremental (§28) |
| `AuditChain` | Tamper-evident audit trail viewer (§33) |
| `RevenueEpisodeView` | Cross-channel revenue episode (§16) |
| `InterferenceGraph` | Revenue interference visualization (§27) |

## Implementation Sequence

1. Add routing (React Router)
2. Add Tailwind CSS (or chosen styling approach)
3. Build layout with navigation
4. Build `/dashboard` with live KPI cards
5. Build `/missions` list page
6. Build `/missions/:id` with agent trace timeline
7. Build `/customers/:id` with revenue episode
8. Build `/chaos` with 7 event type controls
9. Build `/evaluation` with counterfactual display
10. Build `/audit` with hash-chain viewer
11. Build `/memory` with episodic memory viewer
12. Build `/system` with LLM health status
13. Add WebSocket integration for real-time updates

## Tests

```text
# Component tests
test_dashboard_renders_without_error()
test_mission_list_renders()
test_chaos_panel_has_7_event_types()
test_counterfactual_display_shows_incremental()

# Integration
test_dashboard_fetches_from_api()
test_chaos_button_triggers_api_call()
test_mission_trace_updates_via_websocket()
```

## Adversarial Tests

```text
test_dashboard_handles_api_timeout()
test_dashboard_handles_empty_data()
test_mission_detail_handles_missing_mission()
```

## Acceptance Criteria

- [ ] All 9 routes from spec §34 exist and render
- [ ] Dashboard shows revenue at risk, recovery, incremental, missions, replans, escalations
- [ ] Every number on dashboard comes from simulation data, not hardcoded (§34)
- [ ] Chaos panel has 7 buttons matching spec §31 event types
- [ ] Pressing chaos button modifies actual simulation (§32)
- [ ] Agent trace shows timestamped decision steps per §35
- [ ] Counterfactual view shows Control / Treatment / Incremental (§28)
- [ ] Audit view shows hash-chained events (§33)

## Definition of Done

The ULTRON Command Center has all 9 pages. Every display is driven by simulation data. The judge can inject chaos via the UI, watch ULTRON replan in real time, and see the counterfactual proof of incremental recovery. The signature demo flow from §51 is achievable through the UI.

---

# IMPLEMENTATION-READINESS REPORT

## Summary

| Dimension | Status |
|---|---|
| Spec fully read and analyzed | ✅ Complete (52 sections, 1881 lines) |
| Repository fully inspected | ✅ Complete (all files examined) |
| Architecture contradictions identified | ✅ 12 contradictions documented |
| Missing structure identified | ✅ 18 missing components documented |
| Missing interfaces identified | ✅ 16 missing interfaces documented |
| Missing tests identified | ✅ 4 critical tests + full adversarial matrix documented |
| Implementation plan created | ✅ 8 phases with full detail |
| Dead code identified for removal | ✅ 16 files to delete |

## Phase Independence

Each phase can be independently developed, tested, and accepted:

```text
Phase 0: Foundation     → No dependencies
Phase 1: Financial World → Depends on Phase 0
Phase 2: Tools/Economics → Depends on Phase 1
Phase 3: Agent Core     → Depends on Phase 2
Phase 4: LLM Providers  → Depends on Phase 3
Phase 5: Simulator/Eval → Depends on Phase 1, Phase 3
Phase 6: API/Audit      → Depends on Phase 3, Phase 5
Phase 7: Frontend       → Depends on Phase 6
```

Note: Phase 4 and Phase 5 can be developed **in parallel** after Phase 3 completes.

## Estimated File Count

| Category | New | Modified | Deleted |
|---|---|---|---|
| Phase 0 | ~20 | 2 | 16 |
| Phase 1 | 4 | 7 | 0 |
| Phase 2 | 7 | 5 | 3 |
| Phase 3 | 3 | 6 | 0 |
| Phase 4 | 5 | 2 | 0 |
| Phase 5 | 5 | 2 | 0 |
| Phase 6 | 7 | 5 | 1 |
| Phase 7 | ~15 | 5 | 0 |
| **Total** | **~66** | **~34** | **~20** |

## Constraints Honored

- ❌ No application code written
- ❌ No unnecessary dependencies introduced
- ❌ No microservices proposed
- ❌ No financial rules invented
- ❌ No regulatory requirements fabricated
- ❌ No metrics fabricated
- ❌ No fake demo data created
- ✅ All requirements traced to spec sections
- ✅ All existing code reviewed for reuse potential
- ✅ Monolithic architecture preserved per spec §49

## Critical Risks

1. **LLM availability** — HuggingFace Inference has rate limits; local Qwen requires GPU memory management on 4GB VRAM
2. **Counterfactual isolation** — Must be verified with adversarial tests before any demo
3. **Simulation performance** — 200 customers × 30 days with event scheduling must complete in seconds
4. **Trust boundary integrity** — LLM output must never bypass Pydantic validation

## Awaiting Approval

This plan is ready for review. No implementation will begin until explicit approval is received.

Key decisions requiring your input:

1. **Frontend framework**: Spec says Next.js + Tailwind. Current repo has Vite + React. Keep Vite (pragmatic, already set up) or migrate to Next.js (spec-compliant)?
2. **Database**: Spec says "SQLite initially." Current code uses in-memory dicts. Introduce SQLite now, or keep in-memory for MVP and add SQLite later?
3. **Phase execution order**: Phases 4 and 5 can run in parallel. Preference?
