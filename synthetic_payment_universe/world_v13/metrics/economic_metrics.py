from typing import Dict, Any, List

class AgentEconomicMetrics:
    """
    Computes incremental recovered revenue, operational cost, customer relationship cost, and cumulative NEV.
    """
    @staticmethod
    def calculate_summary(recoveries: List[Dict[str, Any]]) -> Dict[str, Any]:
        gross_rec = sum(r.get("recovered_amount", 0.0) for r in recoveries)
        op_cost = sum(r.get("operational_cost", 0.0) for r in recoveries)
        rel_cost = sum(r.get("relationship_cost", 0.0) for r in recoveries)
        nev = round(gross_rec - op_cost - rel_cost, 2)
        return {
            "total_recoveries": len(recoveries),
            "gross_recovered_revenue": round(gross_rec, 2),
            "total_operational_cost": round(op_cost, 2),
            "total_relationship_cost": round(rel_cost, 2),
            "net_economic_value": nev
        }
