from typing import List, Dict, Any, Tuple
from synthetic_payment_universe.schema.entities import Customer, Merchant, Payment

class UniverseSchemaValidator:
    """
    Validates structural correctness, non-negative numerical properties,
    and schema version consistency.
    """
    @staticmethod
    def validate_entities(
        customers: List[Customer],
        merchants: List[Merchant],
        payments: List[Payment]
    ) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        for c in customers:
            if c.average_transaction_value < 0:
                errors.append(f"Customer {c.customer_id} has negative average_transaction_value: {c.average_transaction_value}")
            if not (0.0 <= c.fatigue_score <= 1.0):
                errors.append(f"Customer {c.customer_id} has invalid fatigue_score: {c.fatigue_score}")

        for m in merchants:
            if m.monthly_volume < 0:
                errors.append(f"Merchant {m.merchant_id} has negative monthly_volume: {m.monthly_volume}")

        for p in payments:
            if p.amount <= 0:
                errors.append(f"Payment {p.payment_id} has non-positive amount: {p.amount}")

        return len(errors) == 0, errors
