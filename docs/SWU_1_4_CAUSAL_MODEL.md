# ULTRON-SWU-1.4 Causal Model

## 1. Structural Causal Graph
```text
CustomerCohort -----------> PurchaseIntent -----------> PaymentAttempt
                                                             │
GatewayCongestion --------> AuthorizationRate ───────────────┤
                                                             ▼
ULTRONIntervention -------> CustomerResponse ---------> RecoveredRevenue
      │                           │                          │
      └───────> ContactFatigue ───┴─────────────> CustomerRelationship
                      │                                      │
                      ▼                                      ▼
               CustomerChurn                         FuturePurchase (LTV)
```
- Lineage queries supported: `get_upstream_causes()` and `get_downstream_effects()`.
