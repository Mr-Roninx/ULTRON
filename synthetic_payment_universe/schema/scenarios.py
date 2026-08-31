from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class GoldenScenarioDefinition(BaseModel):
    scenario_id: str
    name: str
    description: str
    customer_segment: str
    initial_amount: float
    iso_failure_code: str
    initial_rail: str
    initial_gateway: str
    initial_gateway_health: float
    future_events: List[Dict[str, Any]] = Field(default_factory=list)
    evaluation_target: str
