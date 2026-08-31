# ULTRON v4.0 — Phase 18: Economic Calibration & Information Value Results

## 1. Information Value Metrics ($\Delta\text{NEV}$)
Evaluated on $N=100$ paired seeds (401–500):

| Metric | Definition | Measured Value | Verdict |
| :--- | :--- | :--- | :--- |
| **$\Delta\text{NEV}_{\text{candidate}}$** | $\text{Best}(\text{Union}) - \text{Best}(\text{Deterministic})$ | **INR 0.00** | `NO_EFFECT` |
| **$\Delta\text{NEV}_{\text{signal}}$** | $\text{Best}(\text{Signal Calibrated}) - \text{Best}(\text{Deterministic})$ | **+INR 825.57** | `MEASURABLE_LIFT` |
| **$\Delta\text{NEV}_{\text{combined}}$** | $\text{Best}(\text{Candidates + Signals}) - \text{Best}(\text{Deterministic})$ | **+INR 825.57** | `MEASURABLE_LIFT` |

---

## 2. Regret Reduction Analysis
- **Baseline Mean Regret**: INR 10,870.00
- **Calibrated Mean Regret**: INR 689.44
- **Absolute Regret Reduction**: **INR 10,180.56**
- **Percentage Reduction**: **93.7%** (`SUPPORTED`)
