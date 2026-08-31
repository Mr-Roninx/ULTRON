# ULTRON Synthetic Universe Integration & Forensic Repository Audit
**Version: ULTRON-SWU-1.0**

## 1. Executive Summary
This audit inspects the complete ULTRON architecture to establish the blueprint for `synthetic_payment_universe/`. It identifies existing components, reuse strategies, adapter layers, and boundary enforcement to prevent schema duplication and future-information leakage.

---

## 2. Forensic Audit of Existing Components

| Existing Component | File Path | Capability & Role | Reuse & Integration Strategy |
| :--- | :--- | :--- | :--- |
| **VirtualClock** | `simulator/clock.py` | Monotonic simulation clock (`now()`, `advance()`, `reset()`) | **Direct Reuse**: `synthetic_payment_universe/world/temporal_engine.py` drives events synchronized with `VirtualClock`. |
| **Observation Firewall** | `backend/benchmark/firewall.py` | Checks temporal boundaries, strips post-action variables | **Direct Integration**: The universe observation layer uses `TemporalObservationFirewall` as an invariant gate. |
| **Action Registry** | `backend/agent/action_registry.py` | Authoritative permissioned action catalog (WAIT, RETRY, etc.) | **Direct Integration**: `synthetic_payment_universe/world/action_api.py` enforces `ActionRegistry.validate_action()`. |
| **Rail Health Engine** | `backend/payment_intelligence/rail_health.py` | Dynamic gateway health tracking | **Adapter**: Dynamic gateway events from the universe feed `rail_health_engine.update_gateway_health()`. |
| **Interference Graph** | `backend/interference/` | Cross-opportunity multi-invoice interference | **Integration**: Universe entities provide linked multi-opportunity exposures on shared `customer_id`. |
| **Production Sim** | `backend/production_sim/` | Idempotent sandbox for payments, ledgers, webhooks | **Adapter / Synergy**: Universe generates offline and online streaming events consumed by production simulator. |
| **Episodic Memory** | `memory/episodic.py` | Longitudinal customer recovery episode store | **Integration**: Historical past episodes from the universe feed `memory_store` without lookahead. |

---

## 3. Separation of Realities: Three-Domain Architecture

```text
+-----------------------------------------------------------------------------+
|                                1. WORLD                                     |
|  - Full temporal event timeline (T0 .. T_end)                               |
|  - Dynamic gateway degradation / recovery regimes                           |
|  - Customer payment attempts, checkouts, subscriptions, B2B disputes        |
|  - Scheduled chaos perturbations                                            |
+-----------------------------------------------------------------------------+
               | (Only events where timestamp <= current_simulation_time)
               v
+-----------------------------------------------------------------------------+
|                          2. AGENT (OBSERVABLE VIEW)                         |
|  - Observable payment failures, ISO codes (e.g. 91, 51, 14, TO)             |
|  - Observable gateway health metrics and historical retry attempts          |
|  - Filtered customer state (no future liquidity, no hidden root cause)     |
|  - Governed by TemporalObservationFirewall & ActionRegistry                |
+-----------------------------------------------------------------------------+
               ^
               | (Action Execution at clock.now())
+-----------------------------------------------------------------------------+
|                      3. EVALUATOR (HIDDEN ORACLE)                           |
|  - True latent root causes (e.g. core banking crash vs network glitch)      |
|  - Future liquidity arrival timestamps (e.g. salary deposit at T+26h)      |
|  - Counterfactual branch evaluation (WAIT vs RETRY vs LINK vs SWITCH)       |
|  - Common random numbers / shared latent state across branches              |
+-----------------------------------------------------------------------------+
```

---

## 4. Proposed Directory Structure

```text
synthetic_payment_universe/
├── __init__.py
├── schema/
│   ├── __init__.py
│   ├── visibility.py
│   ├── taxonomy.py
│   ├── entities.py
│   ├── events.py
│   ├── counterfactual.py
│   └── scenarios.py
├── generator/
│   ├── __init__.py
│   ├── seeds.py
│   ├── customer_gen.py
│   ├── merchant_gen.py
│   ├── gateway_gen.py
│   ├── payment_gen.py
│   ├── communication_gen.py
│   └── universe_builder.py
├── world/
│   ├── __init__.py
│   ├── temporal_engine.py
│   ├── action_api.py
│   └── chaos_engine.py
├── observation/
│   ├── __init__.py
│   ├── observation_builder.py
│   └── firewall.py
├── oracle/
│   ├── __init__.py
│   └── hidden_oracle.py
├── counterfactual/
│   ├── __init__.py
│   └── counterfactual_engine.py
├── causal/
│   ├── __init__.py
│   └── causal_graph.py
├── interference/
│   ├── __init__.py
│   └── cross_opportunity.py
├── storage/
│   ├── __init__.py
│   ├── parquet_exporter.py
│   ├── jsonl_streamer.py
│   └── sqlite_engine.py
├── scenarios/
│   ├── __init__.py
│   └── golden_scenarios.py
├── validators/
│   ├── __init__.py
│   ├── schema_validator.py
│   ├── leakage_validator.py
│   ├── referential_validator.py
│   ├── statistical_validator.py
│   └── counterfactual_validator.py
└── documentation/
    ├── SYNTHETIC_UNIVERSE_SPEC.md
    ├── TAXONOMY_REFERENCE.md
    ├── CAUSAL_AND_COUNTERFACTUAL_GUIDE.md
    ├── PARTITION_MANIFEST.md
    ├── ULTRON_DATASET_INTEGRATION.md
    └── SYNTHETIC_UNIVERSE_VALIDATION.md
```

---

## 5. Implementation Sequence & Validation Gates

- **Gate A (Phase 1-2)**: Schemas, Visibility, Taxonomy & Event Types.
- **Gate B (Phase 3-8)**: Deterministic Generators (Seeds, Customers, Merchants, Gateways, Payments).
- **Gate C (Phase 15-18)**: Temporal Engine, Observation Firewall, Oracle & Counterfactual Engine.
- **Gate D (Phase 19-25)**: Causal Graph, Chaos, Interference, Golden Scenarios & Multi-Format Storage.
- **Gate E (Phase 27)**: Automated Quality & Anti-Leakage Validators.
- **Gate F (Phase 37-38)**: Comprehensive Test Suite & Full ULTRON Regression Pass (244+ tests).
