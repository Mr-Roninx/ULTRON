# ULTRON v5.1 — Causal Benchmark Scientific Integrity & Statistical Methodology

---

## 1. Executive Summary & Why This Audit Was Necessary

During forensic verification of the ULTRON v5.1 acceptance package, numerical contradictions were identified between machine-readable JSON metrics and narrative text descriptions. Specifically:
- **Narrative Overstatement**: Hard-coded descriptions referenced historical exploratory figures ($+28.9\%$, $+29.0\%$, and Cohen's $d = 1.12$) that diverged from runtime calculations ($+14.60\%$, paired Cohen's $d_z = 4.959$).
- **Manual Summary Vulnerability**: Certain experiment summaries were statically typed rather than dynamically computed from per-seed observations.
- **Statistical Power Ambiguity**: Small-sample exploratory cohorts ($N=5$) were previously labeled with generalized effect statements without formal confidence interval bounds.

To resolve these discrepancies at their mathematical root, ULTRON v5.1 implements a single authoritative statistical engine (`src/truth/causal_analysis_engine.ts`) governed by the **Zero-Manual-Summary Invariant**: all statistical measures, confidence intervals, effect sizes, and scientific rationales are derived dynamically and deterministically from stored per-seed observations.

---

## 2. Benchmark Methodology: Paired Counterfactual Ablation Design

Each experiment evaluates an isolated subsystem against its exact counterfactual twin:

$$\text{Treatment} = f(\text{Component}_{\text{ON}}, \text{Seed}_i), \quad \text{Control} = f(\text{Component}_{\text{OFF}}, \text{Seed}_i)$$

For each seed $i \in \{1, 2, 3, 4, 5\}$, the paired difference is computed as:
$$d_i = \text{Treatment}_i - \text{Control}_i$$

### Strict Control Principles:
1. **Identical Baseline State**: Identical initial failure cohort, identical customer profiles, and identical macroeconomic assumptions.
2. **Single-Variable Isolation**: Exactly one subsystem (e.g. LLM semantic signals, tool access, episodic recall, dynamic replanning) is toggled per experiment.
3. **Reproducibility**: Experiments are parameterized with deterministic seed sets ($[1, 2, 3, 4, 5]$) and cryptographically fingerprinted using SHA-256 (`configuration_hash: b8b5af0b69e...`).

---

## 3. Mathematical & Statistical Definitions

### A. Paired Mean Difference ($\bar{d}$)
$$\bar{d} = \frac{1}{N} \sum_{i=1}^{N} d_i$$

### B. Sample Standard Deviation of Differences ($s_d$)
$$s_d = \sqrt{\frac{1}{N - 1} \sum_{i=1}^{N} (d_i - \bar{d})^2}$$

### C. Standard Error ($\text{SE}$)
$$\text{SE} = \frac{s_d}{\sqrt{N}}$$

### D. Small-Sample 95% Confidence Interval (Student's $t$)
With $N = 5$ ($df = 4$), the two-tailed critical value is $t_{0.025, 4} = 2.776$:
$$\text{CI}_{95\%} = \left[ \bar{d} - 2.776 \cdot \text{SE}, \; \bar{d} + 2.776 \cdot \text{SE} \right]$$

### E. Paired Standardized Mean Difference (Cohen's $d_z$)
$$d_z = \frac{\bar{d}}{s_d}$$
*(Where $s_d = 0$ for constant deterministic separations, the pooled two-group standard deviation $d_{\text{av}}$ or deterministic indicator is recorded).*

### F. Percentage Lift
$$\text{Lift} = \frac{\bar{x}_{\text{Treatment}} - \bar{x}_{\text{Control}}}{|\bar{x}_{\text{Control}}|} \times 100$$

---

## 4. Authoritative Causal Benchmark Results Table ($N=5$ Paired Seeds)

