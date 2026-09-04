# ULTRON v5.1 — Mission Concurrency Coordinator Specification

## 1. Overview & Architecture

The **Mission Concurrency Coordinator** (`src/agents/concurrency.ts`) provides bounded, parallel execution of autonomous payment recovery missions across multi-opportunity batches while strictly preserving Action Authority, idempotency, and isolation guarantees.

```
                                OPPORTUNITY BATCH
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │        MISSION CONCURRENCY COORDINATOR       │
                 │                                              │
                 │  - Max Concurrency Ceiling (Default: 3)      │
                 │  - Per-Opportunity Lock Deduplication        │
                 │  - Instant Global Kill Switch Propagation    │
                 │  - Batch Metrics Aggregator                  │
                 └──────────────────────┬───────────────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
      [Mission Worker 1]         [Mission Worker 2]         [Mission Worker 3]
       Isolated run_id            Isolated run_id            Isolated run_id
       State Machine 1            State Machine 2            State Machine 3
       Authority Gate 1           Authority Gate 2           Authority Gate 3
```

---

## 2. Invariants & Safety Guarantees

1. **Max Concurrency Ceiling**: Active concurrent missions never exceed `max_concurrent_missions` (default: 3) to prevent API rate exhaustion and system overload.
2. **Per-Opportunity Locking**: An opportunity undergoing active processing acquires an in-memory lock. Duplicate concurrent requests for the same `opportunity_id` are safely rejected or aborted (`skipped_duplicate_lock`).
3. **Instant Kill Switch Propagation**: If the global kill switch is engaged, all pending and in-flight missions in the concurrency queue are immediately halted without executing payment links.
4. **Isolated Telemetry & Budgets**: Each mission runs with a dedicated `run_id`, separate step budgets, and independent SQLite trace records.

---

## 3. Configuration Parameters

```typescript
export interface ConcurrencyPoolConfig {
  max_concurrent_missions: number; // Default: 3
  mission_timeout_ms: number;      // Default: 45000ms
  rate_limit_per_minute: number;   // Default: 60
}
```

---

## 4. Telemetry & Batch Summaries

Each batch produces a comprehensive `BatchMissionSummary`:
- Total submitted, completed, aborted, and failed missions
- Total and average latency (ms)
- Total tokens and steps executed
- Peak concurrency level achieved
