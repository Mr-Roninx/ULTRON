import uuid
from typing import Dict, Any, Optional
from simulator.clock import clock

class ProductionPaymentGateway:
    """
    Idempotent simulated payment gateway supporting multi-rail processing,
    health fluctuations, latency simulation, and retry tracking.
    """
    def __init__(self, gateway_id: str = "GATEWAY_A", default_health: float = 0.95):
        self.gateway_id = gateway_id
        self.health = default_health
        self.processed_requests: Dict[str, Dict[str, Any]] = {}

    def process_payment(self, payment_id: str, amount: float, rail: str, idempotency_key: str) -> Dict[str, Any]:
        if idempotency_key in self.processed_requests:
            return self.processed_requests[idempotency_key]

        success = (self.health >= 0.50)
        result = {
            "transaction_id": f"txn_{uuid.uuid4().hex[:10]}",
            "payment_id": payment_id,
            "amount": amount,
            "rail": rail,
            "gateway_id": self.gateway_id,
            "status": "SUCCESS" if success else "FAILED",
            "failure_code": None if success else "GATEWAY_DEGRADED_503",
            "timestamp": clock.now(),
            "idempotency_key": idempotency_key
        }
        self.processed_requests[idempotency_key] = result
        return result

    def set_health(self, health: float):
        self.health = max(0.0, min(1.0, health))

    def reset(self):
        self.processed_requests.clear()
        self.health = 0.95
