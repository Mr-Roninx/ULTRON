import os
import sqlite3
import random
from typing import Dict, Any, List, Optional, Tuple
from synthetic_payment_universe.world_v14.config import WorldConfigV14, WorldProfileV14
from synthetic_payment_universe.world_v14.clock import emergent_clock
from synthetic_payment_universe.world_v14.repository import SQLiteEmergentRepository
from synthetic_payment_universe.world_v14.events.micro_events import MicroEconomicEvent
from synthetic_payment_universe.world_v14.events.persistent_queue import PopulationEventQueue
from synthetic_payment_universe.world_v14.events.replay_engine import PopulationReplayEngine
from synthetic_payment_universe.world_v14.population.customer_cohorts import PopulationCustomerEntity, CustomerCohort, CustomerLifecycleState
from synthetic_payment_universe.world_v14.population.merchant_cohorts import PopulationMerchantEntity, MerchantCohort, MerchantLifecycleState
from synthetic_payment_universe.world_v14.population.lifecycle import PopulationLifecycleEngine
from synthetic_payment_universe.world_v14.economy.macro_shocks import MacroShockEngine, MacroEconomicShock
from synthetic_payment_universe.world_v14.economy.emergent_demand import EmergentPaymentDemandEngine
from synthetic_payment_universe.world_v14.economy.feedback_loops import EconomicFeedbackLoops
from synthetic_payment_universe.world_v14.gateways.competitive_gateways import CompetitiveGatewayEngine
from synthetic_payment_universe.world_v14.ledger.double_entry_ledger import PopulationDoubleEntryLedger
from synthetic_payment_universe.world_v14.ledger.provenance_tracker import provenance_tracker, ProvenanceChain
from synthetic_payment_universe.world_v14.causal.structural_dag import PopulationCausalDAG
from synthetic_payment_universe.world_v14.counterfactual.civilization_fork import CivilizationForkEngine
from synthetic_payment_universe.world_v14.observation.observation_builder import PopulationObservationBuilder
from synthetic_payment_universe.world_v14.scaling.streaming_generator import StreamingPopulationGenerator
from backend.agent.action_registry import action_registry

