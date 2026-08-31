# ULTRON-SWU-1.3 Causal Model

## 1. Structural Causal Graph
```text
CustomerBehavior -------------> PaymentIntent -------------> AuthorizationOutcome
                                                                    ^
GatewayHealth ----------------> AuthorizationRate ------------------+
                                                                    |
ULTRONIntervention -----------> CustomerResponse -------------------+
      │                               │
      ├───────> Fatigue ──────────────┤
      │                               ▼
      └───────────────────────> RecoveryOutcome
                                      │
                   ┌──────────────────┴──────────────────┐
                   ▼                                     ▼
        CustomerRelationship                      MerchantRevenue
                   │                                     │
                   ▼                                     ▼
        FuturePaymentProbability                  SettledBankLedger
```
Lineage queries supported: `get_upstream_causes()` and `get_downstream_effects()`.
