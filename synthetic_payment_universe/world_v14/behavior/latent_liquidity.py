from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class LatentLiquidityProfileV14(BaseModel):
    customer_id: str
    salary_day: int = 1
    monthly_inflow: float = 120000.0
    cash_reserve: float = 35000.0
    liquidity_cycle: str = "SALARY_CYCLE"
    next_inflow_timestamp: int = 1760000000 + (30 * 86400)

class PopulationLiquidityEngine:
    """
    Evaluator-only latent liquidity dynamics. Strictly forbidden from Agent context.
    """
    def __init__(self):
        self._profiles: Dict[str, LatentLiquidityProfileV14] = {}

    def register(self, profile: LatentLiquidityProfileV14):
        self._profiles[profile.customer_id] = profile

    def is_liquid(self, customer_id: str, current_timestamp: int) -> bool:
        p = self._profiles.get(customer_id)
        if not p:
            return True
        days_to_inflow = (p.next_inflow_timestamp - current_timestamp) / 86400.0
        return p.cash_reserve > 10000.0 or (days_to_inflow % 30) < 5

latent_population_liquidity_engine = PopulationLiquidityEngine()
