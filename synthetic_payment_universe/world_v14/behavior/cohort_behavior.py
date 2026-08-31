import random
from typing import Tuple
from synthetic_payment_universe.world_v14.population.customer_cohorts import PopulationCustomerEntity

class CohortBehaviorEngine:
    """
    Evaluates customer outreach conversion probabilities under channel, fatigue, and relationship scores.
    """
    @staticmethod
    def evaluate_response(customer: PopulationCustomerEntity, channel: str, subseed: int = 123) -> Tuple[bool, bool]:
        rng = random.Random(subseed + int(customer.fatigue_score * 1000))
        
        channel_efficiency = {
            "EMAIL": 0.35,
            "SMS": 0.50,
            "WHATSAPP": 0.70,
            "VOICE": 0.40,
            "HUMAN_ESCALATION": 0.88
        }.get(channel.upper(), 0.50)

        # Fatigue degrades open probability
        p_open = max(0.04, channel_efficiency * (1.0 - (customer.fatigue_score * 0.70)))
        opened = rng.random() < p_open

        # Relationship trust drives conversion
        p_conv = max(0.02, p_open * customer.relationship_score)
        converted = opened and (rng.random() < p_conv)

        return opened, converted
