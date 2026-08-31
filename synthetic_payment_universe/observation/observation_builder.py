from typing import Dict, Any, List, Optional
from simulator.clock import clock
from synthetic_payment_universe.schema.entities import Customer, Payment, Gateway, Rail
from synthetic_payment_universe.observation.firewall import UniverseObservationFirewall
from synthetic_payment_universe.world.temporal_engine import temporal_world_engine

class UniverseObservationAPI:
    """
    Public Observable World Interface for ULTRON.
    Exposes strictly bounded historical slices through UniverseObservationFirewall.
    """
    def __init__(self):
        self._customers: Dict[str, Customer] = {}
        self._payments: Dict[str, Payment] = {}
        self._gateways: Dict[str, Gateway] = {}
        self._rails: Dict[str, Rail] = {}

    def register_entities(
        self,
        customers: Optional[List[Customer]] = None,
        payments: Optional[List[Payment]] = None,
        gateways: Optional[List[Gateway]] = None,
        rails: Optional[List[Rail]] = None
    ):
        for c in (customers or []):
            self._customers[c.customer_id] = c
        for p in (payments or []):
            self._payments[p.payment_id] = p
        for g in (gateways or []):
            self._gateways[g.gateway_id] = g
        for r in (rails or []):
            self._rails[r.rail_id] = r

    def observe_payment(self, payment_id: str, current_time: int) -> Optional[Dict[str, Any]]:
        pmt = self._payments.get(payment_id)
        if not pmt:
            return None
        return UniverseObservationFirewall.sanitize_for_agent(pmt.model_dump(), current_time)

    def observe_customer(self, customer_id: str, current_time: int) -> Optional[Dict[str, Any]]:
        cust = self._customers.get(customer_id)
        if not cust:
            return None
        return UniverseObservationFirewall.sanitize_for_agent(cust.model_dump(), current_time)

    def observe_gateway(self, gateway_id: str, current_time: int) -> Optional[Dict[str, Any]]:
        gw = self._gateways.get(gateway_id)
        if not gw:
            return None
        return UniverseObservationFirewall.sanitize_for_agent(gw.model_dump(), current_time)

    def observe_rail(self, rail_id: str, current_time: int) -> Optional[Dict[str, Any]]:
        r = self._rails.get(rail_id)
        if not r:
            return None
        return UniverseObservationFirewall.sanitize_for_agent(r.model_dump(), current_time)

    def observe_customer_exposure(self, customer_id: str, current_time: int) -> Dict[str, Any]:
        matched = [p for p in self._payments.values() if p.customer_id == customer_id and p.created_at <= current_time]
        total_exp = sum(p.amount for p in matched if p.status in ["FAILED", "PENDING", "OPEN"])
        return {
            "customer_id": customer_id,
            "total_exposure": round(total_exp, 2),
            "pending_payment_count": len(matched),
            "observation_time": current_time
        }

    def observe_events(self, current_time: int) -> List[Dict[str, Any]]:
        events = temporal_world_engine.get_events_until(current_time)
        return [e.model_dump() for e in events]

    def reset(self):
        self._customers.clear()
        self._payments.clear()
        self._gateways.clear()
        self._rails.clear()

universe_observation_api = UniverseObservationAPI()
