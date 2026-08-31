# ULTRON v5.0 Real Payment Mission Architecture

## 1. Mission Lifecycle State Machine
```
    NEW
      ↓
    OBSERVING
      ↓
    DIAGNOSING
      ↓
    PLANNING
      ↓
    AUTHORIZED
      ↓
    EXECUTING
      ↓
    AWAITING_PROVIDER
      ↓
    RECONCILING
      ↓
    RECOVERED / FAILED / ESCALATED / STOPPED
```

## 2. Persistence & Asynchronous Execution
Missions persist across process restarts, webhooks, retries, `WAIT`, `WAKE`, and `REPLAN` cycles without busy polling loops.
