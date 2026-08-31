from pydantic import BaseModel, Field
from typing import Optional, Any, List
from enum import Enum
import uuid
from backend.agent.schemas import WakeReason, Plan

class MissionState(str, Enum):
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    SLEEPING = "SLEEPING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"

class AgentMission(BaseModel):
    mission_id: str = Field(default_factory=lambda: f"m_{uuid.uuid4().hex[:8]}")
    customer_id: str
    state: MissionState = MissionState.INITIALIZING
    wake_reason: WakeReason = WakeReason.NONE
    current_plan: Optional[Plan] = None
    plan_history: List[Plan] = Field(default_factory=list)
    last_event: Optional[Any] = None
    created_at: int = 0
    updated_at: int = 0
    
    def sleep(self, reason: WakeReason):
        self.state = MissionState.SLEEPING
        self.wake_reason = reason

    def wake(self, event: Any):
        self.state = MissionState.ACTIVE
        self.wake_reason = WakeReason.NONE
        self.last_event = event

    def add_plan(self, plan: Plan):
        if self.current_plan:
            self.plan_history.append(self.current_plan)
        self.current_plan = plan
