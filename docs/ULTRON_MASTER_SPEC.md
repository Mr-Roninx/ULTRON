
# ULTRON v3.2 — MASTER BUILD SPECIFICATION

**Project:** ULTRON v3.2
**Track:** AI Revenue Recovery
**Category:** Autonomous Fintech / Revenue Recovery Agent
**Development Environment:** Google Antigravity
**Primary Development Model:** Gemini 3.1 Pro High
**Architecture Review:** Claude Opus 4.5/available Opus equivalent
**Adversarial Review:** Gemini 3.7 Flash
**Runtime Primary LLM:** Hugging Face Inference Provider
**Runtime Fallback:** Local Qwen3-4B
**Backend:** Python + FastAPI
**Agent:** LangGraph/state-machine architecture
**Frontend:** Next.js + React + Tailwind
**Database:** SQLite initially; PostgreSQL-ready architecture
**Simulation:** Deterministic discrete-event simulator
**Deployment:** Local-first, cloud-ready

---

# 1. MASTER OBJECTIVE

Build ULTRON as a **real autonomous revenue-recovery agent**, not a dashboard, recommendation engine, chatbot, retry scheduler, or collection CRM.

ULTRON must operate inside a simulated financial world.

Its fundamental loop is:

```text
OBSERVE
   ↓
INVESTIGATE
   ↓
UNDERSTAND
   ↓
FORM HYPOTHESIS
   ↓
PLAN
   ↓
CHECK FEASIBILITY
   ↓
CHECK AUTHORITY
   ↓
CHECK RISK
   ↓
EXECUTE
   ↓
WAIT
   ↓
OBSERVE RESULT
   ↓
COMPARE PREDICTION vs REALITY
   ↓
LEARN
   ↓
REPLAN IF NECESSARY
```

The defining property is:

> **ULTRON acts, observes the consequence of its action, and changes its plan when reality contradicts its expectation.**

---

# 2. WHAT ULTRON IS SOLVING

Revenue leakage is not necessarily one isolated payment failure.

A customer can simultaneously have:

```text
Payment failure
      +
Checkout abandonment
      +
Invoice overdue
      +
Gateway degradation
      +
Customer communication fatigue
```

Existing systems typically operate inside individual silos.

ULTRON creates a unified revenue state.

The system asks:

> **"Given everything currently happening around this customer and across the merchant's revenue system, what should ULTRON do next, and what is the measurable incremental revenue impact of doing it?"**

---

# 3. WHAT ULTRON IS NOT

Do not allow the implementation to drift into:

```text
❌ CRM
❌ dashboard
❌ payment retry cron
❌ chatbot
❌ static scoring model
❌ email generator
❌ generic RAG application
❌ LLM wrapper
❌ collection reminder system
❌ hardcoded demo
```

ULTRON must demonstrate autonomous behavior.

---

# 4. THE CORE DIFFERENTIATOR

ULTRON combines five capabilities:

### 1. Financial-state awareness

It understands asynchronous payment states.

### 2. Cross-channel revenue reasoning

It sees payment, checkout and invoice events together.

### 3. Autonomous action

It executes bounded recovery actions.

### 4. Closed-loop adaptation

It observes outcomes and replans.

### 5. Counterfactual measurement

It measures:

```text
What happened with ULTRON
vs.
What would have happened without ULTRON
```

The fifth point is especially important.

Do not simply claim:

> "We recovered ₹10 lakh."

Show:

```text
CONTROL:
₹6.8L

ULTRON:
₹9.4L

INCREMENTAL:
₹2.6L
```

---

# 5. HIGH-LEVEL ARCHITECTURE

```text
                         ┌─────────────────────┐
                         │      ULTRON UI      │
                         │   Command Center    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Mission API      │
                         │      FastAPI        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │      ULTRON AGENT CORE        │
                    │                               │
                    │ Observe → Investigate         │
                    │ Plan → Validate → Act         │
                    │ Wait → Observe → Replan       │
                    └──────────────┬────────────────┘
                                   │
          ┌────────────────────────┼─────────────────────────┐
          │                        │                         │
          ▼                        ▼                         ▼
   ┌──────────────┐       ┌────────────────┐       ┌───────────────┐
   │ LLM Gateway  │       │ Deterministic  │       │ Tool Gateway  │
   │              │       │ Decision Core  │       │               │
   │ HF Cloud     │       │                │       │ Payment       │
   │      ↓       │       │ FSM            │       │ Reconcile     │
   │ Qwen3-4B     │       │ Policy         │       │ Message       │
   │ fallback     │       │ Risk           │       │ PTP           │
   └──────────────┘       │ Economics      │       │ Escalate      │
                          └────────────────┘       └───────────────┘
                                   │
                                   ▼
                       ┌─────────────────────┐
                       │  SIMULATED WORLD    │
                       │                     │
                       │ Customers           │
                       │ Payments            │
                       │ Gateway             │
                       │ Checkout            │
                       │ Invoices            │
                       │ Communications      │
                       │ Virtual Clock       │
                       └──────────┬──────────┘
                                  │
                                  ▼
                        ┌─────────────────────┐
                        │ Evaluation Engine   │
                        │                     │
                        │ Control             │
                        │ Treatment           │
                        │ Incremental ₹       │
                        └─────────────────────┘
```

