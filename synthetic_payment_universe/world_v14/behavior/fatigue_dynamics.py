from synthetic_payment_universe.world_v14.population.customer_cohorts import PopulationCustomerEntity

class PopulationFatigueDynamics:
    """
    Manages channel contact fatigue and daily exponential decay.
    """
    @staticmethod
    def apply_contact_fatigue(customer: PopulationCustomerEntity, channel: str):
        channel_deltas = {
            "EMAIL": 0.04,
            "SMS": 0.08,
            "WHATSAPP": 0.12,
            "VOICE": 0.25,
            "HUMAN_ESCALATION": 0.02
        }
        delta = channel_deltas.get(channel.upper(), 0.08)
        customer.fatigue_score = min(1.0, round(customer.fatigue_score + delta, 3))

    @staticmethod
    def decay_fatigue(customer: PopulationCustomerEntity, days_passed: float):
        factor = 0.82 ** days_passed
        customer.fatigue_score = max(0.0, round(customer.fatigue_score * factor, 3))
