# ULTRON v3.8 — Phase 16 Operating & Audit Protocol

## 1. Mission & Authority Boundaries
ULTRON is an autonomous B2B revenue and payment recovery agent. The foundational architectural invariant is:
> **The LLM is an intelligence and candidate proposal component, NOT a financial authority.**

### Authoritative Pipeline
```text
WORLD -> OBSERVE -> INVESTIGATE -> HYPOTHESIZE -> REAL LLM REASONING -> CANDIDATE ACTIONS
  -> FEASIBILITY -> POLICY -> RISK -> ECONOMIC / NEV RANKING -> ACTION DECISION AUTHORITY
  -> FSM -> EXECUTE -> WAIT -> OBSERVE -> REPLAN -> LEARN -> EPISODIC MEMORY
```

## 2. Strict Invariants
1. **Zero Financial Mutation**: The LLM cannot mutate balances, modify ledger rows, or execute raw SQL.
2. **Action Registry Governed**: All executable actions must originate from `backend/agent/action_registry.py`.
3. **Temporal Firewall Enforced**: No agent component may observe data with `timestamp > clock.now()`.
4. **Secret Scrubbing**: Telemetry and logs recursively scrub API keys, bearer tokens, and private prompts.
5. **Bounded Latency**: LLM requests enforce soft (5s) and hard (10s) timeouts with failover: `HF -> Local -> Safe Fallback`.
