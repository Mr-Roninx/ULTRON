from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.mission.mission_state import RevenueMissionState
from simulator.clock import clock

class OpportunityItem(BaseModel):
    opportunity_id: str
    opportunity_type: str  # "SUBSCRIPTION", "CHECKOUT", "INVOICE", "PAYMENT"
    amount: float
    status: str
    created_at: int = 0
    details: Dict[str, Any] = Field(default_factory=dict)

class RevenueMission(BaseModel):
    mission_id: str
    customer_id: str
    customer_name: str = "Unknown Customer"
    state: RevenueMissionState = RevenueMissionState.DISCOVERED
    opportunities: List[OpportunityItem] = Field(default_factory=list)
    total_exposure: float = 0.0
    primary_opportunity_id: Optional[str] = None
    recovered_amount: float = 0.0
    created_at: int = 0
    updated_at: int = 0
    active_plan_id: Optional[str] = None
    telemetry_trail: List[Dict[str, Any]] = Field(default_factory=list)

    def recalculate_exposure(self) -> float:
        self.total_exposure = sum(o.amount for o in self.opportunities if o.status not in ["RECOVERED", "CLOSED", "WRITTEN_OFF"])
        return self.total_exposure

    def add_opportunity(self, opportunity: OpportunityItem):
        # Prevent duplicate opportunities
        if not any(o.opportunity_id == opportunity.opportunity_id for o in self.opportunities):
            self.opportunities.append(opportunity)
            if self.primary_opportunity_id is None:
                self.primary_opportunity_id = opportunity.opportunity_id
            self.recalculate_exposure()
            self.updated_at = clock.now()

    def transition_state(self, new_state: RevenueMissionState, reason: str = ""):
        old_state = self.state
        self.state = new_state
        self.updated_at = clock.now()
        self.telemetry_trail.append({
            "from_state": old_state.value,
            "to_state": new_state.value,
            "reason": reason,
            "timestamp": clock.now()
        })
