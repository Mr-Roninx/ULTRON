# ULTRON Synthetic Payment Universe v1.2 Architecture

## 1. System Components
```text
+-----------------------------------------------------------------------------+
|                            PERSISTENT WORLD CORE                            |
|  - WorldIdentity & Config (WorldProfile: tiny, dev, standard, large)        |
|  - SQLiteWorldRepository (WAL mode, indexed relational tables)              |
|  - SimulatedDoubleEntryLedger (Debit/Credit balance invariant)              |
+-----------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------+
|                          TEMPORAL EVENT ENGINE                              |
|  - PersistentEventPriorityQueue (Chronological order)                       |
|  - TemporalEventProcessor (Monotonic step-by-step event dispatch)           |
|  - ReplayEngine (Historical trajectory replay)                              |
+-----------------------------------------------------------------------------+
                                     │
                                     ▼
+-----------------------------------------------------------------------------+
|                      CAUSAL & COUNTERFACTUAL FORKING                        |
|  - StructuralCausalGraph (SCM cause-and-effect DAG)                         |
|  - WorldCounterfactualForkEngine (5-branch common random numbers)           |
+-----------------------------------------------------------------------------+
                                     │
                                     ▼ (WorldObservationFirewall)
+-----------------------------------------------------------------------------+
|                               ULTRON AGENT                                  |
|  - WorldAdapter -> AgentLoop -> LLMRouter -> NEV -> ActionRegistry          |
+-----------------------------------------------------------------------------+
```
