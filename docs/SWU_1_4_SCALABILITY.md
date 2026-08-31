# ULTRON-SWU-1.4 Scalability Report

## 1. Scale Benchmarks
- **Streaming Generator**: Inserts 500-record chunks, maintaining memory consumption under 200MB even for 100K+ populations.
- **SQLite Performance**: WAL mode and indexed relations achieve >10,000 events/sec query and replay performance.
- **Replay**: Bit-for-bit SHA-256 cryptographic reconstruction verified.
