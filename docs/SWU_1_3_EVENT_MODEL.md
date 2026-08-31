# ULTRON-SWU-1.3 Event Model

## 1. Event Stream Architecture
All events inherit from `EconomicEvent` with:
- `event_id`: Unique identifier
- `event_type`: Categorical event code
- `entity_id`: Target entity
- `timestamp`: Virtual clock time
- `visibility`: `OBSERVABLE`, `HIDDEN`, or `EVALUATOR_ONLY`
- `causal_parent_id`: Lineage parent link
- `sequence_index`: Tie-breaker for identical timestamps
