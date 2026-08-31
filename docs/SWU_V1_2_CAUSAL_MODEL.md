# ULTRON Synthetic Payment Universe v1.2 Causal Model

## 1. Structural Causal Graph (DAG)
```text
CustomerBehavior -------------> PaymentIntent -------------> PaymentOutcome
                                                                    ^
GatewayHealth ----------------> AuthorizationRate ------------------+
                                                                    |
ULTRONAction -----------------> CustomerResponse -------------------+
      │                               ^
      └──────> CommunicationFatigue ──┘
```
Lineage queries supported: `get_upstream_causes()` and `get_downstream_effects()`.
