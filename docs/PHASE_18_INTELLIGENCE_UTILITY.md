# ULTRON v4.0 — Phase 18: Intelligence Utility & Signal Calibration Audit

## 1. Overview
This report documents the counterfactual intelligence evaluation across $N=100$ independent evaluation seeds (`401–500`).

---

## 2. 4-Branch Counterfactual Design
- **Branch A (LLM OFF)**: Deterministic heuristic baseline.
- **Branch B (LLM ON)**: Candidate set proposals only.
- **Branch C (LLM ON + Signals)**: Raw semantic signal inputs.
- **Branch D (LLM ON + Signals + Calibration)**: Calibrated, bounded signals feeding NEV parameterization.

---

## 3. Empirical Results
- **Candidate Novelty Rate**: **53.8%** (`PROVEN`)
- **Candidate Pool Modification**: **100.0%** (`PROVEN`)
- **Semantic Diagnosis Differentiation**: **100.0%** (`PROVEN`)
- **Mean $\Delta\text{NEV}$ (Candidate Only)**: **INR 0.00** (`NO_EFFECT`)
- **Mean $\Delta\text{NEV}$ (Signal Calibrated)**: **+INR 825.57** (`MEASURABLE_LIFT`)
- **LLM Candidate Regret Reduction**: **93.7%** (From INR 10,870.00 down to INR 689.44) (`REGRET_REDUCED`)