---

# 6. CRITICAL TRUST BOUNDARY

The most important architectural rule:

```text
                 LLM
                  │
                  │ proposes
                  ▼
            Structured Intent
                  │
                  ▼
             Pydantic
                  │
                  ▼
            Feasibility
                  │
                  ▼
             Authority
                  │
                  ▼
               Risk
                  │
                  ▼
              Financial FSM
                  │
                  ▼
              Executor
                  │
                  ▼
             Financial World
```

Never:

```text
LLM → database
```

Never:

```text
LLM → payment state
```

Never:

```text
LLM → raw payment API
```

---

# 7. LLM RESPONSIBILITY

The LLM may:

* investigate
* interpret evidence
* classify ambiguous information
* form hypotheses
* choose between deterministic candidate strategies
* generate communication
* explain its decision
* decide which tool to call next

The LLM may **not** own:

* financial arithmetic
* payment state
* compliance rules
* authorization
* risk limits
* counterfactual truth
* recovery metrics
* audit integrity

---

# 8. LLM PROVIDER ARCHITECTURE

Create:

```text
backend/
└── llm/
    ├── base.py
    ├── huggingface.py
    ├── local_qwen.py
    ├── router.py
    └── schemas.py
```

Interface:

```python
class LLMProvider:
    async def generate(...)
    async def structured(...)
    async def health(...)
```

Providers:

```text
HuggingFaceProvider
LocalQwenProvider
```

Router:

```text
AUTO
 │
 ▼
Hugging Face
 │
 ├── success → continue
 │
 └── failure
       ↓
   local Qwen3-4B
```

Record every fallback.

Example:

```json
{
  "event": "LLM_PROVIDER_FALLBACK",
  "from": "huggingface",
  "to": "local_qwen",
  "reason": "timeout"
}
```

---

# 9. HUGGING FACE

Do not hardcode one provider into ULTRON.

Use configuration:

```env
ULTRON_LLM_PROVIDER=auto

HF_TOKEN=
HF_MODEL=

LOCAL_LLM_URL=http://localhost:8000/v1
LOCAL_LLM_MODEL=
```

HF's current Inference Providers provide unified access to models and providers, but usage beyond included credits is billed, so the application must gracefully handle quota/rate-limit/provider failures. ([Hugging Face][2])

---

# 10. LOCAL MODEL

Your machine:

```text
16 GB RAM
GTX 1650 4 GB VRAM
```

Therefore do not attempt to make a 70B-class model your local fallback.

Use a small quantized Qwen model suitable for your hardware.

Expose it behind an OpenAI-compatible interface.

ULTRON sees:

```text
LLMProvider
```

not:

```text
Qwen
```

This keeps the runtime model replaceable.

---

# 11. PAYMENT WORLD

ULTRON needs a realistic payment lifecycle.

Minimum:

```text
CREATED
INITIATED
AUTHORIZING
AUTHORIZED
CAPTURED
SETTLED
FAILED
UNKNOWN
RECONCILING
REVERSED
REFUNDED
```

Example:

```text
INITIATED
    ↓
AUTHORIZING
    ↓
UNKNOWN
    ↓
RECONCILING
    ↓
FAILED
```

The UNKNOWN state is crucial.

It represents:

> "We do not yet know the authoritative financial outcome."

ULTRON must **not blindly retry** in UNKNOWN.

---

# 12. PAYMENT FAILURE INTELLIGENCE

Build:

```text
FailureNormalizer
FailureClassifier
RetryabilityResolver
ReconciliationResolver
```

Classifications:

