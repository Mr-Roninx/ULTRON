from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class LatentLiquidityProfile(BaseModel):
    customer_id: str
    salary_day: int = 1
    monthly_inflow: float = 100000.0
    current_cash_reserve: float = 25000.0
    liquidity_cycle: str = "SALARY_CYCLE" # SALARY_CYCLE, CASHFLOW_VOLATILE, MONTH_END
    next_salary_timestamp: int = 1760000000 + (30 * 86400)

class CivilizationLiquidityEngine:
    """
    Evaluator-only latent liquidity dynamics. Hidden from ULTRON Agent.
    """
    def __init__(self):
        self._profiles: Dict[str, LatentLiquidityProfile] = {}

    def register_profile(self, profile: LatentLiquidityProfile):
        self._profiles[profile.customer_id] = profile

    def get_profile(self, customer_id: str) -> Optional[LatentLiquidityProfile]:
        return self._profiles.get(customer_id)

    def is_customer_liquid(self, customer_id: str, current_timestamp: int) -> bool:
        prof = self._profiles.get(customer_id)
        if not prof:
            return True
        # If within 5 days after salary day -> highly liquid
        time_to_salary = (prof.next_salary_timestamp - current_timestamp) % (30 * 86400)
        return time_to_salary > (25 * 86400) or prof.current_cash_reserve > 10000.0

latent_civilization_liquidity_engine = CivilizationLiquidityEngine()
