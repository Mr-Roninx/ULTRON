# Phase 15: Architecture Audit & Reality Baseline
## ULTRON v3.7 — Real LLM End-to-End Intelligence Audit

### 1. Architectural Foundation & Discovered Subsystems

ULTRON v3.7 operates as a deterministic, mathematically bounded autonomous revenue recovery system. In Phase 15, we audit the full trajectory of a real Large Language Model (Hugging Face Router / `Qwen/Qwen3.8-2.4T-A95B:novita`) operating within the agent lifecycle.

```
                    ┌─────────────────────────┐
                    │      OBSERVED WORLD     │
                    │ (VirtualClock, State)   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   INVESTIGATE & DIAG    │
                    │ (ISO-8583, Rail Health) │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       LLM REASONER      │
                    │  (HuggingFaceProvider)  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       AgentIntent       │
                    │   (Candidate Proposals) │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   FEASIBILITY FILTER    │
                    │ (Policy, Risk, Auth)    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   ECONOMIC ENGINE / NEV │
                    │ (Net Expected Value)    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ ACTION DECISION AUTH    │
                    │ (Deterministic Ranking) │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │           FSM           │
                    │ (Finite State Machine)  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     TOOL EXECUTION      │
                    │ (Simulated Dynamics)    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   OBSERVE / WAIT / WAKE │
                    │ (Mid-Flight Replan)     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    LEARN & EPISODIC     │
                    │ (Prediction Errors)     │
                    └─────────────────────────┘
```

---

### 2. Audited Architectural Components

1. **`AgentLoop` (`backend/agent/loop.py`)**:
   - Manages the longitudinal FSM transition lifecycle: `OBSERVE` $\rightarrow$ `INVESTIGATE` $\rightarrow$ `HYPOTHESIZE` $\rightarrow$ `PLAN` $\rightarrow$ `FEASIBILITY_CHECK` $\rightarrow$ `AUTHORITY_CHECK` $\rightarrow$ `RISK_CHECK` $\rightarrow$ `EXECUTE` $\rightarrow$ `WAIT` $\rightarrow$ `EVALUATE` $\rightarrow$ `LEARN` $\rightarrow$ `REPLAN`.
2. **`LLMRouter` & `HuggingFaceProvider` (`backend/llm/provider.py`)**:
   - Multi-provider router: Primary (`HuggingFaceProvider` via OpenAI-compatible Router endpoint `https://router.huggingface.co/v1`) $\rightarrow$ Fallback (`LocalQwenProvider`) $\rightarrow$ Safe Deterministic Fallback (`WAIT` intent).
3. **`AgentIntent` (`backend/agent/schemas.py`)**:
   - Pydantic schema encapsulating LLM reasoning, hypotheses, candidate actions, preferred action, and expected yield.
4. **`FeasibleActionEngine`, `PolicyEngine`, `RiskEngine` (`financial/`)**:
   - Enforces strict operational boundaries, customer segment constraints, exposure caps, and permission levels. Rejects unauthorized actions unconditionally.
5. **`ActionRanker` & `EconomicEngine` (`backend/agent/action_ranker.py`, `backend/economics/engine.py`)**:
   - Calculates Net Expected Value: $\text{NEV} = \mathbb{E}[\text{Recovery}] - C_{\text{financial}} - C_{\text{relationship}} - C_{\text{operational}} - C_{\text{risk}}$.
   - Adjusts scores based on episodic memory prediction errors.
6. **`VirtualClock` & `TemporalObservationFirewall` (`simulator/clock.py`, `backend/agent/observation.py`)**:
   - Enforces strict causality: all observations must satisfy $\text{timestamp} \le \text{clock.now()}$.
7. **`EpisodicMemoryStore` (`memory/episodic.py`)**:
   - Stores `EpisodeRecord` with prediction errors, dynamically updating action effectiveness multipliers for future encounters.

---

### 3. Core Operational Boundaries

- **Zero Financial Authority for LLM**: The LLM functions solely as an intelligence and candidate proposal engine. The deterministic engine ranks, filters, and authorizes all actions.
- **Fail-Closed Security**: Any invalid, unparseable, or adversarial LLM output automatically falls back to deterministic safe execution (`WAIT`) without crashing or executing unsafe mutations.
- **Privacy & Secret Protection**: `HF_TOKEN`, authorization headers, private prompts, and chain-of-thought tokens are strictly excluded from all logs, telemetry, and artifacts.
