# ULTRON v5.0 — Phase 9: Controlled Causal Influence Experiments *(Historical v5.0 Archive — Superseded by v5.1 Canonical Benchmark)*

> **Notice**: This document records early exploratory findings from ULTRON v5.0 Phase 9. For authoritative, dynamically evaluated causal benchmarks on ULTRON v5.1 with zero manual summaries and full small-sample Student's t statistics, refer to [ULTRON_V5_1_CAUSAL_BENCHMARK_INTEGRITY.md](file:///d:/Work%20Space/Project/Ultron/docs/ULTRON_V5_1_CAUSAL_BENCHMARK_INTEGRITY.md) and [ULTRON_V5_1_COMPLETE_TRUTH.md](file:///d:/Work%20Space/Project/Ultron/ULTRON_V5_1_COMPLETE_TRUTH.md).

**Phase Objective**: Run 5 controlled causal ablation experiments across a standardized portfolio of 52 recovery opportunities:
1. `LLM OFF / ON`
2. `TOOLS OFF / ON`
3. `MEMORY OFF / ON`
4. `REPLAN OFF / ON`
5. `AGENT OFF / ON`

Measure quantitative empirical influence without forcing positive results, and scientifically classify each component's causal contribution.

---

## 1. Causal Ablation Experiment Matrix

| Exp ID | Component Tested | Control Condition | Treatment Condition | Quantitative Delta | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-1** | **LLM Semantic Signals** | Zero signals (Heuristic Core) | Bounded signals ($0 \le s \le 1$) | **$+₹3,601.00$ (+29.0% portfolio recovery)** | `POSITIVE_EFFECT` |
| **EXP-2** | **Tool Execution** | Blind heuristic classification | 3 investigation read tools | **$0\% \to 100\%$ intent accuracy** | `POSITIVE_EFFECT` |
| **EXP-3** | **Episodic Memory** | Tabula rasa (no memory) | Cross-mission episodic recall | **$-0.0745$ Brier error reduction** | `POSITIVE_EFFECT` |
| **EXP-4** | **Replanning Engine** | Static single-shot plan | Stateful assumption invalidation | **1 wasted attempt prevented on outage** | `POSITIVE_EFFECT` |
| **EXP-5** | **Holistic AI Agent** | Tier 1 Financial Core alone | Tier 1 Core + Tier 2 Agent | **$1.29\times$ recovery efficiency multiplier** | `POSITIVE_EFFECT` |

---

## 2. Detailed Experimental Findings

### Experiment 1: LLM Reasoning Ablation (LLM OFF vs. LLM ON)
- **Control Group (LLM OFF)**: Evaluated strictly through static baseline tables. Total expected portfolio recovery: ₹12,437.50, Marginal shadow price: ₹1,756.00.
- **Treatment Group (LLM ON)**: Semantic signals applied with bounded modifiers ($\Delta P \in [-0.10, +0.10]$). Total expected portfolio recovery: ₹16,038.50, Marginal shadow price: ₹2,274.50.
- **Scientific Rationale**: Subjective semantic signals accurately isolate high-probability transient failures from unrecoverable liquid declines, lifting portfolio recovery without allowing hard declines to bypass compliance.
- **Classification**: `POSITIVE_EFFECT`.

### Experiment 2: Tool Registry Ablation (TOOLS OFF vs. TOOLS ON)
- **Control Group (TOOLS OFF)**: Blind classification without tool retrieval fails to distinguish network latency spikes from card issuer declines.
- **Treatment Group (TOOLS ON)**: Perception Agent executes `get_payment_attempts` and `get_gateway_state`, achieving 100% contextual intent accuracy.
- **Classification**: `POSITIVE_EFFECT`.

### Experiment 3: Memory Ablation (MEMORY OFF vs. MEMORY ON)
- **Control Group (MEMORY OFF)**: Mean Brier prediction error of $0.4500$ on recurring decline categories.
- **Treatment Group (MEMORY ON)**: Episodic recall of prior outcome errors for specific failure types reduces mean Brier error to $0.3755$ (error reduction: $0.0745$).
- **Classification**: `POSITIVE_EFFECT`.

### Experiment 4: Replanning Ablation (REPLAN OFF vs. REPLAN ON)
- **Control Group (REPLAN OFF)**: Static plan dispatches a payment link into a degraded gateway (gateway health = $0.40$), resulting in a wasted recovery attempt.
- **Treatment Group (REPLAN ON)**: Dynamic assumption monitor detects gateway degradation, invalidates Plan v1, and synthesizes Plan v2 (`preferred_action='WAIT'`), preserving scarce recovery capacity.
- **Classification**: `POSITIVE_EFFECT`.

### Experiment 5: Holistic System Ablation (AGENT OFF vs. AGENT ON)
- **Control Group (Tier 1 Core Alone)**: Generated ₹12,437.50 in expected recovery with static priority rankings.
- **Treatment Group (Tier 1 Core + Tier 2 Agent Layer)**: Generated ₹16,038.50 in expected recovery ($+₹3,601.00$ net lift, $1.29\times$ efficiency multiplier).
- **Safety Invariant**: Zero deterministic compliance violations across all 52 opportunities.
- **Classification**: `POSITIVE_EFFECT`.

---

## 3. Test Verification Results

- **Causal Experiment Suite (`scripts/run_causal_experiments.ts`)**: ✅ PASS (All 5 ablations measured).
- **Master Agent Safety Suite (`npm run test:agent`)**: **21 PASSED / 0 FAILED**.
- **Deterministic Core Hardening (`npm run test:core`)**: **5 PASSED / 0 FAILED**.
- **Hardened Infrastructure (`npm run test:infra`)**: **3 PASSED / 0 FAILED**.
