import os
import sqlite3
import json
from typing import Dict, Any, List, Optional, Generator

class SQLiteAdversarialRepository:
    """
    SQLite persistence layer for SWU-1.5 Adversarial World.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            # Worlds
            c.execute("""
                CREATE TABLE IF NOT EXISTS worlds (
                    world_id TEXT PRIMARY KEY,
                    master_seed INTEGER,
                    profile TEXT,
                    created_at INTEGER,
                    current_time INTEGER,
                    config_hash TEXT
                );
            """)

            # Customers
            c.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    tier TEXT,
                    sensitivity_type TEXT,
                    fatigue_rolling_24h REAL,
                    fatigue_rolling_7d REAL,
                    relationship_score REAL,
                    churn_status TEXT,
                    raw_json TEXT
                );
            """)

            # Payments
            c.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    merchant_id TEXT,
                    amount REAL,
                    status TEXT,
                    gateway_id TEXT,
                    failure_code TEXT,
                    natural_recovery_timestamp INTEGER,
                    created_at INTEGER,
                    raw_json TEXT,
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
                );
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_v15_pmt_time ON payments(created_at);")

            # Interventions
            c.execute("""
                CREATE TABLE IF NOT EXISTS interventions (
                    intervention_id TEXT PRIMARY KEY,
                    payment_id TEXT,
                    customer_id TEXT,
                    action_type TEXT,
                    channel TEXT,
                    timestamp INTEGER,
                    direct_recovered_amount REAL,
                    natural_recovered_amount REAL,
                    incremental_revenue REAL,
                    operational_cost REAL,
                    relationship_delta REAL,
                    negative_externality REAL,
                    raw_json TEXT,
                    FOREIGN KEY(payment_id) REFERENCES payments(payment_id),
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
                );
            """)

            # Ledger Entries
            c.execute("""
                CREATE TABLE IF NOT EXISTS ledger_entries (
                    entry_id TEXT PRIMARY KEY,
                    transaction_id TEXT,
                    account_debit TEXT,
                    account_credit TEXT,
                    amount REAL,
                    timestamp INTEGER,
                    attribution_tier TEXT,
                    raw_json TEXT
                );
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_v15_ledger_tx ON ledger_entries(transaction_id);")

            # Economic Events
            c.execute("""
                CREATE TABLE IF NOT EXISTS economic_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT,
                    entity_id TEXT,
                    timestamp INTEGER,
                    sequence_index INTEGER,
                    payload_json TEXT
                );
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_v15_evt_time ON economic_events(timestamp);")

            conn.commit()

    def insert_customers(self, customers: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for cust in customers:
                d = cust.model_dump() if hasattr(cust, "model_dump") else cust
                records.append((
                    d["customer_id"],
                    d.get("tier", "SMB"),
                    d.get("sensitivity_type", "NEUTRAL"),
                    d.get("fatigue_rolling_24h", 0.0),
                    d.get("fatigue_rolling_7d", 0.0),
                    d.get("relationship_score", 0.90),
                    d.get("churn_status", "ACTIVE"),
                    json.dumps(d)
                ))
            c.executemany("INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()

    def insert_payments(self, payments: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for p in payments:
                d = p.model_dump() if hasattr(p, "model_dump") else p
                records.append((
                    d["payment_id"],
                    d["customer_id"],
                    d.get("merchant_id", "m_01"),
                    d["amount"],
                    d["status"],
                    d.get("gateway_id", "GATEWAY_A"),
                    d.get("failure_code"),
                    d.get("natural_recovery_timestamp"),
                    d.get("created_at", 1760000000),
                    json.dumps(d)
                ))
            c.executemany("INSERT OR REPLACE INTO payments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()

    def insert_interventions(self, interventions: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for inv in interventions:
                d = inv.model_dump() if hasattr(inv, "model_dump") else inv
                records.append((
                    d["intervention_id"],
                    d["payment_id"],
                    d["customer_id"],
                    d["action_type"],
                    d.get("channel", "EMAIL"),
                    d["timestamp"],
                    d.get("direct_recovered_amount", 0.0),
                    d.get("natural_recovered_amount", 0.0),
                    d.get("incremental_revenue", 0.0),
                    d.get("operational_cost", 0.0),
                    d.get("relationship_delta", 0.0),
                    d.get("negative_externality", 0.0),
                    json.dumps(d)
                ))
            c.executemany("INSERT OR REPLACE INTO interventions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()

    def insert_ledger_entries(self, entries: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for e in entries:
                d = e.model_dump() if hasattr(e, "model_dump") else e
                records.append((
                    d["entry_id"],
                    d["transaction_id"],
                    d["account_debit"],
                    d["account_credit"],
                    d["amount"],
                    d["timestamp"],
                    d.get("attribution_tier", "DIRECT_INCREMENTAL_REVENUE"),
                    json.dumps(d)
                ))
            c.executemany("INSERT OR REPLACE INTO ledger_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()

    def insert_economic_events(self, events: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for evt in events:
                d = evt.model_dump() if hasattr(evt, "model_dump") else evt
                records.append((
                    d["event_id"],
                    d["event_type"],
                    d["entity_id"],
                    d["timestamp"],
                    d.get("sequence_index", 0),
                    json.dumps(d.get("payload", {}))
                ))
            c.executemany("INSERT OR REPLACE INTO economic_events VALUES (?, ?, ?, ?, ?, ?)", records)
            conn.commit()

    def get_events_stream(self, up_to_timestamp: int) -> Generator[Dict[str, Any], None, None]:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM economic_events WHERE timestamp <= ? ORDER BY timestamp ASC, sequence_index ASC", (up_to_timestamp,))
            for row in c:
                yield {
                    "event_id": row[0],
                    "event_type": row[1],
                    "entity_id": row[2],
                    "timestamp": row[3],
                    "sequence_index": row[4],
                    "payload": json.loads(row[5]) if row[5] else {}
                }
