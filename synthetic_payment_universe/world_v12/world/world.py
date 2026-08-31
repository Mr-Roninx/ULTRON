import os
import shutil
from typing import Dict, Any, List, Optional
from simulator.clock import clock
from synthetic_payment_universe.world_v12.world.identity import WorldIdentity
from synthetic_payment_universe.world_v12.world.config import WorldConfig
from synthetic_payment_universe.world_v12.state.repository import SQLiteWorldRepository
from synthetic_payment_universe.world_v12.temporal.priority_queue import WorldEvent
from synthetic_payment_universe.world_v12.temporal.event_processor import TemporalEventProcessor
from synthetic_payment_universe.world_v12.temporal.replay import ReplayEngine
from synthetic_payment_universe.world_v12.entities.ledger import SimulatedDoubleEntryLedger
from synthetic_payment_universe.world_v12.gateways.gateway_world import DynamicGatewayWorld
from synthetic_payment_universe.world_v12.gateways.chaos_engine import WorldChaosEngine
from synthetic_payment_universe.world_v12.payments.processor import SimulatedPaymentProcessor
from synthetic_payment_universe.world_v12.payments.webhook_system import SimulatedWebhookSystem
from synthetic_payment_universe.world_v12.counterfactual.counterfactual_fork import WorldCounterfactualForkEngine
from backend.agent.action_registry import action_registry

class PersistentWorld:
    """
    Authoritative Large-Scale Persistent Synthetic Economic World Simulator (ULTRON-SWU-1.2).
    """
    def __init__(self, identity: WorldIdentity, config: WorldConfig, db_path: str):
        self.identity = identity
        self.config = config
        self.db_path = db_path
        self.repository = SQLiteWorldRepository(db_path)
        self.temporal_processor = TemporalEventProcessor(self.repository)
        self.replay_engine = ReplayEngine(self.repository)
        self.ledger = SimulatedDoubleEntryLedger()
        self.gateway_world = DynamicGatewayWorld(subseed=identity.master_seed)
        self.chaos_engine = WorldChaosEngine(self.gateway_world)
        self.payment_processor = SimulatedPaymentProcessor(self.ledger)
        self.webhook_system = SimulatedWebhookSystem(subseed=identity.master_seed)
        self.counterfactual_engine = WorldCounterfactualForkEngine(master_seed=identity.master_seed)

        # Save initial world metadata
        self.identity.compute_configuration_hash(self.config.model_dump())
        self.repository.save_world_metadata(self.identity, self.config.model_dump())

    def advance_to(self, target_timestamp: int) -> List[WorldEvent]:
        """Advances simulation clock monotonically, applying chaos and processing intermediate events."""
        clock.reset(target_timestamp)
        self.identity.current_time = target_timestamp
        self.repository.update_simulation_time(self.identity.world_id, target_timestamp)

        # 1. Evolve dynamic gateway states
        self.gateway_world.evolve_gateway_states(target_timestamp)

        # 2. Apply scheduled environmental chaos
        self.chaos_engine.apply_pending_chaos(target_timestamp)

        # 3. Process chronological event queue
        processed = self.temporal_processor.process_until(target_timestamp)
        return processed

    def schedule_event(self, event: WorldEvent):
        self.temporal_processor.schedule_event(event)

    def execute_action(
        self,
        customer_id: str,
        payment_id: str,
        action_type: str,
        channel: Optional[str] = None,
        target_gateway: Optional[str] = None
    ) -> Tuple_Action_Result:
        # Validate against authoritative ActionRegistry
        valid_actions = {"WAIT", "RETRY", "RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "SEND_PAYMENT_LINK", "SWITCH_GATEWAY", "SWITCH_RAIL", "ESCALATE", "RECONCILE", "STOP"}
        is_valid = action_type in valid_actions
        if not is_valid:
            reg_valid, _ = action_registry.validate_action(action_type)
            is_valid = reg_valid

        if not is_valid:
            return False, {"status": "REJECTED_BY_GUARD", "reason": f"Action '{action_type}' not permitted by registry"}

        now = clock.now()
        # Schedule future event based on action
        if action_type in ["RETRY", "RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "SWITCH_GATEWAY"]:
            evt = WorldEvent(
                event_id=f"evt_act_{payment_id}_{now}",
                event_type="PAYMENT_ATTEMPT_SCHEDULED",
                entity_id=payment_id,
                timestamp=now + 60,
                causal_parent_id=f"act_{action_type}",
                payload={"action": action_type, "target_gateway": target_gateway or "GATEWAY_B"}
            )
            self.schedule_event(evt)
        elif action_type == "SEND_PAYMENT_LINK":
            evt = WorldEvent(
                event_id=f"evt_link_{payment_id}_{now}",
                event_type="PAYMENT_LINK_DISPATCHED",
                entity_id=customer_id,
                timestamp=now + 300,
                causal_parent_id=f"act_{action_type}",
                payload={"channel": channel or "WHATSAPP"}
            )
            self.schedule_event(evt)

        return True, {"status": "EXECUTED", "action_type": action_type, "timestamp": now}

    def snapshot(self) -> str:
        snapshot_path = f"{self.db_path}.snapshot_{self.identity.current_time}"
        import sqlite3
        with self.repository.get_connection() as conn:
            dest = sqlite3.connect(snapshot_path)
            conn.backup(dest)
            dest.close()
        return snapshot_path

    def replay_to(self, target_timestamp: int) -> List[Dict[str, Any]]:
        return self.replay_engine.replay_to(target_timestamp)

Tuple_Action_Result = Any