```text
TRANSIENT
CUSTOMER_ACTION_REQUIRED
CREDENTIAL_PROBLEM
LIQUIDITY_RELATED
GATEWAY_PROBLEM
UNKNOWN
NON_RETRYABLE
```

Do not hardcode unsupported universal mappings.

Provider-specific mappings must be configuration data.

---

# 13. WORLD MODEL

Start small.

Do not create ten databases.

MVP entities:

```text
Customer
Payment
PaymentAttempt
Invoice
CheckoutSession
Gateway
RecoveryAction
Communication
Mission
Event
```

All state changes produce events.

There should be **one source of truth**.

---

# 14. EVENT MODEL

Do not independently generate:

```text
payment_failed
```

in one table and:

```text
payment.failed
```

somewhere else.

Instead:

```text
Payment state transition
       ↓
Domain event
       ↓
Event store / stream
```

Example:

```json
{
  "event_id": "EV-1021",
  "type": "PAYMENT_FAILED",
  "payment_id": "PAY-10",
  "timestamp": 1200
}
```

---

# 15. VIRTUAL CLOCK

Never use real `sleep()` for the simulator.

Build:

```python
VirtualClock
```

with:

```text
now()
advance()
schedule()
cancel()
next_event()
run_until()
```

Example:

```text
09:00 payment fails

ULTRON schedules recovery at 13:00

simulation advances:

09:00
09:30
10:00
...
13:00

action executes
```

A 30-day simulation should run in seconds.

---

# 16. REVENUE EPISODE

ULTRON should not see three unrelated problems.

Example:

```text
Customer C001

Payment failure: ₹8,200
Checkout abandoned: ₹4,500
Invoice overdue: ₹12,000
```

ULTRON creates:

```text
Revenue Episode
```

with:

```text
total_exposure = ₹24,700
```

Now it can reason about the customer holistically.

---

# 17. AGENT MISSION

Every ULTRON mission should contain:

```text
mission_id
objective
starting_state
observations
hypotheses
plans
actions
results
prediction_errors
replans
final_outcome
```

Example:

```json
{
  "mission_id": "M001",
  "objective": "recover_revenue",
  "status": "ACTIVE"
}
```

---

# 18. AGENT STATES

Use:

```text
OBSERVE
INVESTIGATE
HYPOTHESIZE
PLAN
FEASIBILITY_CHECK
AUTHORITY_CHECK
RISK_CHECK
EXECUTE
WAIT
EVALUATE
LEARN
REPLAN
ESCALATE
COMPLETE
```

---

# 19. BOUNDED AGENT LOOP

Never allow:

```text
while True
```

Use:

```text
MAX_STEPS = 12
MAX_REPLANS = 5
MAX_IDENTICAL_FAILURES = 2
```

If the same action fails twice:

```text
ESCALATE
```

or:

```text
COOLDOWN
```

---

# 20. TOOLS

ULTRON should have a small tool surface.

### Investigation

```text
get_customer_context
get_payment
get_payment_attempts
get_invoice
get_checkout_session
get_gateway_health
get_related_events
get_previous_episodes
```

### Decision

```text
get_feasible_actions
calculate_action_value
```

### Execution

```text
reconcile_payment
schedule_retry
generate_payment_link
send_customer_message
register_ptp
escalate_to_human
```

---

# 21. TOOL CONTRACT

Every tool must:

```text
validate input
      ↓
validate state
      ↓
validate authority
      ↓
execute
      ↓
emit event
      ↓
return structured result
```

Example:

```json
{
  "success": true,
  "action_id": "ACT-22",
  "state_change": "WAITING_FOR_RETRY"
}
```

---

# 22. FEASIBLE ACTION SET

For each opportunity:

```text
possible actions
      ↓
remove impossible
      ↓
remove policy-prohibited
      ↓
remove authority-prohibited
      ↓
remove excessive-risk
      ↓
rank remaining
```

The LLM should preferably choose from this already-valid action set.

---

# 23. ECONOMIC ENGINE

Do not let the LLM calculate:

```text
₹7,800 × probability
```

Python should calculate:

```text
expected_recovery
− operational_cost
− relationship_cost
− risk_cost
```

Example:

```text
NetExpectedValue =
ExpectedRecovery
- ActionCost
- RelationshipCost
- RiskCost
```

All units must be explicit.

---

# 24. RECOVERY STRATEGY

Possible actions:

```text
WAIT
RECONCILE
RETRY
REQUEST_CUSTOMER_ACTION
SEND_PAYMENT_LINK
SEND_MESSAGE
REGISTER_PTP
ESCALATE
STOP
```

