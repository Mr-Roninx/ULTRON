from typing import List, Dict, Any
from pydantic import BaseModel
from synthetic_payment_universe.world_v13.scheduler.capacity_guard import AgentCapacityGuard

class RecoveryOpportunity(BaseModel):
    opportunity_id: str
    opportunity_type: str # FAILED_PAYMENT, SUBSCRIPTION_DUE, OVERDUE_INVOICE, ABANDONED_CHECKOUT
    customer_id: str
    amount: float
    urgency_score: float # [0.0, 1.0]
    expected_nev: float
    age_seconds: int

class OpportunityScheduler:
    """
    Ranks recovery opportunities deterministically based on NEV, urgency, exposure, and relationship cost.
    """
    def __init__(self, capacity_guard: AgentCapacityGuard):
        self.capacity_guard = capacity_guard

    def rank_opportunities(self, opportunities: List[RecoveryOpportunity], current_timestamp: int) -> List[RecoveryOpportunity]:
        # Filter through capacity guard
        eligible = [o for o in opportunities if self.capacity_guard.can_execute_action(o.customer_id, current_timestamp)]
        # Sort by expected NEV descending, then urgency descending
        return sorted(eligible, key=lambda x: (x.expected_nev, x.urgency_score), reverse=True)
