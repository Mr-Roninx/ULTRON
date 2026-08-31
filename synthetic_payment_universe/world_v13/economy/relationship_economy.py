from typing import Dict, Any
from synthetic_payment_universe.world_v13.economy.customer_economy import CustomerEconomyEntity

class CustomerRelationshipEngine:
    """
    Tracks long-term customer trust, relationship score, and goodwill retention.
    """
    @staticmethod
    def adjust_relationship(customer: CustomerEconomyEntity, delta: float):
        new_score = customer.relationship_score + delta
        customer.relationship_score = max(0.0, min(1.0, round(new_score, 3)))
        if customer.relationship_score < 0.30:
            customer.churn_probability = min(0.95, round(customer.churn_probability + 0.20, 3))
        elif customer.relationship_score > 0.85:
            customer.churn_probability = max(0.01, round(customer.churn_probability * 0.90, 3))
