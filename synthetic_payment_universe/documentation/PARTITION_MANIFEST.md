# ULTRON Synthetic Universe Partition Manifest

| Partition | Seed Range | Customers | Payments | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **DEV** | `1–1000` | 100 | 1,000 | Agent development, heuristics tuning |
| **VALIDATION** | `1001–2000` | 100 | 1,000 | Hyperparameter calibration, confidence thresholds |
| **EVALUATION** | `2001–5000` | 200 | 2,000 | Primary benchmark, causal lift measurement |
| **HARD_CASES** | `5001–6000` | 50 | 500 | Near-tied 1–5% NEV boundary testing |
| **CHAOS** | `6001–7000` | 50 | 500 | Mid-flight gateway degradation & replan evaluation |
| **ADVERSARIAL** | `7001–8000` | 50 | 500 | Prompt injection, invalid ISO codes, lookahead attacks |
