import os
import sqlite3
import random
from typing import Dict, Any, List, Optional, Tuple
from synthetic_payment_universe.world_v15.configuration import WorldConfigV15, WorldProfileV15
from synthetic_payment_universe.world_v15.clock import adversarial_clock
from synthetic_payment_universe.world_v15.repository import SQLiteAdversarialRepository
from synthetic_payment_universe.world_v15.behavior.customer_heterogeneity import HeterogeneousCustomerEntity, CustomerSensitivityType
from synthetic_payment_universe.world_v15.behavior.intervention_effects import InterventionEffectsEngine
from synthetic_payment_universe.world_v15.behavior.customer_fatigue import CustomerFatigueModel, LongHorizonFatigueState
from synthetic_payment_universe.world_v15.behavior.ltv_dynamics import CustomerLTVDynamics
from synthetic_payment_universe.world_v15.externalities.gateway_externalities import GatewayExternalityEngine
from synthetic_payment_universe.world_v15.externalities.merchant_externalities import MerchantExternalityEngine
from synthetic_payment_universe.world_v15.natural_recovery.natural_recovery_engine import NaturalRecoveryEngine
from synthetic_payment_universe.world_v15.attribution.attribution_tiers import MultiTierAttributionEngine, MultiTierEconomicAttribution
from synthetic_payment_universe.world_v15.attribution.accounting_reconciliation import AccountingReconciliationEngine
from synthetic_payment_universe.world_v15.attribution.truth_reconciliation import TruthReconciliationEngine
from synthetic_payment_universe.world_v15.counterfactual.shadow_evaluator import ShadowEvaluator
from synthetic_payment_universe.world_v15.observation.blind_firewall import BlindObservationFirewall
from synthetic_payment_universe.world_v15.ledger.adversarial_ledger import AdversarialDoubleEntryLedger
from backend.agent.action_registry import action_registry

