import json
from typing import Dict, Any, List, Optional
from simulator.clock import clock
from synthetic_payment_universe.world_v12.world.world import PersistentWorld
from synthetic_payment_universe.world_v12.observation.firewall import WorldObservationFirewall

class WorldAdapter:
    """
    Adapter connecting the ULTRON AgentLoop to the Persistent Synthetic World.
    Enforces strict temporal observation boundaries on all data exposed to the agent.
    """
    def __init__(self, world: PersistentWorld):
        self.world = world

    def get_current_time(self) -> int:
        return clock.now()

    def observe_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        now = clock.now()
        with self.world.repository.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT raw_json FROM customers WHERE customer_id = ? AND created_at <= ?", (customer_id, now))
            row = c.fetchone()
            if not row:
                return None
            raw_dict = json.loads(row[0])
            return WorldObservationFirewall.sanitize(raw_dict, now)

    def observe_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        now = clock.now()
        with self.world.repository.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT raw_json FROM payments WHERE payment_id = ? AND created_at <= ?", (payment_id, now))
            row = c.fetchone()
            if not row:
                return None
            raw_dict = json.loads(row[0])
            return WorldObservationFirewall.sanitize(raw_dict, now)

    def observe_gateway(self, gateway_id: str) -> Dict[str, Any]:
        now = clock.now()
        gw = self.world.gateway_world.gateways.get(gateway_id)
        if not gw:
            return {"gateway_id": gateway_id, "health_score": 0.90, "latency_ms": 150.0}
        return WorldObservationFirewall.sanitize(gw.model_dump(), now)

    def get_history(self, customer_id: str) -> List[Dict[str, Any]]:
        now = clock.now()
        history: List[Dict[str, Any]] = []
        with self.world.repository.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT raw_json FROM payments WHERE customer_id = ? AND created_at <= ? ORDER BY created_at ASC", (customer_id, now))
            for row in c:
                history.append(WorldObservationFirewall.sanitize(json.loads(row[0]), now))
        return history

    def execute_action(
        self,
        customer_id: str,
        payment_id: str,
        action_type: str,
        channel: Optional[str] = None
    ) -> Any:
        return self.world.execute_action(
            customer_id=customer_id,
            payment_id=payment_id,
            action_type=action_type,
            channel=channel
        )
