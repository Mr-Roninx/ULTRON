# ULTRON v5.1 — Structured Uncertainty Model Specification

## 1. Overview & Objective

The **Uncertainty Model** (`src/agents/uncertainty.ts`) replaces naive LLM self-confidence with a 3-dimensional deterministic uncertainty quantification system based entirely on observable historical and runtime evidence.

---

## 2. The Three Independent Confidence Dimensions

```
                           UNCERTAINTY MODEL
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
 ┌───────────────┐         ┌───────────────┐         ┌───────────────┐
 │ MODEL_CONF    │         │  DATA_CONF    │         │ ECONOMIC_CONF │
 │ (Calibration  │         │ (Completeness │         │ (IVEN / Cost  │
 │  History)     │         │  of Context)  │         │  Ratio)       │
 └───────┬───────┘         └───────┬───────┘         └───────┬───────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   ▼
                       COMPOSITE CONFIDENCE SCORE
                                   │
               ┌───────────────────┼───────────────────┐
               ▼                   ▼                   ▼
          ≥ 0.70              0.40 - 0.70            < 0.40
         PROCEED              INVESTIGATE         HUMAN_REVIEW
                                                    / ABSTAIN
```

### 1. Model Confidence ($C_{\text{model}}$)
Quantifies reliability of prior historical outcomes for the failure code:
- $N \ge 30$: $1.0 - \min(\text{HistoricalError}, 1.0)$
- $10 \le N < 30$: $0.60 - (\text{HistoricalError} \times 0.3)$
- $N < 10$: $0.35$ (Penalized for low sample size)

### 2. Data Confidence ($C_{\text{data}}$)
Measures the completeness of active opportunity signals:
- Base: $0.20$
- $+$ Economic Score present: $+0.25$
- $+$ Specialist Perception present: $+0.25$
- $+$ Customer History present: $+0.15$
- $+$ Gateway State verified: $+0.15$

### 3. Economic Confidence ($C_{\text{econ}}$)
Evaluates resilience of the economic thesis against cost shocks:
- $\text{IVEN} > 5 \times \text{Costs}$: $0.95$
- $\text{IVEN} > 2 \times \text{Costs}$: $0.75$
- $\text{IVEN} > 1 \times \text{Costs}$: $0.55$
- $\text{IVEN} > 0$: $0.35$
- $\text{IVEN} \le 0$: $0.10$

---

## 3. Composite Calculation & Threshold Routing

$$C_{\text{composite}} = 0.35 \cdot C_{\text{model}} + 0.35 \cdot C_{\text{data}} + 0.30 \cdot C_{\text{econ}}$$

- **`PROCEED`** ($C_{\text{composite}} \ge 0.70$): Evidence is solid, proceed through deterministic allocation.
- **`INVESTIGATE`** ($0.40 \le C_{\text{composite}} < 0.70$): Evidence is promising but incomplete; call read-only tools to gather missing signals.
- **`HUMAN_REVIEW` / `ABSTAIN`** ($C_{\text{composite}} < 0.40$): Low confidence forbids autonomous action.