class AdversarialEconomicWorld:
    """
    Master World Simulator for ULTRON-SWU-1.5 (Economic Adversarial Reality).
    Exposes ULTRON to negative intervention effects, natural recovery competition, gateway externalities, and 11 competing policies.
    """
    def __init__(self, world_id: str, master_seed: int, config: WorldConfigV15, db_path: str):
        self.world_id = world_id
        self.master_seed = master_seed
        self.config = config
        self.db_path = db_path

        self.repository = SQLiteAdversarialRepository(db_path)
        self.ledger = AdversarialDoubleEntryLedger()
        self.gateway_externalities = GatewayExternalityEngine()
        self.shadow_evaluator = ShadowEvaluator(master_seed=master_seed)

        self.customers: Dict[str, HeterogeneousCustomerEntity] = {}
        self.customer_fatigue_states: Dict[str, LongHorizonFatigueState] = {}
        self.payments: Dict[str, Dict[str, Any]] = {}

    def advance_days(self, days: int) -> int:
        now = adversarial_clock.now()
        target = now + (days * 86400)
        adversarial_clock.advance_to(target)

        # Decay customer fatigue across population
        for c in self.customers.values():
            state = self.customer_fatigue_states.get(c.customer_id)
            if state:
                CustomerFatigueModel.decay_fatigue(state, days)
                c.fatigue_rolling_24h = state.rolling_24h
                c.fatigue_rolling_7d = state.rolling_7d

        # Reset daily gateway loads
        self.gateway_externalities.reset_load()

        return days

    def execute_agent_action(
        self,
        customer_id: str,
        payment_id: str,
        action_type: str,
        channel: str = "EMAIL",
        target_gateway: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        # Fail-closed ActionRegistry authority
        valid_actions = {
            "WAIT", "RETRY", "SEND_PAYMENT_LINK", "SWITCH_GATEWAY", "SWITCH_RAIL",
            "ESCALATE", "AGGRESSIVE_DUNNING", "ALWAYS_RETRY", "ALWAYS_CONTACT"
        }
        is_valid = action_type in valid_actions
        if not is_valid:
            reg_valid, _ = action_registry.validate_action(action_type)
            is_valid = reg_valid

        if not is_valid:
            return False, {"status": "REJECTED_BY_GUARD", "reason": f"Action '{action_type}' not permitted"}

        now = adversarial_clock.now()
        cust = self.customers.get(customer_id)
        pmt = self.payments.get(payment_id, {})
        is_natural = pmt.get("would_recover_naturally", False)

        fatigue_state = self.customer_fatigue_states.setdefault(customer_id, LongHorizonFatigueState())

        # 1. Negative intervention consequences
        neg_effect = InterventionEffectsEngine.evaluate_outreach_effect(
            action_type=action_type,
            channel=channel,
            current_fatigue=fatigue_state.rolling_24h,
            is_natural_recovery=is_natural
        )

        CustomerFatigueModel.apply_contact(fatigue_state, neg_effect.fatigue_delta, now)
        if cust:
            cust.fatigue_rolling_24h = fatigue_state.rolling_24h
            cust.fatigue_rolling_7d = fatigue_state.rolling_7d
            cust.relationship_score = max(0.05, min(1.0, round(cust.relationship_score + neg_effect.relationship_delta, 3)))
            if neg_effect.churn_triggered:
                cust.churn_status = "CHURNED"

        # 2. Gateway externalities if switching
        ext_cost = 0.0
        if action_type in ["SWITCH_GATEWAY", "ALWAYS_SWITCH_GATEWAY"]:
            gw_id = target_gateway or "GATEWAY_B"
            ext_cost = self.gateway_externalities.add_traffic(gw_id, count=1)

        # 3. Merchant burden
        merch_cost = MerchantExternalityEngine.calculate_merchant_burden(action_type, count=1)
        total_externality = ext_cost + neg_effect.externality_cost + merch_cost

        return True, {
            "status": "EXECUTED",
            "action_type": action_type,
            "timestamp": now,
            "fatigue_delta": neg_effect.fatigue_delta,
            "relationship_delta": neg_effect.relationship_delta,
            "externality_cost": total_externality,
            "churn_triggered": neg_effect.churn_triggered
        }

    def record_settled_recovery(
        self,
        payment_id: str,
        customer_id: str,
        amount: float,
        action_type: str,
        channel: str = "EMAIL"
    ) -> MultiTierEconomicAttribution:
        now = adversarial_clock.now()
        pmt = self.payments.get(payment_id, {})
        is_natural = pmt.get("would_recover_naturally", False)
        cust = self.customers.get(customer_id)

        # 1. Forward LTV delta calculation
        ltv_before = CustomerLTVDynamics.project_future_revenue(cust, 90) if cust else 0.0
        # Post-action relationship
        ltv_after = CustomerLTVDynamics.project_future_revenue(cust, 90) if cust else 0.0
        ltv_delta = max(0.0, round(ltv_after - ltv_before, 2))

        # 2. Multi-tier classification
        op_cost = 18.0 if action_type != "AGGRESSIVE_DUNNING" else 65.0
        attr = MultiTierAttributionEngine.classify_attribution(
            recovered_amount=amount,
            is_natural_recovery=is_natural,
            forward_ltv_delta=ltv_delta,
            externality_cost=0.0,
            operational_cost=op_cost
        )

        # 3. Double-entry ledger recording
        self.ledger.record_transaction(
            transaction_id=payment_id,
            account_debit="BANK_CASH_GATEWAY_A",
            account_credit="MERCHANT_SETTLEMENT_CLEARING",
            amount=amount,
            timestamp=now,
            attribution_tier=EconomicAttributionTier.DIRECT_INCREMENTAL_REVENUE if attr.direct_incremental_revenue > 0 else EconomicAttributionTier.NON_INCREMENTAL_RECOVERY,
            provenance={"action_type": action_type, "is_natural": is_natural}
        )

        # Update payment status
        if payment_id in self.payments:
            self.payments[payment_id]["status"] = "SETTLED"

        return attr

    def snapshot(self) -> str:
        snap_path = f"{self.db_path}.snapshot_{adversarial_clock.now()}"
        src = sqlite3.connect(self.db_path)
        dst = sqlite3.connect(snap_path)
        src.backup(dst)
        dst.close()
        src.close()
        return snap_path
