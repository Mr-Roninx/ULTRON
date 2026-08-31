# ULTRON-SWU-1.3 World Persistence

## 1. Storage & State Management
- **Primary Storage**: SQLite with Write-Ahead Logging (WAL) and strict foreign keys.
- **Snapshots**: Atomic hot backups via `CivilizationSnapshotEngine.snapshot()`.
- **Replay**: Full deterministic event stream replay via `CivilizationReplayEngine.compute_state_hash()`.
