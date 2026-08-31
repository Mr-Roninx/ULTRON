from typing import Dict, Any, List, Optional
from synthetic_payment_universe.schema.entities import GroundTruthOutcome

class HiddenOracle:
    """
    Evaluator-only ground truth repository.
    Stores latent customer profiles, true root causes, counterfactuals, and natural recovery trajectories.
    Strictly forbidden from being accessed by the agent decision loop.
    """
    def __init__(self):
        self._ground_truths: Dict[str, GroundTruthOutcome] = {}
        self._latent_liquidity_windows: Dict[str, Dict[str, Any]] = {}

    def register_ground_truth(self, ground_truth: GroundTruthOutcome):
        self._ground_truths[ground_truth.payment_id] = ground_truth

    def register_liquidity_window(self, customer_id: str, next_window_timestamp: int, expected_inflow: float):
        self._latent_liquidity_windows[customer_id] = {
            "next_window_timestamp": next_window_timestamp,
            "expected_inflow": expected_inflow
        }

    def get_ground_truth(self, payment_id: str) -> Optional[GroundTruthOutcome]:
        return self._ground_truths.get(payment_id)

    def get_liquidity_window(self, customer_id: str) -> Optional[Dict[str, Any]]:
        return self._latent_liquidity_windows.get(customer_id)

    def reset(self):
        self._ground_truths.clear()
        self._latent_liquidity_windows.clear()

hidden_oracle = HiddenOracle()
