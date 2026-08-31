# ULTRON v3.2 — Phase 10 Architecture Review

**Date:** 2026-08-28
**Phase:** 10 (Benchmark, Counterfactual Evaluation & Incremental Revenue Proof)
**Objective:** Review existing architecture for benchmark readiness and outline the Phase 10 benchmark framework implementation.

---

## 1. Existing System Components & Readiness

### 1.1 The World Simulator (`simulator/world.py`)
- **Isolation Capability:** `FinancialWorld` implements a `snapshot()` method which returns a `copy.deepcopy()` of all customers, payments, invoices, checkouts, and events. This is the cornerstone of the benchmark framework, allowing us to safely branch into Control (baselines) and Treatment (ULTRON) from identical states.
- **Clock Management:** `VirtualClock` maintains a deterministic priority queue. Benchmarks will require precise clock manipulation (e.g., advancing time uniformly across isolated branches).
- **Chaos Engine:** `ChaosEngine` now has 7 discrete, deterministic event types. This allows injecting precise, identical disruptions across all baseline and treatment branches.

### 1.2 The Counterfactual Evaluator (`evaluator/counterfactual.py`)
- Currently, `CounterfactualEvaluator.calculate_regret()` evaluates the net expected value (NEV) of alternative actions during execution. 
- While it correctly leverages `FinancialWorld.snapshot()` for isolated exploration, it currently operates at the *single-action* level. The benchmark framework must extend this to evaluate entire *episodes* over time.

### 1.3 The Economic Engine (`backend/economics/engine.py` & `relationship.py`)
- Calculates `NEV = ExpectedRecovery - ActionCost - RelationshipCost - RiskCost`.
- This engine will be the ground truth for evaluating both baselines and ULTRON in the benchmark matrix. All strategies will be scored on final recovered revenue and cumulative action/relationship costs.

---

## 2. Benchmark Framework Architecture

The benchmark framework will sit in `backend/benchmark/` and will consist of the following primary components:

### 2.1 The Strategies
We will implement an abstract `BenchmarkStrategy` class and the following concrete implementations:
1. **`NoActionBaseline`**: Does nothing. Lets the clock advance and payments naturally fail or settle via existing gateway retry logic.
2. **`FixedRetry`**: Retries failed payments exactly once after 24 hours.
3. **`TraditionalDunning`**: Sends a sequence of payment links at T+1, T+3, T+7 days.
4. **`RuleBasedRecovery`**: Executes simple rules (e.g., if segment == "ENTERPRISE", escalate; if "RETAIL", send link).
5. **`UltronAgentStrategy`**: The full ULTRON v3.2 agent loop (`AgentLoop`).

### 2.2 Ablation Matrix
For the `UltronAgentStrategy`, we will support configuration flags to run ablation studies:
- `disable_interference`: Disables temporal association graph logic.
- `disable_memory`: Runs without `EpisodicMemory`.
- `disable_replanning`: Forces the agent to act without the ability to replan.
- `disable_relationship_cost`: Removes relationship proxy calculations from NEV.

### 2.3 The Benchmark Runner (`backend/benchmark/runner.py`)
- **Initialization**: Will use a seeded generator to create a canonical start state.
- **Execution Loop**: For each strategy in the suite, it will:
  1. Restore the canonical world state via deep copy.
  2. Instantiate the strategy.
  3. Enter an event loop spanning $T$ days.
  4. At each tick, the strategy observes the world and injects actions.
  5. The clock advances, and events (including chaos) resolve.
  6. Final state is evaluated via `economic_engine`.
- **Output**: Generates `docs/PERFORMANCE_REPORT_PHASE_10.md` detailing the incremental revenue recovered compared to the baselines.

### 2.4 Future Information Firewall (`tests/benchmark/test_future_information_firewall.py`)
- Ensures strict causal isolation. 
- The firewall will cryptographically seal the future events in the simulator and verify that no agent prompt, observation, or execution path reads the state of the simulation at time $t' > t$ where $t$ is the current agent clock time.

---

## 3. Implementation Sequence

1. **Verify Isolation**: Enhance tests to prove that `FinancialWorld.snapshot()` guarantees no state leakage.
2. **Implement Strategies**: Build the baselines in `backend/benchmark/baselines.py`.
3. **Implement Runner**: Build the runner in `backend/benchmark/runner.py` with ablation support.
4. **Implement Firewall**: Build the future information firewall test.
5. **Execution**: Run the full matrix on a complex seeded scenario (combining chaos events with Ananya Textiles / scaled data).
6. **Reporting**: Produce `docs/PHASE_10_EVALUATION_REPORT.md` showcasing the incremental recovered revenue proof.
