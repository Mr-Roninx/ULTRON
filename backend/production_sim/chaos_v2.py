from typing import Dict, Any, List, Optional
from simulator.clock import clock
from backend.payment_intelligence.rail_health import rail_health_engine

class ChaosEngineV2:
    """
    Simulates production environment volatility across gateways, webhooks, and customer behaviors.
    """
    def __init__(self):
        self.active_perturbations: List[Dict[str, Any]] = []

    def inject_gateway_degradation(self, gateway_id: str = "GATEWAY_A", health: float = 0.10, latency_ms: float = 4500.0):
        rail_health_engine.update_gateway_health(gateway_id, success_probability=health, latency_ms=latency_ms)
        self.active_perturbations.append({
            "type": "GATEWAY_DEGRADATION",
            "target": gateway_id,
            "health": health,
            "timestamp": clock.now()
        })

    def inject_webhook_delay(self, delay_seconds: int = 7200):
        self.active_perturbations.append({
            "type": "WEBHOOK_DELAY",
            "delay_seconds": delay_seconds,
            "timestamp": clock.now()
        })

    def inject_customer_delay(self, delay_seconds: int = 14400):
        self.active_perturbations.append({
            "type": "CUSTOMER_DELAY",
            "delay_seconds": delay_seconds,
            "timestamp": clock.now()
        })

    def evaluate_chaos_response(self, agent_replan_count: int, initial_plan_valid: bool) -> Dict[str, Any]:
        has_chaos = len(self.active_perturbations) > 0
        replan_req = not initial_plan_valid

        replan_trig = (agent_replan_count > 0)
        successful_replan = (replan_req and replan_trig)
        false_replan = (not replan_req and replan_trig)
        missed_replan = (replan_req and not replan_trig)

        return {
            "chaos_detected": has_chaos,
            "replan_required": replan_req,
            "replan_triggered": replan_trig,
            "false_replan": false_replan,
            "missed_replan": missed_replan,
            "successful_replan": successful_replan,
            "recovery_after_replan": successful_replan
        }

    def reset(self):
        self.active_perturbations.clear()

chaos_engine_v2 = ChaosEngineV2()