| Experiment ID | Component Tested | Metric & Unit | Control Mean | Treatment Mean | Paired Mean Diff ($\bar{d}$) | 95% Confidence Interval | Effect Size (Cohen's $d_z$) | Classification |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **`EXP_1_LLM_ABLATION`** | Semantic Signals | IVEN (paise) | $540,450.00$ | $619,372.60$ | $+78,922.60$ ($+14.60\%$) | $[59,165.28, 98,679.92]$ | $d_z = 4.959$ (Large) | **`POSITIVE_EFFECT`** |
| **`EXP_2_TOOLS_ABLATION`** | Tool Ingestion | Intent Score (0–1) | $0.4000$ | $0.9500$ | $+0.5500$ ($+137.50\%$) | $[0.5500, 0.5500]$ (Degenerate) | Undefined (Zero Variance) | **`POSITIVE_EFFECT`** |
| **`EXP_3_MEMORY_ABLATION`** | Episodic Memory | Brier Error ($\downarrow$) | $0.4500$ | $0.3605$ | $-0.0895$ ($-19.89\%$) | $[-0.0993, -0.0797]$ | $d_z = -11.321$ (Large) | **`POSITIVE_EFFECT`** |
| **`EXP_4_REPLAN_ABLATION`** | Replanning Engine | Wasted Dispatches ($\downarrow$) | $1.0000$ | $0.0000$ | $-1.0000$ ($-100.00\%$) | $[-1.0000, -1.0000]$ (Degenerate) | Undefined (Zero Variance) | **`POSITIVE_EFFECT`** |
| **`EXP_5_PORTFOLIO_SWEEP`** | Portfolio Agent | Allocated IVEN (paise) | $88,750.00$ | $888,550.00$ | $+799,800.00$ ($+901.18\%$) | $[780,541.78, 819,058.22]$ | $d_z = 51.558$ (Large) | **`POSITIVE_EFFECT`** |
| **`EXP_6_UNCERTAINTY_GATING`** | Uncertainty Model | Avoided Loss (paise) | $0.00$ | $400.00$ | $+400.00$ paise | $[400.00, 400.00]$ (Degenerate) | Undefined (Zero Variance) | **`POSITIVE_EFFECT`** |
| **`EXP_7_CONCURRENCY_SCALING`**| Concurrency Pool | Latency ms ($\downarrow$) | $3,200.00$ | $1,650.00$ | $-1,550.00$ ($-48.44\%$) | $[-1,550.00, -1,550.00]$ (Degenerate) | Undefined (Zero Variance) | **`POSITIVE_EFFECT`** |
| **`EXP_8_HOLISTIC_INTELLIGENCE`**| Complete v5.1 System| Expected Value (paise)| $540,450.00$ | $619,372.60$ | $+78,922.60$ ($+14.60\%$) | $[59,165.28, 98,679.92]$ | $d_z = 4.959$ (Large) | **`POSITIVE_EFFECT`** |

*All summary figures verified against raw per-seed observations with 0 discrepancies. For zero-variance differences, Cohen's d_z is undefined.*

---

## 5. Statistical Significance & Power Status

- **Statistical Significance**: **`NOT_CLAIMED`** ($p\text{-value} = \text{null}$).
- **Power Classification**: **`PRELIMINARY_UNDERPOWERED_N5`**.
- **Scientific Interpretation**: An exploratory sample of $N=5$ paired seeds provides directionally consistent evidence under synthetic benchmark conditions. Cohen's $d_z$ reflects observed effect magnitude within the test sample and must not be conflated with asymptotic statistical significance.

---

## 6. Audit of Corrected Discrepancies

| Item / Claim | Historical Text (Superseded) | Corrected Value (Canonical) | Reason for Correction |
|:---|:---|:---|:---|
| **EXP_1 / EXP_8 Lift** | $+28.9\%$ / $+29.0\%$ IVEN Lift | **$+14.60\%$** ($\bar{d} = 78,922.60\text{ paise}$) | Calculated directly from raw per-seed observations ($540,450 \to 619,372.6$ paise). |
| **EXP_1 Effect Size** | $d = 1.12$ / $0.404$ | **$d_z = 4.959$** | Enforced standard paired Cohen's $d_z = \bar{d} / s_d$. |
| **Zero Variance Effect Sizes** | Arbitrary sentinels ($9.999$) | **`null` / Undefined (Zero Variance)** | Enforced strict statistical validity when sample delta variance is 0. |
| **EXP_5 Captured IVEN** | $+48,600\text{ paise}$ | **$+799,800.00\text{ paise}$** | Computed from multi-opportunity knapsack auction sweep ($K=3$). |
| **Zero Manual Summaries** | Static Markdown strings | **100% Dynamically Generated** | Enforced programmatic derivation via `CausalAnalysisEngine`. |
| **Significance Statements** | "Statistically validated" | **"Preliminary directional evidence"** | Explicitly removed premature inferential claims for $N=5$. |

---

## 7. Claim Boundaries & External Validity

1. **Synthetic Cohort Boundary**: These benchmarks evaluate algorithmic performance across controlled synthetic failure distributions. They do **not** claim real-world production revenue uplift.
2. **Provider Evidence Independence**: Real payment settlement evidence on Razorpay Test Mode (`plink_TWcnQZVwogNPop` / `pay_TWd8rHL0ewMl51`, ₹4,500.00) is evaluated independently via REST API reconciliation and does not rely on synthetic causal models.
3. **Deterministic Authority Boundary**: AI agent signals remain advisory; the Tier 1 Deterministic Financial Core holds exclusive authority over payment link creation and ledger mutations.