The action itself must be rail-aware.

Do not assume:

> "payment failed → silent retry."

That would recreate one of the weaknesses we identified earlier.

---

# 25. RELATIONSHIP STATE

Do not invent a mysterious:

```text
relationship_score = 0.91
```

unless the calculation is defined.

Instead store observable signals:

```text
recent_contacts
recent_responses
successful_prior_recoveries
customer_value
complaints
opt_out
silence_duration
```

Then calculate a deterministic relationship-cost proxy.

---

# 26. MEMORY

Start with exact episodic memory.

Do not begin with pgvector.

Example:

```json
{
  "customer_id": "C100",
  "failure": "INSUFFICIENT_FUNDS",
  "action": "WAIT_24H",
  "result": "RECOVERED"
}
```

Next time:

```text
C100
↓
similar situation
↓
retrieve episode
↓
modify plan
```

That is enough to demonstrate memory.

Semantic/vector memory can become a later extension.

---

# 27. INTERFERENCE ENGINE

This is one of ULTRON's strongest differentiators.

ULTRON should discover relationships such as:

```text
Payment failure
       ↓
Checkout abandonment
       ↓
Invoice delay
```

Calculate:

```text
P(B | A)
P(B | not A)
```

Then:

```text
ExcessProbability =
P(B | A) - P(B | not A)
```

Call this:

> **Interference Score**

Do not incorrectly call it "causal lift."

---

# 28. COUNTERFACTUAL ENGINE

This is mandatory.

At decision time:

```text
WORLD STATE
     │
     ├──────────────┐
     ▼              ▼
CONTROL          TREATMENT
No action        ULTRON action
     │              │
     ▼              ▼
Outcome          Outcome
     │              │
     └──────┬───────┘
            ▼
    Incremental Recovery
```

Both worlds must start from identical state.

Use deterministic seeds.

The agent must never see the control outcome.

---

# 29. EVALUATOR ISOLATION

This is extremely important.

```text
Agent
  │
  ▼
Observable World
```

separate from:

```text
Evaluator
  │
  ├── Control
  └── Treatment
```

Never expose:

```text
baseline_outcome
treatment_outcome
incremental_recovery
```

to ULTRON before it acts.

Otherwise your experiment is contaminated.

---

# 30. PREDICTION ERROR

Before action:

```text
PredictedRecovery = ₹8,000
```

After action:

```text
ActualRecovery = ₹12,000
```

Then:

```text
PredictionError = ₹4,000
```

If sufficiently large:

```text
REPLAN
```

This is what makes ULTRON an adaptive agent.

---

# 31. CHAOS ENGINE

Build judge-triggerable events:

```text
UPI_DEGRADATION
GATEWAY_TIMEOUT
WEBHOOK_DELAY
GATEWAY_RECOVERY
MASS_CHECKOUT_ABANDONMENT
CUSTOMER_SILENCE
PAYMENT_STATE_AMBIGUITY
```

The chaos event must modify the **actual simulated world**.

Not merely:

```text
change UI number
```

---

# 32. THE SIGNATURE DEMO

Judge clicks:

> **UPI degradation 80%**

The actual simulator changes.

ULTRON observes:

```text
Gateway health ↓
```

Existing plan:

```text
USE UPI
```

becomes invalid.

ULTRON:

```text
prediction error
        ↓
invalidate plan
        ↓
investigate alternatives
        ↓
feasibility
        ↓
risk
        ↓
new action
        ↓
execute
```

That is the moment that proves autonomy.

---

# 33. AUDIT LEDGER

Every meaningful action becomes:

```text
AuditEvent
```

Fields:

```text
event_id
mission_id
timestamp
actor
event_type
input_hash
previous_hash
current_hash
```

Create:

```text
HASH(event + previous_hash)
```

This creates a tamper-evident chain.

Do not overclaim that this alone provides regulatory compliance.

Call it:

> **Tamper-evident audit trail.**

---

# 34. FRONTEND

ULTRON Command Center:

```text
/dashboard
/missions
/missions/:id
/customers/:id
/chaos
/evaluation
/audit
/memory
/system
```

The primary screen should show:

```text
REVENUE AT RISK
₹X

ULTRON RECOVERY
₹Y

INCREMENTAL
₹Z

ACTIVE MISSIONS
N

REPLANS
N

ESCALATIONS
N
```

But every number must be generated from the simulation.

---

# 35. AGENT TRACE

