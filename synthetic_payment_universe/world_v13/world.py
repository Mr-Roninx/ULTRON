import os
import json
import random
from typing import Dict, Any, List, Optional, Tuple
from synthetic_payment_universe.world_v13.config import WorldConfig, WorldProfile
from synthetic_payment_universe.world_v13.clock import economic_clock
from synthetic_payment_universe.world_v13.repository import SQLiteCivilizationRepository
from synthetic_payment_universe.world_v13.events.event import EconomicEvent
from synthetic_payment_universe.world_v13.events.processor import CivilizationEventProcessor
from synthetic_payment_universe.world_v13.events.replay import CivilizationReplayEngine
from synthetic_payment_universe.world_v13.economy.customer_economy import CustomerEconomyEngine, CustomerEconomyEntity
from synthetic_payment_universe.world_v13.economy.merchant_economy import MerchantEconomyEngine, MerchantEconomyEntity
from synthetic_payment_universe.world_v13.economy.payment_economy import PaymentEconomyEngine, PaymentCivilizationEntity
from synthetic_payment_universe.world_v13.economy.gateway_economy import GatewayEconomyEngine
from synthetic_payment_universe.world_v13.economy.subscription_economy import SubscriptionEconomyEngine, SubscriptionCivilizationEntity
from synthetic_payment_universe.world_v13.economy.invoice_economy import InvoiceEconomyEngine, InvoiceCivilizationEntity
from synthetic_payment_universe.world_v13.ledger.ledger import CivilizationDoubleEntryLedger
from synthetic_payment_universe.world_v13.causal.graph import CivilizationCausalGraph
from synthetic_payment_universe.world_v13.causal.lineage import causal_lineage_engine, RecoveryProvenance
from synthetic_payment_universe.world_v13.counterfactual.fork import CivilizationCounterfactualForkEngine
from synthetic_payment_universe.world_v13.chaos.engine import CivilizationChaosEngine
from synthetic_payment_universe.world_v13.observation.api import WorldObservationAPI
from synthetic_payment_universe.world_v13.snapshots.snapshot import CivilizationSnapshotEngine
from synthetic_payment_universe.world_v13.snapshots.restore import CivilizationRestoreEngine
from synthetic_payment_universe.world_v13.scheduler.capacity_guard import AgentCapacityGuard
from synthetic_payment_universe.world_v13.scheduler.opportunity_scheduler import OpportunityScheduler
from backend.agent.action_registry import action_registry

