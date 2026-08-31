from synthetic_payment_universe.world_v13.economy.customer_economy import CustomerEconomyEntity

class FatigueDynamics:
    """
    Manages channel-specific fatigue accumulation and time-based recovery.
    """
    @staticmethod
    def calculate_contact_fatigue_penalty(customer: CustomerEconomyEntity) -> float:
        if customer.fatigue_score < 0.30:
            return 1.0 # No penalty
        elif customer.fatigue_score < 0.70:
            return 0.70 # Moderate penalty
        else:
            return 0.25 # Severe penalty