Show:

```text
10:01:02 OBSERVE
Payment PAY-104 failed

10:01:03 INVESTIGATE
Gateway health checked

10:01:04 HYPOTHESIS
Transient gateway degradation

10:01:05 PLAN
Wait for gateway recovery

10:01:06 AUTHORITY
PASS

10:01:06 RISK
PASS

10:01:07 EXECUTE
WAIT

10:03:21 CHAOS
UPI degradation 80%

10:03:22 OBSERVE
Prediction invalidated

10:03:23 REPLAN

10:03:25 EXECUTE
Alternative recovery action

10:03:31 RECOVERED
₹8,200
```

---

# 36. DATASET

MVP:

```text
200 customers
2,000 payments
300 invoices
500 checkout sessions
```

Do not start with 50,000+ rows.

The goal is reproducibility, not big-data theater.

Generate:

```text
customers.json
payments.json
invoices.json
checkout_sessions.json
```

But domain events should be generated from state transitions.

---

# 37. DATA GENERATION

Use:

```text
seed
```

Example:

```python
world = World(seed=42)
```

Running:

```text
seed = 42
```

must produce the same world.

That allows judges to reproduce results.

---

# 38. TESTING

You need four layers.

### Unit

```text
FSM
policy
risk
economics
clock
memory
classifier
```

### Integration

```text
agent → tool → simulator
```

### Scenario

```text
payment failure
unknown state
gateway outage
checkout abandonment
invoice overdue
```

### Adversarial

```text
LLM malformed JSON
LLM timeout
duplicate action
invalid transition
future-data leakage
infinite loop
policy bypass
tool failure
```

---

# 39. THE MOST IMPORTANT TEST

Write:

```text
test_agent_cannot_access_future_outcome()
```

Verify that:

```text
agent_context
```

does not contain:

```text
baseline_outcome
actual_recovery
counterfactual_recovery
```

before action completion.

This protects your biggest credibility claim.

---

# 40. SECOND CRITICAL TEST

```text
test_unknown_payment_blocks_duplicate_action()
```

Scenario:

```text
payment initiated
gateway timeout
payment UNKNOWN
```

ULTRON must not:

```text
retry
```

until reconciliation determines the state.

---

# 41. THIRD CRITICAL TEST

```text
test_chaos_causes_replan()
```

Expected:

```text
initial_plan != final_plan
```

after chaos changes the environment.

This proves that ULTRON isn't simply replaying a predetermined script.

---

# 42. FOURTH CRITICAL TEST

```text
test_recovery_metric_is_counterfactual()
```

Verify:

```text
incremental =
treatment_outcome - control_outcome
```

and not:

```text
incremental = treatment_outcome
```

---

# 43. DEVELOPMENT PHASES

## Phase 0

Repository + rules + architecture.

## Phase 1

World model.

## Phase 2

Virtual clock.

## Phase 3

Financial FSM.

## Phase 4

Failure intelligence.

## Phase 5

Tool gateway.

## Phase 6

Policy/authority/risk.

## Phase 7

Agent loop.

## Phase 8

Recovery economics.

## Phase 9

Prediction-error replanning.

## Phase 10

Memory.

## Phase 11

Revenue episodes.

## Phase 12

Interference.

## Phase 13

Counterfactual evaluator.

## Phase 14

Chaos engine.

## Phase 15

Audit.

## Phase 16

API.

## Phase 17

Frontend.

## Phase 18

Adversarial testing.

## Phase 19

Benchmark.

## Phase 20

Demo hardening.

---

# 44. ANTIGRAVITY OPERATING PROTOCOL

For each phase:

```text
/grill-me
```

if architecture is unclear.

Then:

```text
/plan
```

Antigravity's current `/plan` workflow analyzes the repository and produces a reviewable implementation-plan artifact before execution. ([Google Antigravity][3])

Review it.

Then:

```text
Proceed
```

After implementation:

```text
run tests
```

Then ask:

```text
Break what you just built.
```

Fix the failures.

Only then start the next phase.

---

# 45. USE ANTIGRAVITY RULES

Create:

```text
.agents/rules/
```

with:

```text
ultron-core.md
financial-safety.md
agent-development.md
testing.md
frontend.md
```

Antigravity currently uses `.agents/rules` for workspace rules, and these rules can be always-on, manually invoked, model-selected, or glob-scoped. ([Google Antigravity][4])

---

# 46. CREATE A WORKFLOW

Create:

```text
.agents/workflows/ultron-phase.md
```

