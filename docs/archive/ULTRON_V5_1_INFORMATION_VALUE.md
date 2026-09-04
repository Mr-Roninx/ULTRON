# ULTRON v5.1 — Information Value Estimator Specification

## 1. Overview & Objective

The **Information Value Estimator** (`src/agents/information_value.ts`) enables ULTRON to evaluate whether collecting more information (via specialist perception, customer lookup, or gateway health verification) is economically justified before committing limited recovery capacity.

---

## 2. Expected Value of Information (EVOI) Formulation

$$\text{EVOI} = \text{IVEN} \times (1 - C_{\text{composite}}) \times \gamma_{\text{max\_fraction}}$$

Where:
- $\text{IVEN}$ = Expected Incremental Value in paise
- $C_{\text{composite}}$ = Composite confidence score $\in [0, 1]$
- $\gamma_{\text{max\_fraction}} = 0.20$ (Hard bounding cap: EVOI cannot exceed 20% of opportunity IVEN)

---

## 3. Decision Matrix (Deterministic & Non-LLM)

| Condition | Recommended Action | Rationale |
|:---|:---|:---|
| Gateway Health $< 0.75$ AND $\text{EVOI} > \text{Cost}_{\text{investigation}}$ | **`INVESTIGATE`** | Gateway is degraded; investigation yields higher value than the fixed operational cost of 200 paise. |
| $C_{\text{composite}} \ge 0.70$ AND Gateway Health $\ge 0.75$ AND $\text{IVEN} > 5000\text{ paise}$ | **`ACT`** | High confidence, stable gateway, and strong economic return justify immediate recovery link dispatch. |
| $\text{IVEN} \le 5000\text{ paise}$ OR Gateway Health $< 0.75$ | **`WAIT`** | Marginal economic return or unviable gateway conditions require deferral. |
| $\text{EVOI} > \text{Cost}_{\text{investigation}}$ | **`INVESTIGATE`** | Intermediate confidence level where investigation cost is smaller than expected information gain. |
| Otherwise | **`ACT`** (if $\text{IVEN} > 0$) / **`WAIT`** | Deterministic fallback based on raw sign of IVEN. |

---

## 4. Safety Bounds

1. **Fixed Investigation Cost**: Fixed at $200\text{ paise}$ ($\text{₹}2.00$).
2. **Cap on EVOI**: Strictly bounded by $\text{IVEN} \times 0.20$ to prevent infinite loops and runaway informational valuations.
3. **No Financial Operations**: The estimator is pure advisory logic.