class EmergentEconomicWorld:
    """
    Master World Simulator for ULTRON-SWU-1.4 (Emergent Population Economy).
    Multi-cohort population, dynamic feedback loops A-F, macro shocks, double-entry accounting.
    """
    def __init__(self, world_id: str, master_seed: int, config: WorldConfigV14, db_path: str):
        self.world_id = world_id
        self.master_seed = master_seed
        self.config = config
        self.db_path = db_path

        self.repository = SQLiteEmergentRepository(db_path)
        self.event_queue = PopulationEventQueue()
        self.replay_engine = PopulationReplayEngine(self.repository)
        self.gateway_engine = CompetitiveGatewayEngine()
        self.ledger = PopulationDoubleEntryLedger()
        self.macro_shocks = MacroShockEngine()
        self.causal_dag = PopulationCausalDAG()
        self.fork_engine = CivilizationForkEngine(master_seed=master_seed)
        self.observation_builder = PopulationObservationBuilder(self.repository)
        self.streaming_generator = StreamingPopulationGenerator(self.repository)

        # Working in-memory entities
        self.customers: Dict[str, PopulationCustomerEntity] = {}
        self.merchants: Dict[str, PopulationMerchantEntity] = {}
        self.relationships: Dict[str, Dict[str, Any]] = {} # (cust_id, merch_id) -> rel

    def schedule_event(self, event: MicroEconomicEvent):
        self.event_queue.push(event)

    def advance_to(self, target_timestamp: int) -> List[MicroEconomicEvent]:
        """
        Advances simulation clock monotonically, evolving gateway traffic, macro shocks, and processing events.
        """
        emergent_clock.advance_to(target_timestamp)
        processed: List[MicroEconomicEvent] = []

        # 1. Decay gateway traffic
        self.gateway_engine.decay_traffic()

        # 2. Check active macro shocks
        shocks = self.macro_shocks.get_active_shocks(target_timestamp)
        for s in shocks:
            if not s.applied and s.shock_type == "GATEWAY_DISRUPTION" and s.target_entity in self.gateway_engine.gateways:
                gw = self.gateway_engine.gateways[s.target_entity]
                gw.current_authorization_rate = s.magnitude
                gw.latency_ms = s.payload.get("latency_ms", 3000.0)
                s.applied = True

        # 3. Process events up to target time
        while self.event_queue.has_events_up_to(target_timestamp):
            evt = self.event_queue.pop()
            if not evt:
                break
            processed.append(evt)

        if processed:
            self.repository.insert_economic_events(processed)

        return processed

    def advance_days(self, days: int) -> List[MicroEconomicEvent]:
        target = emergent_clock.now() + (days * 86400)
        return self.advance_to(target)

    def execute_agent_action(
        self,
        customer_id: str,
        payment_id: str,
        action_type: str,
        channel: Optional[str] = None,
        target_gateway: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        # Validate against authoritative ActionRegistry
        valid_actions = {"WAIT", "RETRY", "RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "SEND_PAYMENT_LINK", "SWITCH_GATEWAY", "SWITCH_RAIL", "ESCALATE", "RECONCILE", "STOP"}
        is_valid = action_type in valid_actions
        if not is_valid:
            reg_valid, _ = action_registry.validate_action(action_type)
            is_valid = reg_valid

        if not is_valid:
            return False, {"status": "REJECTED_BY_GUARD", "reason": f"Action '{action_type}' not permitted"}

        now = emergent_clock.now()

        # Routing action updates gateway traffic (Loop B)
        if action_type in ["SWITCH_GATEWAY", "RETRY_GATEWAY_B"]:
            gw_id = target_gateway or "GATEWAY_B"
            self.gateway_engine.route_transaction(gw_id)

        # Outreach updates fatigue (Loop C)
        cust = self.customers.get(customer_id)
        if cust and action_type in ["SEND_PAYMENT_LINK", "SEND_MESSAGE", "EMAIL", "SMS"]:
            delta = 0.12 if channel == "WHATSAPP" else 0.08
            cust.fatigue_score = EconomicFeedbackLoops.apply_loop_c_fatigue(cust.fatigue_score, delta)

        evt = MicroEconomicEvent(
            event_id=f"evt_act_{payment_id}_{now}",
            event_type=f"AGENT_INTERVENTION_{action_type}",
            entity_id=payment_id,
            timestamp=now + 60,
            causal_parent_id=f"act_{action_type}",
            payload={"action": action_type, "customer_id": customer_id}
        )
        self.schedule_event(evt)

        return True, {"status": "EXECUTED", "action_type": action_type, "timestamp": now}

    def record_recovery(
        self,
        payment_id: str,
        customer_id: str,
        merchant_id: str,
        amount: float,
        action_type: str,
        diagnosis: str = "TRANSIENT_FAILURE"
    ):
        now = emergent_clock.now()
        # 1. Double-entry ledger
        entry = self.ledger.record_transaction(
            transaction_id=payment_id,
            source_event_id=f"evt_rec_{payment_id}",
            account_debit="BANK_CASH_GATEWAY_A",
            account_credit="MERCHANT_SETTLEMENT_CLEARING",
            amount=amount,
            timestamp=now,
            provenance={"action_type": action_type, "diagnosis": diagnosis}
        )

        # 2. Relationship update (Loop A)
        cust = self.customers.get(customer_id)
        if cust:
            cust.relationship_score = EconomicFeedbackLoops.apply_loop_a_relationship(cust.relationship_score, True)

        # 3. Provenance record
        provenance_tracker.record(ProvenanceChain(
            payment_id=payment_id,
            failure_code="91",
            observed_timestamp=now - 3600,
            diagnosis=diagnosis,
            action_type=action_type,
            execution_timestamp=now - 3500,
            settlement_timestamp=now,
            recovered_amount=amount,
            ledger_entry_id=entry.entry_id
        ))

    def snapshot(self) -> str:
        snap_path = f"{self.db_path}.snapshot_{emergent_clock.now()}"
        src = sqlite3.connect(self.db_path)
        dst = sqlite3.connect(snap_path)
        src.backup(dst)
        dst.close()
        src.close()
        return snap_path
