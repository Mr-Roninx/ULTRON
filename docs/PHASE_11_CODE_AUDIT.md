# ULTRON v3.2 → v3.3 Phase 11 Code Audit
### Benchmark Integrity, Causal Mechanism Activation & Risk Policy Calibration

**Date:** 2026-08-28  
**Status:** Complete

---

## 1. Existing Architecture
The current architecture evaluates `UltronStrategy` by pulling opportunities from the static `canonical_world.snapshot()`. The benchmark engine iterates through every opportunity synchronously, instantiating an `AgentLoop` that evaluates the state and executes exactly one intervention, immediately reaching the `COMPLETE` or `ESCALATE` state.

## 2. Existing Execution Flow
- `runner.py` invokes `UltronStrategy.run()`.
- `UltronStrategy.run()` loops sequentially through `opportunities`.
- For each opportunity, `AgentLoop` executes the 13-state FSM.
- Action (e.g. `SEND_PAYMENT_LINK`, `WAIT`, `RETRY`) is determined.
- `simulator_dynamics` processes the action and schedules future outcomes in the `VirtualClock`.
- Once all opportunities are evaluated, `runner.py` executes `clock.advance(horizon_seconds)`.
- Final financial metrics are computed.

## 3. Actual AgentLoop Behavior
The `AgentLoop` executes exactly once per opportunity at $T=0$. It does not sleep, yield, or wake up at a future date to re-evaluate customer state. Once an action is scheduled (e.g. `RETRY`), the FSM terminates. 

## 4. Actual Benchmark Behavior
Because the benchmark only executes strategies at $T=0$, then jumps the clock to $T=\text{horizon}$, the simulation lacks continuous temporal evaluation. Baselines and ULTRON both make a single static pass.

## 5. Why Ablations Currently Produce Identical Results
- **ULTRON_NO_MEMORY:** With a single pass at $T=0$, no prior episodes exist to recall.
- **ULTRON_NO_REPLANNING:** Because execution is instantaneous at $T=0$, no environmental changes occur *during* the agent's decision cycle that would invalidate a plan and trigger a replan.
- **ULTRON_NO_DECAY:** No significant time passes between decisions for a single customer, so decay functions operate on $\Delta t = 0$.
- **ULTRON_NO_INTERFERENCE:** Opportunities are evaluated independently. Customer-level correlated risk graph is not consulted.

## 6. Why Horizon Results Repeat
The agent makes all its decisions at $T=0$. Whether the horizon is 7, 14, 30, or 60 days, the agent's initial interventions are identical. Natural recovery occurs differently over these horizons, but since no *new* agent actions are dispatched based on delayed customer responses, the agent's gross recovery remains static.

## 7. Why Chaos Results Repeat
Chaos scenarios (e.g., `GATEWAY_TIMEOUT`, `WEBHOOK_DELAY`) manifest as temporal events. Because the agent only evaluates at $T=0$, it never experiences the delay or the subsequent recovery, and therefore cannot react dynamically to mitigate the chaos.

## 8. Why Replans Are Zero in Clean Benchmark
Replanning requires an asynchronous observation loop where an initial plan (e.g., "Retry via Gateway A in 4 hours") is interrupted by an environmental change ("Gateway A down") when the agent wakes up to execute. Since execution happens instantaneously at $T=0$, no interruptions occur.

## 9. Current Risk Decision Logic
The `EconomicEngine` calculates risk cost as: `RiskCost = ExpectedRecovery * RiskScore`. The `ExpectedRecovery` is often statically guessed or provided by the LLM. This heavily penalizes high-value invoices with even slight risk scores, forcing the agent to conservatively choose `WAIT` rather than risk the relationship, resulting in under-recovery.

## 10. Proposed Minimal Changes
- **Temporal Event Loop:** Rewrite `runner.py` and `UltronStrategy.run()` to operate in an event-driven loop. The agent must be able to schedule a `WAKEUP` event in the `VirtualClock` and re-enter the `AgentLoop`.
- **Deterministic NEV Ranking:** Remove LLM expected yield guessing. Calculate deterministic NEV for all feasible actions and select the highest NEV action.
- **Multi-Episode Memory:** Persist `EpisodeRecord` across time ticks and customer interactions.
- **Interference Graph:** Group opportunities by `customer_id` and evaluate customer-level exposure before acting.
- **Calibrated Risk Policy:** Use a multi-tier confidence system (High, Medium, Low Confidence) and bound risk cost relative to true LTV.

## 11. Files Requiring Modification
- `simulator/clock.py` (Add robust event stepping API)
- `backend/benchmark/runner.py` (Implement continuous time-stepped simulation)
- `backend/benchmark/ultron_strategy.py` (Support multi-tick re-evaluations)
- `backend/agent/loop.py` (Support yielding at `WAIT` and waking up)
- `backend/economics/engine.py` (Deterministic NEV calculation & Action ranking)
- `backend/evaluator/counterfactual.py` (Support new NEV metrics)

## 12. New Files Required
- `backend/benchmark/longitudinal.py` (Class C benchmark)
- `tests/benchmark/test_horizon_sensitivity.py`
- `tests/benchmark/test_memory_causality.py`
- `tests/benchmark/test_interference_causality.py`
- `tests/benchmark/test_replanning_causality.py`
- `tests/benchmark/test_chaos_causality.py`

## 13. Regression Risks
- **Future Information Leakage:** Waking the agent dynamically risks leaking future simulation state into the agent's context if the firewall is not tightly coupled to the `VirtualClock`'s current tick.
- **Counterfactual Integrity:** Introducing longitudinal memory might bleed between treatment and control if `memory_store` is not explicitly branched per simulation run.
