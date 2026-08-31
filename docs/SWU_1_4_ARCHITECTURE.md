# ULTRON Synthetic Payment Universe v1.4 Architecture

## 1. High-Level Architecture
```text
+-------------------------------------------------------------------------------+
|                       EMERGENT CIVILIZATION CORE                              |
|  - EmergentEconomicWorld (Continuous multi-horizon simulation)                |
|  - SQLiteEmergentRepository (WAL mode, indexed relational schema)             |
|  - PopulationDoubleEntryLedger (Zero-imbalance financial ledger)              |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
|                         POPULATION & DEMAND LAYER                             |
|  - Customer Cohorts (Salary-cycle, volatile SMB, highly loyal, enterprise)   |
|  - Merchant Lifecycles (New, growing, stable, stressed, declining)           |
|  - Emergent Demand: Cohort Propensity x Trust x Macro Surge                   |
|  - Dynamic Gateways (A, B, C, D) reacting to traffic load (Loop B)            |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼
+-------------------------------------------------------------------------------+
|                   CAUSAL DYNAMICS & COUNTERFACTUAL FORKING                    |
|  - Closed Feedback Loops A, B, C, D, E, F                                     |
|  - 5-Branch CivilizationForkEngine (CRN-aligned)                              |
|  - End-to-End ProvenanceTracker & CausalAttributionEngine                     |
+-------------------------------------------------------------------------------+
                                      │
                                      ▼ (RecursiveObservationFirewall)
+-------------------------------------------------------------------------------+
|                            ULTRON AUTONOMOUS AGENT                            |
|  - AgentLoop -> LLMRouter -> Calibration -> NEV -> ActionRegistry             |
+-------------------------------------------------------------------------------+
```
