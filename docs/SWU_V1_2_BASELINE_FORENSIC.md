# ULTRON Synthetic Payment Universe v1.2 Forensic Baseline Audit
**Document ID: SWU_V1_2_BASELINE_FORENSIC**  
**Date: 2026-08-29**  
**Status: COMPLETED (Phase A Gate)**

---

## 1. Executive Summary
This document establishes the forensic baseline for the transition from **ULTRON Synthetic Payment Universe v1.1 (SWU-1.1)** to **ULTRON Synthetic Payment Universe v1.2 (SWU-1.2 / Codename: ULTRON-SWU-1.2)**. 

SWU-1.1 proved dataset realism, partition seed isolation, longitudinal customer histories, natural recovery rates (35.4%), and 100% test integrity across 274 tests. SWU-1.2 transforms this foundation into a **large-scale, persistent, event-driven, causally consistent financial world simulator** with double-entry ledgers, dynamic gateway/communication timelines, counterfactual world state forking, and strict three-domain separation (`WORLD`, `AGENT`, `EVALUATOR`).

---

## 2. Component Mapping & Reusability Matrix

| Existing Module | SWU-1.2 Role | Action / Strategy | Invariant Guarantees |
| :--- | :--- | :--- | :--- |
| `simulator/clock.py` (`VirtualClock`) | Global temporal synchronization | Reuse directly | Monotonic deterministic advancement |
| `backend/agent/action_registry.py` | Permissioned Action Authority | Reuse directly | LLM cannot execute unauthorized actions |
| `backend/agent/loop.py` (`AgentLoop`) | Autonomous decision lifecycle | Connect via `WorldAdapter` | LLM is an intelligence advisor, not authority |
| `backend/benchmark/firewall.py` | Temporal Observation Firewall | Extend in `world_v12/` | Strict $timestamp \le T$ lookahead block |
| `synthetic_payment_universe/schema/` | Entity & Taxonomy schemas | Extend with Ledger & World IDs | Backward compatibility preserved |
| `synthetic_payment_universe/storage/` | SQLite / JSONL / Parquet storage | Extend with indexed repository | Zero RAM exhaustion on 1M+ rows |
| `memory/episodic.py` | Episodic memory repository | Connect to persistent world ID | Only observable past outcomes stored |
| `synthetic_payment_universe/oracle/` | Evaluator-only ground truth | Encapsulate in `HiddenOracle` | Strictly inaccessible to AgentLoop / LLM |
| `synthetic_payment_universe/counterfactual/` | 5-branch causal evaluator | Extend with world state forking | Common random numbers & isolated state |

---

## 3. Key Architectural Conflicts & Mitigations
1. **In-Memory vs Persistent World State**:
   - *Conflict*: Previous generators held batches in memory before saving.
   - *Resolution*: SWU-1.2 implements `SQLiteWorldRepository` and streaming generators with lazy iteration, indexed queries, and chunked commits.
2. **Instant vs Delayed Communication Cycles**:
   - *Conflict*: Early simulators resolved link clicks instantly.
   - *Resolution*: SWU-1.2 enqueues discrete temporal events (`COMMUNICATION_SENT` $\rightarrow$ `DELIVERED` $\rightarrow$ `OPENED` $\rightarrow$ `CLICKED` $\rightarrow$ `CONVERTED`) processed in future clock ticks.
3. **Ledger Mutation Protection**:
   - *Conflict*: Ensuring no LLM decision directly touches monetary balances.
   - *Resolution*: Implemented double-entry simulated ledger service. Actions emit business intents; only authoritative world/ledger services execute balanced journal entries.

---

## 4. Phased Implementation Roadmap
- **Phase B**: World Core (`World`, `WorldConfig`, `WorldIdentity`, `SQLiteWorldRepository`, `Snapshots`).
- **Phase C**: Temporal Engine & Replay (`PersistentPriorityQueue`, `EventProcessor`, `ReplayEngine`).
- **Phase D**: Economic Entities & Simulated Double-Entry Ledger.
- **Phase E**: Behavior, Latent Liquidity, Rich Failure Taxonomy & Natural Recovery.
- **Phase F**: Gateway Dynamic Regimes, Communications & Webhooks.
- **Phase G**: Structural Causal Graph & Counterfactual World Forking.
- **Phase H**: ULTRON `WorldAdapter` & Observation Firewall Integration.
- **Phase I**: Large Scale Profiles (`tiny`, `dev`, `standard`, `large`) & CLI.
- **Phase J**: Automated Validators & 28+ Comprehensive Test Suite.
- **Phase K**: Full Regression & Master Evidence Documentation.
