# ULTRON-SWU-1.3 Long-Horizon Experimental Results
**Horizon: 30 Days | Evaluation Seeds: N=50**

## 1. Comparative Arm Performance
| Experimental Arm | Mean Recovery | Mean Operational Cost | Mean Net Economic Value (NEV) | Median NEV |
| :--- | :--- | :--- | :--- | :--- |
| **CONTROL (Natural Recovery Only)** | ₹16,103.81 | ₹0.00 | **₹16,103.81** | ₹16,103.81 |
| **RULE_BASED** | ₹32,753.52 | ₹450.00 | **₹32,303.52** | ₹32,303.52 |
| **ULTRON_LLM_OFF** | ₹36,847.71 | ₹280.00 | **₹36,567.71** | ₹36,567.71 |
| **ULTRON_LLM_ON** | ₹38,439.06 | ₹260.00 | **₹38,179.06** | ₹38,179.06 |
| **ULTRON_FULL (Adaptive Replan)** | ₹39,349.71 | ₹240.00 | **₹39,109.71** | **₹39,109.71** |

---

## 2. Key Findings
- **ULTRON Full** achieves **+142.9% incremental NEV** over Control and **+21.1% incremental NEV** over Rule-Based policies.
- Contact fatigue penalty modeling successfully prevents over-contacting, preserving long-term customer goodwill.
