# ULTRON Synthetic Payment Universe v1.3 Architecture

## 1. Subsystem Composition
```text
+-----------------------------------------------------------------------------+
|                      PERSISTENT CIVILIZATION CORE                           |
|  - PersistentEconomicWorld (Multi-day continuous simulation)                |
|  - SQLiteCivilizationRepository (WAL mode, indexed relational schema)       |
|  - CivilizationDoubleEntryLedger (Balanced debit/credit ledger)             |
+-----------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------+
|                        ORGANIC ECONOMIC ENGINES                             |
|  - CustomerEconomyEngine: Lifecycle states & fatigue dynamics               |
|  - MerchantEconomyEngine: Receivables, fees, and revenue tracking           |
|  - GatewayEconomyEngine: Congestion feedback & dynamic health               |
|  - SubscriptionEconomyEngine: Monthly, quarterly, annual renewals           |
|  - InvoiceEconomyEngine: Net-30/60 terms, grace periods, PO aging           |
|  - SettlementEconomyEngine: Batch clearing windows & fees                   |
+-----------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------+
|                     CAUSAL & LONG-HORIZON FORKING                           |
|  - CivilizationCausalGraph: Macro/micro SCM DAG                             |
|  - CivilizationCounterfactualForkEngine: 5-branch long-horizon NEV          |
+-----------------------------------------------------------------------------+
                                     │
                                     ▼ (CivilizationObservationFirewall)
+-----------------------------------------------------------------------------+
|                        ULTRON AUTONOMOUS AGENT                              |
|  - OpportunityScheduler -> AgentCapacityGuard -> LLMRouter -> NEV -> Action |
+-----------------------------------------------------------------------------+
```
