from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class MacroEconomicShock(BaseModel):
    shock_id: str
    shock_type: str # SEASONAL_DEMAND_SURGE, SALARY_LIQUIDITY_SHIFT, GATEWAY_DISRUPTION, FEE_INCREASE
    target_entity: str
    magnitude: float # Multiplier or offset
    start_timestamp: int
    end_timestamp: int
    applied: bool = False
    payload: Dict[str, Any] = Field(default_factory=dict)

class MacroShockEngine:
    """
    Simulates macro-level exogenous economic shocks hidden from the agent until observable effects manifest.
    """
    def __init__(self):
        self.scheduled_shocks: List[MacroEconomicShock] = []

    def schedule_shock(self, shock: MacroEconomicShock):
        self.scheduled_shocks.append(shock)

    def get_active_shocks(self, current_timestamp: int) -> List[MacroEconomicShock]:
        return [s for s in self.scheduled_shocks if s.start_timestamp <= current_timestamp <= s.end_timestamp]
