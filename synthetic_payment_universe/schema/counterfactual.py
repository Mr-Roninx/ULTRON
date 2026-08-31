from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from synthetic_payment_universe.schema.visibility import EventVisibility

class CounterfactualBranch(BaseModel):
    branch_id: str
    decision_point_id: str
    action_type: str # e.g. WAIT, RETRY, SEND_PAYMENT_LINK, SWITCH_GATEWAY, ESCALATE
    branch_subseed: int
    fork_timestamp: int

class CounterfactualOutcome(BaseModel):
    branch_id: str
    decision_point_id: str
    payment_id: str
    customer_id: str
    action_type: str
    success: bool
    recovered_amount: float
    operational_cost: float
    relationship_cost: float
    net_economic_value: float
    time_to_recovery_seconds: int
    customer_churn_occurred: bool
    visibility: EventVisibility = EventVisibility.EVALUATOR_ONLY
