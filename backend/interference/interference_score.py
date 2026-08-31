from typing import Dict, Any
from backend.interference.interference_graph import interference_graph

class InterferenceScoreEngine:
    def calculate_interference(self, customer_id: str) -> float:
        exposure = interference_graph.get_customer_exposure(customer_id)
        return exposure.get("interference_score", 0.0)

interference_score_engine = InterferenceScoreEngine()
