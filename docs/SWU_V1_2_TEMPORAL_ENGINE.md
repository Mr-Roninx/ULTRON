# ULTRON Synthetic Payment Universe v1.2 Temporal Engine

## 1. Monotonic Event Processing
The temporal engine uses `PersistentEventPriorityQueue` ordered by `(timestamp, sequence_index)`. When `world.advance_to(T)` is invoked:
1. Dynamic gateway health state machines evolve.
2. Scheduled chaos events trigger if `scheduled_timestamp <= T`.
3. Intermediate events are dequeued and dispatched to registered handlers.
4. Processed events are committed to SQLite event logs.
