# ULTRON Agent Integration with Synthetic Payment Universe

```text
Synthetic Payment Universe
        │
        ▼ (Filtered by UniverseObservationFirewall)
Observation API (`observe_payment`, `observe_customer`, `observe_gateway`)
        │
        ▼
ULTRON AgentLoop (`OBSERVE` -> `INVESTIGATE` -> `HYPOTHESIZE`)
        │
        ▼
LLM Semantic Signals (`failure_is_transient`, `customer_liquidity_likelihood`)
        │
        ▼
Calibration Engine (`[0.0, 1.0]`, Confidence Attenuation, ±25% Max Impact)
        │
        ▼
Deterministic NEV Engine (Net Expected Value Argmax Selection)
        │
        ▼
Action Decision Authority (100% Deterministic Financial Invariant)
        │
        ▼
Universe Action API (`execute_action` -> `ActionRegistry` -> `TemporalEngine`)
        │
        ▼
Temporal Event Simulation & Ground Truth Evaluation
```
