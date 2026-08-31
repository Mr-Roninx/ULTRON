from typing import Dict, Any
from synthetic_payment_universe.world_v13.repository import SQLiteCivilizationRepository

class WorldCivilizationMetrics:
    """
    Computes real-time macroeconomic metrics directly from the persistent SQLite tables.
    """
    @staticmethod
    def compute_metrics(repository: SQLiteCivilizationRepository) -> Dict[str, Any]:
        with repository.get_connection() as conn:
            c = conn.cursor()
            # Payments
            c.execute("SELECT status, COUNT(*), SUM(amount) FROM payments GROUP BY status")
            pmt_stats = {row[0]: {"count": row[1], "volume": row[2]} for row in c.fetchall()}

            # Customers
            c.execute("SELECT COUNT(*), AVG(fatigue_score), AVG(relationship_score) FROM customers")
            cust_row = c.fetchone()

            # Ledger
            c.execute("SELECT SUM(amount) FROM ledger_entries")
            ledger_total = c.fetchone()[0] or 0.0

            return {
                "payment_statistics": pmt_stats,
                "customer_count": cust_row[0] if cust_row else 0,
                "average_fatigue": round(cust_row[1] or 0.0, 3),
                "average_relationship": round(cust_row[2] or 0.0, 3),
                "ledger_transaction_volume": round(ledger_total, 2)
            }