class PersistentEconomicWorld:
    """
    Authoritative Persistent Economic Civilization Simulator (ULTRON-SWU-1.3).
    Continuous multi-day/multi-month simulation, dynamic feedback loops, and double-entry accounting.
    """
    def __init__(self, world_id: str, master_seed: int, config: WorldConfig, db_path: str):
        self.world_id = world_id
        self.master_seed = master_seed
        self.config = config
        self.db_path = db_path

        self.repository = SQLiteCivilizationRepository(db_path)
        self.event_processor = CivilizationEventProcessor(self.repository)
        self.replay_engine = CivilizationReplayEngine(self.repository)
        self.gateway_economy = GatewayEconomyEngine(subseed=master_seed)
        self.ledger = CivilizationDoubleEntryLedger()
        self.causal_graph = CivilizationCausalGraph()
        self.counterfactual_engine = CivilizationCounterfactualForkEngine(master_seed=master_seed)
        self.chaos_engine = CivilizationChaosEngine(self.gateway_economy)
        self.observation_api = WorldObservationAPI(self.repository, self.gateway_economy)
        self.capacity_guard = AgentCapacityGuard()
        self.opportunity_scheduler = OpportunityScheduler(self.capacity_guard)

        # In-memory working entities
        self.customers: Dict[str, CustomerEconomyEntity] = {}
        self.merchants: Dict[str, MerchantEconomyEntity] = {}
        self.payments: Dict[str, PaymentCivilizationEntity] = {}
        self.subscriptions: Dict[str, SubscriptionCivilizationEntity] = {}
        self.invoices: Dict[str, InvoiceCivilizationEntity] = {}

    def schedule_event(self, event: EconomicEvent):
        self.event_processor.schedule_event(event)

    def advance_to(self, target_timestamp: int) -> List[EconomicEvent]:
        """
        Advances simulation clock to target timestamp, triggering organic economy, chaos, and scheduled events.
        """
        economic_clock.advance_to(target_timestamp)

        # 1. Apply scheduled chaos
        self.chaos_engine.apply_pending_chaos(target_timestamp)

        # 2. Decay gateway load & customer fatigue
        self.gateway_economy.decay_load()
        days_passed = max(0.01, (target_timestamp - economic_clock.start_time()) / 86400.0)
        for cust in self.customers.values():
            CustomerEconomyEngine.decay_fatigue(cust, days_passed)

        # 3. Process events queue up to target time
        processed = self.event_processor.process_until(target_timestamp)
        return processed

    def advance_days(self, days: int) -> List[EconomicEvent]:
        target = economic_clock.now() + (days * 86400)
        return self.advance_to(target)

    def execute_agent_action(
        self,
        customer_id: str,
        payment_id: str,
        action_type: str,
        channel: Optional[str] = None,
        target_gateway: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        # Fail-closed validation against authoritative ActionRegistry
        valid_actions = {"WAIT", "RETRY", "RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "SEND_PAYMENT_LINK", "SWITCH_GATEWAY", "SWITCH_RAIL", "ESCALATE", "RECONCILE", "STOP"}
        is_valid = action_type in valid_actions
        if not is_valid:
            reg_valid, _ = action_registry.validate_action(action_type)
            is_valid = reg_valid

        if not is_valid:
            return False, {"status": "REJECTED_BY_GUARD", "reason": f"Action '{action_type}' not permitted"}

        now = economic_clock.now()

        # Check capacity guard
        if not self.capacity_guard.can_execute_action(customer_id, now):
            return False, {"status": "REJECTED_CAPACITY", "reason": "Max actions per customer per day exceeded"}

        self.capacity_guard.record_action(customer_id, now)

        # Apply action dynamics
        cust = self.customers.get(customer_id)
        if cust and action_type in ["SEND_PAYMENT_LINK", "SEND_MESSAGE", "EMAIL", "SMS"]:
            CustomerEconomyEngine.apply_contact(cust, channel or "WHATSAPP", now)

        if action_type in ["SWITCH_GATEWAY", "RETRY_GATEWAY_B"]:
            self.gateway_economy.route_traffic(target_gateway or "GATEWAY_B")

        # Schedule future event
        evt = EconomicEvent(
            event_id=f"evt_act_{payment_id}_{now}",
            event_type=f"AGENT_ACTION_{action_type}",
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
        now = economic_clock.now()
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

        # 2. Customer & Merchant economics
        cust = self.customers.get(customer_id)
        if cust:
            CustomerEconomyEngine.record_successful_recovery(cust, amount, now)

        merch = self.merchants.get(merchant_id)
        if merch:
            MerchantEconomyEngine.record_payment_success(merch, amount)

        # 3. Provenance recording
        causal_lineage_engine.record_provenance(RecoveryProvenance(
            payment_id=payment_id,
            failure_timestamp=now - 3600,
            failure_code="91",
            observed_by_agent_timestamp=now - 3500,
            diagnosis=diagnosis,
            selected_action=action_type,
            action_execution_timestamp=now - 3000,
            recovery_timestamp=now,
            recovered_amount=amount,
            settlement_batch_id=f"stl_{payment_id}",
            ledger_entry_id=entry.entry_id,
            customer_relationship_delta=0.05
        ))

    def snapshot(self) -> str:
        snap_path = f"{self.db_path}.snapshot_{economic_clock.now()}"
        return CivilizationSnapshotEngine.snapshot(self.db_path, snap_path)

    def restore(self, snapshot_path: str):
        CivilizationRestoreEngine.restore(snapshot_path, self.db_path)
