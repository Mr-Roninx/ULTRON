# ULTRON Synthetic Payment Universe Specification
**Version: ULTRON-SWU-1.0**

## 1. Architectural Principles
The Synthetic Payment Universe implements a strictly partitioned three-domain architecture:
1. **WORLD**: Complete evolving financial reality with dynamic gateway health, customer lifecycles, and scheduled chaos perturbations.
2. **AGENT**: Observable view accessible to ULTRON strictly satisfying $timestamp \le current\_time$, filtered via `TemporalObservationFirewall`.
3. **EVALUATOR**: Hidden oracle ground truth containing latent liquidity windows, true root causes, and counterfactual branch outcomes.

---

## 2. Supported Formats
- **JSONL**: Streaming event-driven log format for large-scale workloads.
- **SQLite (.db)**: Relational tables (`customers`, `merchants`, `payments`, `ground_truth`) with foreign-key integrity.
- **Parquet (.parquet)**: High-performance columnar format for machine learning and bulk statistical evaluation.

---

## 3. Data Partitions
- **DEV**: Seeds `1–1000`
- **VALIDATION**: Seeds `1001–2000`
- **EVALUATION**: Seeds `2001–5000`
- **HARD_CASES**: Seeds `5001–6000`
- **CHAOS**: Seeds `6001–7000`
- **ADVERSARIAL**: Seeds `7001–8000`
