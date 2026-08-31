from typing import Dict, Any, Optional

class LatentLiquidityEngine:
    """
    Evaluator-only engine tracking latent cashflow and salary cycles.
    Strictly forbidden from being observed directly by ULTRON agent loop.
    """
    def __init__(self):
        self._liquidity_states: Dict[str, Dict[str, Any]] = {}

    def register_customer_liquidity(
        self,
        customer_id: str,
        salary_day: int,
        inflow_amount: float,
        next_inflow_timestamp: int
    ):
        self._liquidity_states[customer_id] = {
            "salary_day": salary_day,
            "inflow_amount": inflow_amount,
            "next_inflow_timestamp": next_inflow_timestamp
        }

    def has_sufficient_liquidity(self, customer_id: str, amount: float, current_timestamp: int) -> bool:
        if customer_id not in self._liquidity_states:
            return True
        st = self._liquidity_states[customer_id]
        if current_timestamp >= st["next_inflow_timestamp"]:
            return True
        return amount <= (st["inflow_amount"] * 0.3)

    def get_latent_state(self, customer_id: str) -> Optional[Dict[str, Any]]:
        return self._liquidity_states.get(customer_id)

    def reset(self):
        self._liquidity_states.clear()

latent_liquidity_engine = LatentLiquidityEngine()
