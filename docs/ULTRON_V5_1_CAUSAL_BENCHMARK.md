# ULTRON v5.1 — Causal Benchmark Suite & Statistical Evidence

## 1. Overview & Protocol

The ULTRON Causal Benchmark Suite (`scripts/run_causal_experiments.ts`) measures the empirical causal influence of each individual Tier 2 AI Agent subcomponent against its respective control condition using paired random cohorts ($N = 5$ paired seeds per experiment).

---

## 2. The 8 Causal Experiments Matrix

| Exp ID | Component | Control | Treatment | Effect Metric | Classification |
|---|---|---|---|---|---|
| **EXP-1** | **LLM Semantic Signals** | LLM OFF | LLM ON | Expected IVEN Recovery (paise) | **`POSITIVE_EFFECT`** |
| **EXP-2** | **Tool Registry** | Blind Guess | 3 Live Read Tools | Intent Diagnosis Accuracy | **`POSITIVE_EFFECT`** |
| **EXP-3** | **Episodic Memory** | Tabula Rasa | Memory Recall | Brier Prediction Error | **`POSITIVE_EFFECT`** |
| **EXP-4** | **Replan Engine** | Static Plan | Dynamic Replanning | Wasted Link Dispatch Reductions | **`POSITIVE_EFFECT`** |
| **EXP-5** | **Portfolio Agent** | FIFO Sequential | Multi-Signal Priority Sweep | Captured IVEN per Run | **`POSITIVE_EFFECT`** |
| **EXP-6** | **Uncertainty Model** | Blind Dispatch | 3-Dim Uncertainty Routing | Avoided Operational Losses | **`POSITIVE_EFFECT`** |
| **EXP-7** | **Concurrency Pool** | Sequential ($C=1$) | Worker Pool ($C=2$) | Batch Processing Latency | **`POSITIVE_EFFECT`** |
| **EXP-8** | **Holistic Architecture** | Rule Core Alone | Complete Tier 1 + Tier 2 System | Net Portfolio Value | **`POSITIVE_EFFECT`** |

---

## 3. Statistical Analysis Standards

For each experiment, the framework computes:
- $\mu_{\text{control}}$ and $\mu_{\text{treatment}}$
- Mean Difference $\Delta = \mu_{\text{treatment}} - \mu_{\text{control}}$
- Median Difference
- Standard Deviation $\sigma$ and Standard Error $SE = \sigma / \sqrt{N}$
- Two-sided 95% Confidence Interval $[\Delta - 1.96 \cdot SE, \Delta + 1.96 \cdot SE]$
- Cohen's $d$ Effect Size

---

## 4. Benchmark Artifact Locations

- Primary Evidence: [`results/agent/causal_influence.json`](file:///d:/Work%20Space/Project/Ultron/results/agent/causal_influence.json)
- v5.1 Benchmark Package: [`results/agent/v51/causal_benchmark.json`](file:///d:/Work%20Space/Project/Ultron/results/agent/v51/causal_benchmark.json)
