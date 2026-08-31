# ULTRON Synthetic Payment Universe v1.2 Storage Architecture

## 1. Storage Layers
- **Primary**: Indexed relational SQLite database (`world.db`) with WAL mode.
- **Streaming Logs**: Event-driven streaming JSON Lines (`events.jsonl`, `payments.jsonl`, `customers.jsonl`).
- **Columnar Export**: Compressed Apache Parquet (`.parquet`) for batch machine learning and benchmark pipelines.
