from typing import Dict, Any

class CommunicationPolicyEngine:
    """
    Enforces customer contact rate limits, channel preferences, and anti-fatigue safeguards.
    """
    MAX_CONTACTS_PER_24H = 3

    @classmethod
    def can_contact_customer(cls, customer_id: str, current_contact_count_24h: int, is_opted_out: bool = False) -> bool:
        if is_opted_out:
            return False
        if current_contact_count_24h >= cls.MAX_CONTACTS_PER_24H:
            return False
        return True

communication_policy = CommunicationPolicyEngine()
