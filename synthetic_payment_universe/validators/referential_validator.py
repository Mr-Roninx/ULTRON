from typing import List, Dict, Any, Tuple, Set
from synthetic_payment_universe.schema.entities import Customer, Merchant, Payment

class UniverseReferentialValidator:
    """
    Validates referential integrity across relational entities (Customer, Merchant, Payment).
    """
    @staticmethod
    def validate_relationships(
        customers: List[Customer],
        merchants: List[Merchant],
        payments: List[Payment]
    ) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        cust_ids: Set[str] = {c.customer_id for c in customers}
        merch_ids: Set[str] = {m.merchant_id for m in merchants}

        for p in payments:
            if p.customer_id not in cust_ids:
                errors.append(f"Foreign Key Error: Payment {p.payment_id} references missing customer {p.customer_id}")
            if p.merchant_id not in merch_ids:
                errors.append(f"Foreign Key Error: Payment {p.payment_id} references missing merchant {p.merchant_id}")

        return len(errors) == 0, errors
