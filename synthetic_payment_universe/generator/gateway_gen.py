import random
from typing import Dict, List, Tuple
from synthetic_payment_universe.schema.entities import Gateway, Rail, GatewayEvent
from synthetic_payment_universe.generator.seeds import MasterSeedManager

GATEWAY_IDS = ["GATEWAY_A", "GATEWAY_B", "GATEWAY_C", "GATEWAY_D"]
RAIL_IDS = ["CARD", "UPI", "ACH", "E_NACH", "BANK_TRANSFER"]

class GatewayRailGenerator:
    """
    Simulates dynamic gateway health fluctuations, rail latency distributions,
    and event-driven health state transitions.
    """
    def __init__(self, seed_manager: MasterSeedManager):
        self.seed_mgr = seed_manager
        self.gateways: Dict[str, Gateway] = {}
        self.rails: Dict[str, Rail] = {}
        self._initialize_default_state()

    def _initialize_default_state(self):
        for gid in GATEWAY_IDS:
            self.gateways[gid] = Gateway(
                gateway_id=gid,
                name=f"Payment Processor {gid}",
                current_health=0.96 if gid in ["GATEWAY_A", "GATEWAY_B"] else 0.88,
                latency_ms=120.0,
                status="STABLE"
            )
        for rid in RAIL_IDS:
            self.rails[rid] = Rail(
                rail_id=rid,
                name=f"Payment Rail {rid}",
                current_health=0.95,
                base_latency_ms=100.0 if rid == "UPI" else 250.0
            )

    def evolve_gateway_health(self, timestamp: int, step_index: int) -> List[GatewayEvent]:
        """
        Evolves gateway health dynamically over simulation time based on deterministic subseed.
        """
        subseed = self.seed_mgr.get_gateway_seed(step_index)
        rng = random.Random(subseed)
        events: List[GatewayEvent] = []

        for gid, gw in self.gateways.items():
            prev_health = gw.current_health
            # Stochastic perturbation
            roll = rng.random()
            if roll < 0.05: # Outage event
                new_health = rng.uniform(0.05, 0.20)
                status = "OUTAGE"
            elif roll < 0.15: # Degradation event
                new_health = rng.uniform(0.30, 0.60)
                status = "DEGRADING"
            elif roll < 0.35 and prev_health < 0.80: # Recovery
                new_health = min(0.98, prev_health + rng.uniform(0.20, 0.40))
                status = "RECOVERING"
            else: # Normal fluctuation
                new_health = max(0.85, min(0.99, prev_health + rng.uniform(-0.02, 0.02)))
                status = "STABLE"

            gw.current_health = round(new_health, 3)
            gw.status = status
            gw.latency_ms = round(100.0 + (1.0 - new_health) * 4000.0, 1)

            if abs(new_health - prev_health) > 0.05:
                events.append(GatewayEvent(
                    event_id=f"gwevt_{gid}_{timestamp}",
                    gateway_id=gid,
                    previous_health=prev_health,
                    new_health=gw.current_health,
                    event_type=f"HEALTH_{status}",
                    timestamp=timestamp
                ))

        return events
