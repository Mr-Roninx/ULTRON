from typing import Dict, Any, List
from synthetic_payment_universe.world_v13.observation.api import WorldObservationAPI

class ObservationSliceBuilder:
    """
    Assembles customer, payment, invoice, and gateway telemetry into an agent context payload.
    """
    def __init__(self, observation_api: WorldObservationAPI):
        self.observation_api = observation_api

    def build_opportunity_slice(self, customer_id: str, payment_id: str, gateway_id: str = "GATEWAY_A") -> Dict[str, Any]:
        cust = self.observation_api.observe_customer(customer_id) or {}
        pmt = self.observation_api.observe_payment(payment_id) or {}
        gw = self.observation_api.observe_gateway(gateway_id)

        return {
            "current_time": self.observation_api.get_current_time(),
            "customer": cust,
            "payment": pmt,
            "gateway": gw
        }
