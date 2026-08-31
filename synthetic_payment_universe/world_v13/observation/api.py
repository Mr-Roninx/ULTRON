import json
from typing import Dict, Any, List, Optional
from synthetic_payment_universe.world_v13.clock import economic_clock
from synthetic_payment_universe.world_v13.repository import SQLiteCivilizationRepository
from synthetic_payment_universe.world_v13.economy.gateway_economy import GatewayEconomyEngine
from synthetic_payment_universe.world_v13.observation.firewall import CivilizationObservationFirewall

class WorldObservationAPI:
    """
    Exposes sanitized observable state to the ULTRON Agent at current virtual clock time.
    """
    def __init__(self, repository: SQLiteCivilizationRepository, gateway_economy: GatewayEconomyEngine):
        self.repository = repository
        self.gateway_economy = gateway_economy

    def get_current_time(self) -> int:
        return economic_clock.now()

    def observe_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        now = economic_clock.now()
        with self.repository.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT raw_json FROM customers WHERE customer_id = ? AND created_at <= ?", (customer_id, now))
            row = c.fetchone()
            if not row:
                return None
            return CivilizationObservationFirewall.sanitize(json.loads(row[0]), now)

    def observe_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        now = economic_clock.now()
        with self.repository.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT raw_json FROM payments WHERE payment_id = ? AND created_at <= ?", (payment_id, now))
            row = c.fetchone()
            if not row:
                return None
            return CivilizationObservationFirewall.sanitize(json.loads(row[0]), now)

    def observe_gateway(self, gateway_id: str) -> Dict[str, Any]:
        now = economic_clock.now()
        gw = self.gateway_economy.gateways.get(gateway_id)
        if not gw:
            return {"gateway_id": gateway_id, "health_score": 0.90, "latency_ms": 150.0}
        return CivilizationObservationFirewall.sanitize(gw.model_dump(), now)

    def observe_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        now = economic_clock.now()
        with self.repository.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT raw_json FROM invoices WHERE invoice_id = ?", (invoice_id,))
            row = c.fetchone()
            if not row:
                return None
            return CivilizationObservationFirewall.sanitize(json.loads(row[0]), now)
