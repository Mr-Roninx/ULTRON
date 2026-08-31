import json
from typing import Dict, Any, Optional
from synthetic_payment_universe.world_v14.repository import SQLiteEmergentRepository
from synthetic_payment_universe.world_v14.observation.recursive_firewall import RecursiveObservationFirewall

class PopulationObservationBuilder:
    """
    Constructs sanitized agent observation context slices from persistent storage.
    """
    def __init__(self, repository: SQLiteEmergentRepository):
        self.repository = repository

    def build_slice(self, customer_id: str, payment_id: str, current_time: int) -> Dict[str, Any]:
        cust = {}
        pmt = {}
        with self.repository.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT raw_json FROM customers WHERE customer_id = ?", (customer_id,))
            row_c = c.fetchone()
            if row_c:
                cust = RecursiveObservationFirewall.sanitize(json.loads(row_c[0]), current_time)

            c.execute("SELECT raw_json FROM payments WHERE payment_id = ?", (payment_id,))
            row_p = c.fetchone()
            if row_p:
                pmt = RecursiveObservationFirewall.sanitize(json.loads(row_p[0]), current_time)

        return {
            "current_time": current_time,
            "customer": cust,
            "payment": pmt
        }
