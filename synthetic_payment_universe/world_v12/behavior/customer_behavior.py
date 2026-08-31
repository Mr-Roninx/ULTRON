import random
from typing import Dict, Any, Tuple
from synthetic_payment_universe.world_v12.entities.customer import Customer

BEHAVIOR_CONVERSION_MODIFIERS: Dict[str, float] = {
    "SALARY_CYCLE": 0.85,
    "CASHFLOW_VOLATILE": 0.45,
    "PRICE_SENSITIVE": 0.60,
    "LOYAL_CUSTOMER": 0.92,
    "LOW_ENGAGEMENT": 0.30,
    "HIGH_ENGAGEMENT": 0.88,
    "BUSINESS_MONTH_END": 0.78,
    "BUSINESS_QUARTER_END": 0.82,
    "HIGH_FATIGUE": 0.20,
    "RECOVERY_RESPONSIVE": 0.90,
    "STANDARD": 0.75
}

class CustomerBehaviorEngine:
    """
    Evaluates stateful customer responses to communications and recovery actions.
    Considers fatigue, latent behavior profiles, and channel affinity.
    """
    @staticmethod
    def evaluate_communication_response(
        customer: Customer,
        channel: str,
        subseed: int
    ) -> Tuple[bool, bool, float]:
        """
        Returns (opened, converted, fatigue_increase).
        """
        rng = random.Random(subseed)
        base_mod = BEHAVIOR_CONVERSION_MODIFIERS.get(customer.latent_profile, 0.70)
        
        # Channel affinity
        channel_aff = 1.15 if channel in customer.preferred_channels else 0.80
        
        # Fatigue penalty
        effective_p = max(0.05, (base_mod * channel_aff) - (customer.fatigue_score * 0.40))

        opened = (rng.random() < min(0.98, effective_p + 0.15))
        converted = (opened and rng.random() < effective_p)

        # Fatigue delta depends on channel aggressiveness
        fatigue_map = {"EMAIL": 0.05, "SMS": 0.08, "WHATSAPP": 0.10, "VOICE": 0.20, "PAYMENT_LINK": 0.05}
        f_delta = fatigue_map.get(channel, 0.05)

        return opened, converted, f_delta
