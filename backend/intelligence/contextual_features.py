from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from simulator.clock import clock
from backend.benchmark.firewall import TemporalObservationFirewall

class ContextualFeatures(BaseModel):
    payment_id: str
    customer_id: str
    failure_code: str
    rail: str
    gateway_id: str
    gateway_health: float
    complaints: int
    segment: str
    payment_age_seconds: int
    is_settled: bool = False
    feature_timestamp: int = Field(default_factory=clock.now)

class ContextualFeatureExtractor:
    """
    Extracts strictly bounded, observation-only contextual features.
    Guaranteed to block lookahead leakage via TemporalObservationFirewall.
    """
    @staticmethod
    def extract_features(
        payment: Dict[str, Any],
        customer: Dict[str, Any],
        gateway_health: float
    ) -> ContextualFeatures:
        now = clock.now()
        
        # Verify no future leakage
        TemporalObservationFirewall.verify_time_boundary(payment.get("created_at", now))
        TemporalObservationFirewall.verify_time_boundary(customer.get("created_at", now))

        p_created = int(payment.get("created_at", now))
        age = max(0, now - p_created)

        return ContextualFeatures(
            payment_id=str(payment.get("id", "pmt_unknown")),
            customer_id=str(customer.get("id", "c_unknown")),
            failure_code=str(payment.get("failure_code", "UNKNOWN")),
            rail=str(payment.get("rail", "CARD")),
            gateway_id=str(payment.get("gateway_id", "GATEWAY_A")),
            gateway_health=float(gateway_health),
            complaints=int(customer.get("complaints", 0)),
            segment=str(customer.get("segment", "B2B_MIDMARKET")),
            payment_age_seconds=age,
            is_settled=(payment.get("status") == "SETTLED"),
            feature_timestamp=now
        )

contextual_feature_extractor = ContextualFeatureExtractor()
