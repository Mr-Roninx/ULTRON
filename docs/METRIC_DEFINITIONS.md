# ULTRON v3.2 — Metric Definitions & Mathematical Formulations

**Document Status:** Approved Definition Standard  
**Date:** 2026-08-28  

---

## 1. Primary Economic Metrics

### 1.1 Revenue at Risk & Addressable Revenue
- $\text{Revenue at Risk} = \sum_{i \in \text{Opportunities}} \text{InitialAmount}_i$
- $\text{Addressable Revenue} = \text{Revenue at Risk}$ (Strictly fixed across all baseline and treatment comparisons).

### 1.2 Gross Recovery
- $\text{Gross Recovery} = \sum_{i \in \text{Opportunities}} \mathbb{I}(\text{State}_i \in \{\text{SETTLED}, \text{PAID}, \text{COMPLETED}\}) \times \text{InitialAmount}_i$

### 1.3 Natural Recovery
- $\text{Natural Recovery} = \text{Gross Recovery}_{\text{NoAction}}$

### 1.4 Incremental Recovery
$$\text{Incremental Recovery} = \text{Gross Recovery}_{\text{Treatment}} - \text{Gross Recovery}_{\text{Control}}$$

### 1.5 Net Incremental Recovery
$$\text{Net Incremental Recovery} = \text{Incremental Recovery} - \text{Intervention Cost} - \text{Relationship Cost} - \text{Risk Cost}$$
Where:
- $\text{Intervention Cost} = \sum \text{Action Cost} + \sum \text{Human Escalation Cost}$
- $\text{Relationship Cost} = \sum_{\text{Contacted}} \text{RelationshipCostProxy}(\text{Customer})$
- $\text{Risk Cost} = \sum \text{RiskWeight} \times \text{Exposure}$

### 1.6 Primary Recovery Rate
$$\text{Recovery Rate} = \frac{\text{Gross Recovery}}{\text{Addressable Revenue}}$$
*(Note: $\frac{\text{Recovered}}{\text{Attempted}}$ is strictly prohibited as a primary recovery metric).*

---

## 2. Statistical Analysis Methodology

For any metric $X$ across $N$ independent seeds:
- **Sample Mean:** $\bar{X} = \frac{1}{N} \sum_{k=1}^N X_k$
- **Sample Median:** $\text{Median}(X_1, \dots, X_N)$
- **Sample Standard Deviation:** $s = \sqrt{\frac{1}{N-1}\sum_{k=1}^N (X_k - \bar{X})^2}$
- **95% Bootstrap Confidence Interval:** Constructed via 1,000 non-parametric bootstrap resamples with deterministic seeding ($B=1000, \alpha=0.05$).

---

## 3. Scientific Terminology Guardrails

- The difference $P(B|A) - P(B|\neg A)$ is designated as **"Temporal Association Delta"** or **"Interference Score"** (NEVER "causal lift").
- The synthetic testbed is designated as a **"Controlled Simulation Benchmark"** (NEVER "real-world proof" or "production certification").
