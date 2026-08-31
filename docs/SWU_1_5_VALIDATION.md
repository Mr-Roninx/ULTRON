# ULTRON-SWU-1.5 Validation & Shadow Evaluation

## 1. Shadow Evaluation Architecture
- `ShadowEvaluator` evaluates all 11 competing policies (Control, Rule-Based, LLM-Off, LLM-On, Full, Conservative, Aggressive Dunning, Always Wait, Always Retry, Always Contact, Always Switch Gateway) completely out-of-band.
- Agent execution paths receive zero feedback or signals from the shadow evaluator.
- Seed determinism: Identical pre-fork SHA-256 state hashes, divergent post-fork outcomes verified.
