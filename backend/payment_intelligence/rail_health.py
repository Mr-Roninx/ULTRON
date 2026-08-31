from typing import Dict, Any, List, Optional
from backend.payment_intelligence.schemas import (
    RailType,
    RailHealthStatus,
    GatewayHealthState,
    RailHealthState
)
from simulator.clock import clock

class RailHealthEngine:
    """
    Maintains real-time simulated telemetry and degradation states
    for payment rails and gateway instances.
    """
    def __init__(self):
        self._gateways: Dict[str, GatewayHealthState] = {}
        self._rails: Dict[str, RailHealthState] = {}
        self.reset()

    def reset(self):
        now = clock.now()
        self._gateways = {
            "GATEWAY_A": GatewayHealthState(
                gateway_id="GATEWAY_A",
                status=RailHealthStatus.HEALTHY,
                success_probability=0.96,
                failure_rate=0.04,
                timeout_rate=0.01,
                latency_ms=180.0,
                last_updated=now
            ),
            "GATEWAY_B": GatewayHealthState(
                gateway_id="GATEWAY_B",
                status=RailHealthStatus.HEALTHY,
                success_probability=0.94,
                failure_rate=0.06,
                timeout_rate=0.01,
                latency_ms=210.0,
                last_updated=now
            ),
            "GATEWAY_C": GatewayHealthState(
                gateway_id="GATEWAY_C",
                status=RailHealthStatus.HEALTHY,
                success_probability=0.91,
                failure_rate=0.09,
                timeout_rate=0.02,
                latency_ms=320.0,
                last_updated=now
            ),
            "STRIPE": GatewayHealthState(
                gateway_id="STRIPE",
                status=RailHealthStatus.HEALTHY,
                success_probability=0.97,
                failure_rate=0.03,
                timeout_rate=0.005,
                latency_ms=150.0,
                last_updated=now
            ),
            "RAZORPAY": GatewayHealthState(
                gateway_id="RAZORPAY",
                status=RailHealthStatus.HEALTHY,
                success_probability=0.93,
                failure_rate=0.07,
                timeout_rate=0.015,
                latency_ms=230.0,
                last_updated=now
            ),
            "ADYEN": GatewayHealthState(
                gateway_id="ADYEN",
                status=RailHealthStatus.HEALTHY,
                success_probability=0.95,
                failure_rate=0.05,
                timeout_rate=0.01,
                latency_ms=190.0,
                last_updated=now
            )
        }

        self._rails = {
            "CARD": RailHealthState(
                rail=RailType.CARD,
                status=RailHealthStatus.HEALTHY,
                success_probability=0.95,
                failure_rate=0.05,
                timeout_rate=0.01,
                latency_ms=220.0,
                active_gateways=["GATEWAY_A", "GATEWAY_B", "STRIPE", "ADYEN"],
                last_updated=now
            ),
            "UPI": RailHealthState(
                rail=RailType.UPI,
                status=RailHealthStatus.HEALTHY,
                success_probability=0.92,
                failure_rate=0.08,
                timeout_rate=0.02,
                latency_ms=350.0,
                active_gateways=["RAZORPAY", "GATEWAY_B"],
                last_updated=now
            ),
            "BANK_TRANSFER": RailHealthState(
                rail=RailType.BANK_TRANSFER,
                status=RailHealthStatus.HEALTHY,
                success_probability=0.88,
                failure_rate=0.12,
                timeout_rate=0.03,
                latency_ms=800.0,
                active_gateways=["GATEWAY_C", "RAZORPAY"],
                last_updated=now
            ),
            "ACH": RailHealthState(
                rail=RailType.ACH,
                status=RailHealthStatus.HEALTHY,
                success_probability=0.90,
                failure_rate=0.10,
                timeout_rate=0.02,
                latency_ms=600.0,
                active_gateways=["STRIPE", "GATEWAY_A"],
                last_updated=now
            ),
            "NET_BANKING": RailHealthState(
                rail=RailType.NET_BANKING,
                status=RailHealthStatus.HEALTHY,
                success_probability=0.89,
                failure_rate=0.11,
                timeout_rate=0.02,
                latency_ms=500.0,
                active_gateways=["RAZORPAY", "GATEWAY_C"],
                last_updated=now
            )
        }

    def get_gateway_health(self, gateway_id: Optional[str] = None) -> GatewayHealthState:
        key = str(gateway_id or "GATEWAY_A").upper()
        if key in self._gateways:
            return self._gateways[key]
        # Default fallback
        return GatewayHealthState(gateway_id=key, status=RailHealthStatus.HEALTHY, success_probability=0.90, last_updated=clock.now())

    def get_rail_health(self, rail: str | RailType) -> RailHealthState:
        key = str(rail).upper()
        if hasattr(rail, "value"):
            key = rail.value.upper()
        if key in self._rails:
            return self._rails[key]
        return RailHealthState(rail=RailType.CARD, status=RailHealthStatus.HEALTHY, success_probability=0.90, last_updated=clock.now())

    def update_gateway_health(
        self,
        gateway_id: str,
        success_probability: float,
        latency_ms: float = 200.0,
        status: Optional[RailHealthStatus] = None
    ) -> GatewayHealthState:
        key = gateway_id.upper()
        current = self.get_gateway_health(key)
        old_prob = current.success_probability
        
        new_prob = max(0.0, min(1.0, success_probability))
        new_status = status
        if new_status is None:
            if new_prob < 0.30:
                new_status = RailHealthStatus.DOWN
            elif new_prob < 0.75:
                new_status = RailHealthStatus.DEGRADED
            else:
                new_status = RailHealthStatus.HEALTHY

        updated = GatewayHealthState(
            gateway_id=key,
            status=new_status,
            success_probability=new_prob,
            failure_rate=round(1.0 - new_prob, 4),
            timeout_rate=0.15 if new_status != RailHealthStatus.HEALTHY else 0.01,
            latency_ms=latency_ms,
            recovery_trend=round(new_prob - old_prob, 4),
            last_updated=clock.now()
        )
        self._gateways[key] = updated
        return updated

    def degrade_gateway(self, gateway_id: str, target_health: float = 0.20) -> GatewayHealthState:
        return self.update_gateway_health(
            gateway_id=gateway_id,
            success_probability=target_health,
            latency_ms=1200.0,
            status=RailHealthStatus.DEGRADED if target_health >= 0.1 else RailHealthStatus.DOWN
        )

    def restore_gateway(self, gateway_id: str, target_health: float = 0.95) -> GatewayHealthState:
        return self.update_gateway_health(
            gateway_id=gateway_id,
            success_probability=target_health,
            latency_ms=200.0,
            status=RailHealthStatus.HEALTHY
        )

    def get_healthy_gateways(self, rail: str = "CARD") -> List[str]:
        rail_state = self.get_rail_health(rail)
        healthy = []
        for gw in rail_state.active_gateways:
            gw_state = self.get_gateway_health(gw)
            if gw_state.status != RailHealthStatus.DOWN and gw_state.success_probability >= 0.50:
                healthy.append(gw)
        return healthy

    def get_best_gateway(self, rail: str = "CARD") -> Optional[str]:
        healthy = self.get_healthy_gateways(rail)
        if not healthy:
            return None
        return max(healthy, key=lambda g: self.get_gateway_health(g).success_probability)

    def get_all_gateway_states(self) -> Dict[str, Dict[str, Any]]:
        return {k: v.model_dump() for k, v in self._gateways.items()}

    def get_all_rail_states(self) -> Dict[str, Dict[str, Any]]:
        return {k: v.model_dump() for k, v in self._rails.items()}

rail_health_engine = RailHealthEngine()
