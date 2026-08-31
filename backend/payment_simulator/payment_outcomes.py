import random
from typing import Dict, Any, Tuple
from simulator.models import PaymentStatus
from backend.payment_intelligence.rail_health import rail_health_engine
from backend.payment_intelligence.failure_taxonomy import failure_taxonomy
from simulator.clock import clock

class PaymentOutcomeSimulator:
    """
    Deterministically simulates payment outcomes given action, failure diagnosis,
    gateway/rail health, and seeded stochasticity.
    """
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def reseed(self, seed: int):
        self.rng = random.Random(seed)

    def simulate_retry_outcome(
        self,
        payment_id: str,
        gateway_id: str,
        rail: str,
        failure_code: str,
        attempt_count: int = 1
    ) -> Tuple[PaymentStatus, Dict[str, Any]]:
        # 1. Gateway Health Check
        gw_health = rail_health_engine.get_gateway_health(gateway_id)
        rule = failure_taxonomy.get_rule(failure_code)

        # Base probability from taxonomy and gateway
        if not rule.retry_eligible:
            # Not retryable (e.g. expired card, closed account)
            return PaymentStatus.FAILED, {"reason": "NON_RETRYABLE_TAXONOMY", "effective_prob": 0.0}

        base_p = rule.base_recoverability
        gw_factor = gw_health.success_probability
        
        # Attempt decay: each retry has slightly lower marginal probability
        decay = max(0.4, 1.0 - ((attempt_count - 1) * 0.15))

        effective_prob = base_p * gw_factor * decay

        roll = self.rng.random()
        success = roll < effective_prob

        if success:
            return PaymentStatus.SETTLED, {
                "settled_at": clock.now(),
                "effective_prob": round(effective_prob, 4),
                "gateway_id": gateway_id,
                "roll": round(roll, 4)
            }
        else:
            return PaymentStatus.FAILED, {
                "failed_at": clock.now(),
                "effective_prob": round(effective_prob, 4),
                "gateway_id": gateway_id,
                "roll": round(roll, 4),
                "failure_code": failure_code if gw_factor > 0.3 else "GATEWAY_DOWN"
            }

    def simulate_payment_link_outcome(
        self,
        customer_segment: str,
        amount: float,
        contact_count: int = 0
    ) -> Tuple[PaymentStatus, Dict[str, Any]]:
        # Segment-specific link settlement probability
        segment_base = {
            "B2B_ENTERPRISE": 0.82,
            "B2B_MIDMARKET": 0.75,
            "SMB": 0.65,
            "CONSUMER": 0.55
        }.get(customer_segment, 0.65)

        # Fatigue penalty
        fatigue = max(0.3, 1.0 - (contact_count * 0.10))
        effective_prob = segment_base * fatigue

        roll = self.rng.random()
        success = roll < effective_prob

        if success:
            return PaymentStatus.SETTLED, {
                "settled_at": clock.now(),
                "effective_prob": round(effective_prob, 4),
                "channel": "PAYMENT_LINK"
            }
        else:
            return PaymentStatus.FAILED, {
                "failed_at": clock.now(),
                "effective_prob": round(effective_prob, 4),
                "channel": "PAYMENT_LINK"
            }

payment_outcome_simulator = PaymentOutcomeSimulator()
