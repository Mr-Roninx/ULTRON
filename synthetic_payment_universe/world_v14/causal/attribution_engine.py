from typing import Dict, Any

class CausalAttributionEngine:
    """
    Computes true causal economic lift by comparing ULTRON outcomes against aligned counterfactual controls.
    """
    @staticmethod
    def calculate_causal_lift(ultron_recovery: float, control_natural_recovery: float, ultron_operational_cost: float) -> Dict[str, Any]:
        incremental_rec = max(0.0, ultron_recovery - control_natural_recovery)
        incremental_nev = round(incremental_rec - ultron_operational_cost, 2)
        return {
            "ultron_gross_recovery": round(ultron_recovery, 2),
            "control_natural_recovery": round(control_natural_recovery, 2),
            "incremental_recovery": round(incremental_rec, 2),
            "operational_cost": round(ultron_operational_cost, 2),
            "incremental_net_economic_value": incremental_nev
        }
