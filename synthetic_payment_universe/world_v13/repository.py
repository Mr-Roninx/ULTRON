import os
import sqlite3
import json
from typing import Dict, Any, List, Optional, Generator
from pydantic import BaseModel

class SQLiteCivilizationRepository:
    """
    Persistent SQLite repository for ULTRON-SWU-1.3 Economic Civilization.
    Survives restarts, maintains relational foreign-key integrity, and enables indexed streaming queries.
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
                    partition_name TEXT,
                    created_at INTEGER,
                    simulation_start INTEGER,
                    simulation_end INTEGER,
                    current_time INTEGER,
                    schema_version TEXT,
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
                    relationship_score REAL,
                    churn_probability REAL,
                    average_transaction_value REAL,
                    lifetime_value REAL,
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
                    primary_gateway_id TEXT,
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

            # Subscriptions
            c.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    subscription_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    merchant_id TEXT,
                    amount REAL,
                    interval TEXT,
                    status TEXT,
                    current_period_end INTEGER,
                    raw_json TEXT,
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
                );
            """)

            # Invoices
            c.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id TEXT PRIMARY KEY,
                    buyer_id TEXT,
                    seller_id TEXT,
                    amount REAL,
                    due_timestamp INTEGER,
                    status TEXT,
                    po_number TEXT,
                    raw_json TEXT,
                    FOREIGN KEY(buyer_id) REFERENCES customers(customer_id)
                );
            """)

            # Checkouts
            c.execute("""
                CREATE TABLE IF NOT EXISTS checkouts (
                    checkout_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    merchant_id TEXT,
                    cart_total REAL,
                    status TEXT,
                    created_at INTEGER,
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
                );
            """)

            # Communications
            c.execute("""
                CREATE TABLE IF NOT EXISTS communications (
                    communication_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    channel TEXT,
                    sent_at INTEGER,
                    delivered_at INTEGER,
                    opened_at INTEGER,
                    clicked_at INTEGER,
                    converted INTEGER,
                    fatigue_delta REAL,
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
                );
            """)

            # Disputes
            c.execute("""
                CREATE TABLE IF NOT EXISTS disputes (
                    dispute_id TEXT PRIMARY KEY,
                    payment_id TEXT,
                    invoice_id TEXT,
                    dispute_type TEXT,
                    status TEXT,
                    amount REAL,
                    created_at INTEGER
                );
            """)

            # Ledger Entries (Double-Entry Balance Sheet)
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
                    reconciled INTEGER,
                    provenance_json TEXT
                );
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_ledger_tx ON ledger_entries(transaction_id);")

            # Economic Events (Persistent Event Stream)
            c.execute("""
                CREATE TABLE IF NOT EXISTS economic_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT,
                    entity_id TEXT,
                    timestamp INTEGER,
                    visibility TEXT,
                    causal_parent_id TEXT,
                    sequence_index INTEGER,
                    payload_json TEXT
                );
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_time ON economic_events(timestamp);")
            c.execute("CREATE INDEX IF NOT EXISTS idx_events_entity ON economic_events(entity_id);")

            # Ground Truth Oracle (Evaluator-Only)
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

    def insert_merchants(self, merchants: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for m in merchants:
                d = m.model_dump() if hasattr(m, "model_dump") else m
                records.append((
                    d["merchant_id"],
                    d.get("industry", "SaaS"),
                    d.get("monthly_volume", 5000000.0),
                    d.get("primary_gateway_id", "GATEWAY_A"),
                    json.dumps(d)
                ))
            c.executemany("INSERT OR REPLACE INTO merchants VALUES (?, ?, ?, ?, ?)", records)
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
                    d.get("latent_profile", "STANDARD"),
                    d.get("fatigue_score", 0.0),
                    d.get("relationship_score", 0.90),
                    d.get("churn_probability", 0.05),
                    d.get("average_transaction_value", 15000.0),
                    d.get("lifetime_value", 200000.0),
                    d.get("historical_success_rate", 0.85),
                    d.get("created_at", 1760000000),
                    json.dumps(d)
                ))
            c.executemany("INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", records)
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

    def insert_subscriptions(self, subscriptions: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for s in subscriptions:
                d = s.model_dump() if hasattr(s, "model_dump") else s
                records.append((
                    d["subscription_id"],
                    d["customer_id"],
                    d["merchant_id"],
                    d["amount"],
                    d.get("interval", "MONTHLY"),
                    d.get("status", "ACTIVE"),
                    d.get("current_period_end", 1760000000),
                    json.dumps(d)
                ))
            c.executemany("INSERT OR REPLACE INTO subscriptions VALUES (?, ?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()

    def insert_invoices(self, invoices: List[Any]):
        with self.get_connection() as conn:
            c = conn.cursor()
            records = []
            for inv in invoices:
                d = inv.model_dump() if hasattr(inv, "model_dump") else inv
                records.append((
                    d["invoice_id"],
                    d["buyer_id"],
                    d["seller_id"],
                    d["amount"],
                    d.get("due_timestamp", 1760000000),
                    d.get("status", "OPEN"),
                    d.get("po_number"),
                    json.dumps(d)
                ))
            c.executemany("INSERT OR REPLACE INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?, ?)", records)
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
                    1 if d.get("reconciled", True) else 0,
                    json.dumps(d.get("provenance", {}))
                ))
            c.executemany("INSERT OR REPLACE INTO ledger_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", records)
            conn.commit()

    def insert_economic_events(self, events: List[Any]):
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
                    d.get("sequence_index", 0),
                    json.dumps(d.get("payload", {}))
                ))
            c.executemany("INSERT OR REPLACE INTO economic_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)", records)
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
                    "visibility": row[4],
                    "causal_parent_id": row[5],
                    "sequence_index": row[6],
                    "payload": json.loads(row[7]) if row[7] else {}
                }
