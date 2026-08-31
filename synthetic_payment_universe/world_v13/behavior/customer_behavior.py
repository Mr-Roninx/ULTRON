import random
from typing import Dict, Any, Tuple
from synthetic_payment_universe.world_v13.economy.customer_economy import CustomerEconomyEntity

class CivilizationCustomerBehaviorEngine:
    """
    Simulates customer conversion probability under contact fatigue and communication channels.
    """
    @staticmethod
    def evaluate_outreach_response(
        customer: CustomerEconomyEntity,
        channel: str,
        subseed: int = 12345
    ) -> Tuple[bool, bool]:
        rng = random.Random(subseed + int(customer.fatigue_score * 1000))
        
        # Base channel effectiveness
        channel_base = {
            "EMAIL": 0.35,
            "SMS": 0.50,
            "WHATSAPP": 0.70,
            "VOICE": 0.40,
            "HUMAN_ESCALATION": 0.85
        }.get(channel.upper(), 0.50)

        # Fatigue penalty
        effective_open_p = max(0.05, channel_base * (1.0 - (customer.fatigue_score * 0.75)))
        opened = rng.random() < effective_open_p

        effective_conv_p = max(0.02, effective_open_p * customer.relationship_score)
        converted = opened and (rng.random() < effective_conv_p)

        return opened, converted
