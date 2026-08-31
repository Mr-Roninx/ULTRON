import sqlite3
import os
import json
from typing import List, Dict, Any
from synthetic_payment_universe.schema.entities import Customer, Merchant, Payment, PaymentAttempt, GroundTruthOutcome

class UniverseSQLiteEngine:
    """
    Lightweight relational SQLite database for interactive querying and simulation testing.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    name TEXT,
                    segment TEXT,
                    fatigue_score REAL,
                    average_transaction_value REAL,
                    created_at INTEGER
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS merchants (
                    merchant_id TEXT PRIMARY KEY,
                    name TEXT,
                    industry TEXT,
                    monthly_volume REAL,
                    average_order_value REAL
                )
            """)
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
                    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
                    FOREIGN KEY(merchant_id) REFERENCES merchants(merchant_id)
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS ground_truth (
                    truth_id TEXT PRIMARY KEY,
                    payment_id TEXT,
                    true_root_cause TEXT,
                    eventual_payment INTEGER,
                    eventual_recovery_amount REAL,
                    oracle_optimal_action TEXT,
                    FOREIGN KEY(payment_id) REFERENCES payments(payment_id)
                )
            """)
            conn.commit()

    def insert_batch(
        self,
        customers: List[Customer],
        merchants: List[Merchant],
        payments: List[Payment],
        ground_truths: List[GroundTruthOutcome]
    ):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.executemany(
                "INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?)",
                [(cust.customer_id, cust.name, cust.segment, cust.fatigue_score, cust.average_transaction_value, cust.created_at) for cust in customers]
            )
            c.executemany(
                "INSERT OR REPLACE INTO merchants VALUES (?, ?, ?, ?, ?)",
                [(m.merchant_id, m.name, m.industry, m.monthly_volume, m.average_order_value) for m in merchants]
            )
            c.executemany(
                "INSERT OR REPLACE INTO payments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(p.payment_id, p.customer_id, p.merchant_id, p.amount, p.currency, p.status, p.rail, p.gateway_id, p.failure_code, p.created_at) for p in payments]
            )
            c.executemany(
                "INSERT OR REPLACE INTO ground_truth VALUES (?, ?, ?, ?, ?, ?)",
                [(gt.truth_id, gt.payment_id, gt.true_root_cause, 1 if gt.eventual_payment else 0, gt.eventual_recovery_amount, gt.oracle_optimal_action) for gt in ground_truths]
            )
            conn.commit()