Workflow:

```text
Inspect
 ↓
Read specification
 ↓
Check existing code
 ↓
Plan
 ↓
Implement
 ↓
Test
 ↓
Adversarial test
 ↓
Fix
 ↓
Document
```

Antigravity workflows are reusable Markdown-based procedures invoked through slash commands. ([Google Antigravity][5])

Then:

```text
/ultron-phase
```

becomes your standard development command.

---

# 47. MODEL STRATEGY

Your development model division should be:

| Work                            | Model               |
| ------------------------------- | ------------------- |
| Architecture attack             | Opus                |
| Independent architecture attack | Gemini 3.7 Flash    |
| Final architecture              | Gemini 3.1 Pro High |
| Repository implementation       | Gemini 3.1 Pro High |
| Small refactor                  | Gemini 3.7 Flash    |
| UI work                         | Gemini 3.7 Flash    |
| Difficult debugging             | Gemini 3.1 Pro High |
| Final code review               | Gemini 3.7 Flash    |
| Runtime primary                 | Hugging Face        |
| Runtime fallback                | Qwen3-4B            |

Gemini 3.7 Flash is currently positioned by Google as a workhorse for coding and agentic tasks, while Antigravity supports agentic development across editor, terminal and browser. ([Google Blog][6])

---

# 48. IMPORTANT ANTIGRAVITY SETTING

During the early build, keep **Plan/Review mode**, not unrestricted autonomous execution.

Antigravity's current documentation recommends the review-oriented workflow for implementation plans; its "Always Proceed" mode skips manual approval. ([Google Antigravity][7])

For ULTRON:

```text
Architecture → Review
Financial FSM → Review
Agent Core → Review
Counterfactual Engine → Review
Chaos Engine → Review
```

You can use faster execution later for trivial changes.

---

# 49. DO NOT LET ANTIGRAVITY DO THIS

If it proposes:

```text
"Let's add 12 microservices..."
```

Reject.

If it proposes:

```text
"Let's use PostgreSQL, Redis, Kafka, Celery, Temporal..."
```

before the core agent works:

Reject.

If it proposes:

```text
"Let's use an LLM to calculate expected recovery..."
```

Reject.

If it proposes:

```text
"Let's hardcode the demo outcome..."
```

Reject.

If it proposes:

```text
"Let's store the counterfactual in the agent context..."
```

Reject.

If it proposes:

```text
"Let's make the agent automatically retry every failed payment..."
```

Reject.

---

# 50. THE MINIMUM WINNING PRODUCT

If time collapses, protect these seven things:

```text
1. Financial FSM
2. Virtual simulator
3. Real agent loop
4. Tool authority boundary
5. Chaos → replan
6. Counterfactual evaluation
7. Live audit trace
```

Everything else is secondary.

---

# 51. THE FINAL DEMO

### 0:00 — Problem

Show:

```text
₹X revenue at risk
```

across:

```text
payment
checkout
invoice
```

---

### 0:30 — ULTRON investigates

Show the agent querying:

```text
payment
gateway
customer
related revenue events
```

---

### 1:00 — First action

ULTRON executes a valid recovery action.

---

### 1:30 — Chaos

Judge presses:

> **UPI degradation 80%**

---

### 2:00 — ULTRON realizes its plan is wrong

Show:

```text
PREDICTION ERROR
```

---

### 2:20 — Replan

Show:

```text
PLAN INVALIDATED
```

then a new plan.

---

### 3:00 — Recovery

Show:

```text
₹X recovered
```

---

### 3:30 — Counterfactual

Show:

```text
WITHOUT ULTRON
₹A

WITH ULTRON
₹B

INCREMENTAL
₹B - ₹A
```

---

### 4:00 — Audit

Open:

```text
OBSERVE
INVESTIGATE
PLAN
AUTHORIZE
ACT
OBSERVE
ERROR
REPLAN
ACT
RECOVER
```

---

### 4:30 — Final statement

> **"ULTRON doesn't predict revenue loss and tell someone what to do. It enters the revenue system, investigates the failure, takes a bounded action, observes what happened, changes its plan when reality changes, and measures the revenue it recovered that would otherwise have been lost."**

---

# 52. THE FINAL BUILD PHILOSOPHY

Do not attempt to make ULTRON look intelligent.

Make it **behave intelligently**.

The judge should be able to break its environment.

Then ULTRON should:

```text
notice
understand
adapt
act
recover
prove
```

That is the entire project.
