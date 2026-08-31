import os
import sqlite3
import json
from typing import Dict, Any, List, Optional, Generator
from pydantic import BaseModel

class SQLiteWorldRepository:
    """
    Authoritative persistent repository for ULTRON-SWU-1.2.
    Survives process restarts, uses indexed SQLite relational tables with WAL mode,
    and supports streaming generators with bounded memory usage.
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
            # World Metadata
            c.execute("""
                CREATE TABLE IF NOT EXISTS world_metadata (
                    world_id TEXT PRIMARY KEY,
                    master_seed INTEGER,
                    partition_name TEXT,
                    created_at INTEGER,
                    simulation_start INTEGER,
                    simulation_end INTEGER,
                    current_time INTEGER,
                    schema_version TEXT,
                    configuration_hash TEXT,
                    config_json TEXT
                );
            """)

            # Customers
            c.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    tier TEXT,
                    behavior_profile TEXT,
                    fatigue_score REAL,
                    average_transaction_value REAL,
                    historical_success_rate REAL,
                    created_at INTEGER,
                    raw_json TEXT
                );
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_customers_tier ON customers(tier);")

            # Merchants
            c.execute("""
                CREATE TABLE IF NOT EXISTS merchants (
                    merchant_id TEXT PRIMARY KEY,
                    industry TEXT,
                    monthly_volume REAL,
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
                    currency TEXT,
                    status TEXT,
                    rail TEXT,
                    gateway_id TEXT,
                    failure_code TEXT,
                    created_at INTEGER,
                    raw_json TEXT,
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
                    FOREIGN KEY(merchant_id) REFERENCES merchants(merchant_id)
                );
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_payments_cust ON payments(customer_id);")
            c.execute("CREATE INDEX IF NOT EXISTS idx_payments_time ON payments(created_at);")
            c.execute("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);")

            # Events
            c.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT,
                    entity_id TEXT,
                    timestamp INTEGER,
                    visibility TEXT,
                    causal_parent_id TEXT,
                    payload_json TEXT
                );
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_time ON events(timestamp);")
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_entity ON events(entity_id);")

            # Ledger Entries (Double-Entry)
            c.execute("""
                CREATE TABLE IF NOT EXISTS ledger_entries (
                    entry_id TEXT PRIMARY KEY,
                    transaction_id TEXT,
                    source_event_id TEXT,
                    account_debit TEXT,
                    account_credit TEXT,
                    amount REAL,
                    currency TEXT,
                    timestamp INTEGER,
                    reconciled INTEGER
                );
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_ledger_tx ON ledger_entries(transaction_id);")

            # Ground Truth (Evaluator-Only)
            c.execute("""
                CREATE TABLE IF NOT EXISTS ground_truth (
                    truth_id TEXT PRIMARY KEY,
                    payment_id TEXT,
                    true_root_cause TEXT,
                    eventual_payment INTEGER,
                    eventual_recovery_amount REAL,
                    natural_recovery_timestamp INTEGER,
                    oracle_optimal_action TEXT,
                    FOREIGN KEY(payment_id) REFERENCES payments(payment_id)
                );
            """)
            conn.commit()

    def save_world_metadata(self, identity: BaseModel, config_dict: Dict[str, Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            id_dict = identity.model_dump()
            c.execute("""
                INSERT OR REPLACE INTO world_metadata VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_dict["world_id"],
                id_dict["master_seed"],
                id_dict["partition_name"],
                id_dict["created_at"],
                id_dict["simulation_start"],
                id_dict["simulation_end"],
                id_dict["current_time"],
                id_dict["schema_version"],
                id_dict["configuration_hash"],
                json.dumps(config_dict)
            ))
            conn.commit()

    def load_world_metadata(self, world_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM world_metadata WHERE world_id = ?", (world_id,))
            row = c.fetchone()
            if not row:
                return None
            return {
                "world_id": row[0],
                "master_seed": row[1],
                "partition_name": row[2],
                "created_at": row[3],
                "simulation_start": row[4],
                "simulation_end": row[5],
                "current_time": row[6],
                "schema_version": row[7],
                "configuration_hash": row[8],
                "config": json.loads(row[9]) if row[9] else {}
            }

    def update_simulation_time(self, world_id: str, new_time: int):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE world_metadata SET current_time = ? WHERE world_id = ?", (new_time, world_id))
            conn.commit()

    def insert_merchants_chunk(self, merchants: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for m in merchants:
                d = m.model_dump() if hasattr(m, "model_dump") else m
                records.append((
                    d["merchant_id"],
                    d.get("industry", "SaaS"),
                    d.get("monthly_volume", 5000000.0),
                    json.dumps(d)
                ))
            c.executemany("INSERT OR REPLACE INTO merchants VALUES (?, ?, ?, ?)", records)
            conn.commit()

    def insert_customers_chunk(self, customers: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for cust in customers:
                d = cust.model_dump() if hasattr(cust, "model_dump") else cust
                records.append((
                    d["customer_id"],
                    d.get("tier", "SMB"),
                    d.get("latent_profile", "STANDARD"),
                    d.get("fatigue_score", 0.0),
                    d.get("average_transaction_value", 1000.0),
                    d.get("historical_success_rate", 0.85),
                    d.get("created_at", 1760000000),
                    json.dumps(d)
                ))
            c.executemany("INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()

    def insert_payments_chunk(self, payments: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for p in payments:
                d = p.model_dump() if hasattr(p, "model_dump") else p
                records.append((
                    d["payment_id"],
                    d["customer_id"],
                    d["merchant_id"],
                    d["amount"],
                    d.get("currency", "INR"),
                    d["status"],
                    d.get("rail", "CARD"),
                    d.get("gateway_id", "GATEWAY_A"),
                    d.get("failure_code"),
                    d.get("created_at", 1760000000),
                    json.dumps(d)
                ))
            c.executemany("INSERT OR REPLACE INTO payments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", records)
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
                    d.get("source_event_id", ""),
                    d["account_debit"],
                    d["account_credit"],
                    d["amount"],
                    d.get("currency", "INR"),
                    d["timestamp"],
                    1 if d.get("reconciled", True) else 0
                ))
            c.executemany("INSERT OR REPLACE INTO ledger_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()

    def insert_events_chunk(self, events: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for e in events:
                d = e.model_dump() if hasattr(e, "model_dump") else e
                records.append((
                    d["event_id"],
                    d["event_type"],
                    d["entity_id"],
                    d["timestamp"],
                    str(d.get("visibility", "OBSERVABLE")),
                    d.get("causal_parent_id"),
                    json.dumps(d.get("payload", {}))
                ))
            c.executemany("INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()

    def get_events_stream(self, up_to_timestamp: int) -> Generator[Dict[str, Any], None, None]:
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM events WHERE timestamp <= ? ORDER BY timestamp ASC", (up_to_timestamp,))
            for row in c:
                yield {
                    "event_id": row[0],
                    "event_type": row[1],
                    "entity_id": row[2],
                    "timestamp": row[3],
                    "visibility": row[4],
                    "causal_parent_id": row[5],
                    "payload": json.loads(row[6]) if row[6] else {}
                }
