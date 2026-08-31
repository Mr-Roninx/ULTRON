from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from simulator.models import PaymentStatus, InvoiceStatus, CheckoutStatus, RecoveryAction, Communication
from simulator.world import FinancialWorld
from simulator.clock import clock
from backend.benchmark.models import BenchmarkOpportunity, ResourceConstraints, StrategyMetrics
from backend.benchmark.simulator_dynamics import SimulationDynamicsEngine
from backend.economics.relationship import RelationshipState

class BenchmarkStrategy(ABC):
    def __init__(self, name: str, constraints: Optional[ResourceConstraints] = None):
        self.name = name
        self.constraints = constraints or ResourceConstraints()
        self.actions_attempted = 0
        self.actions_successful = 0
        self.actions_blocked = 0
        self.customer_contacts = 0
        self.escalations = 0
        self.intervention_cost = 0.0
        self.relationship_cost = 0.0
        self.risk_cost = 0.0
        self.opportunity_actions: Dict[str, str] = {}

    @abstractmethod
    def run(self, world: FinancialWorld, opportunities: List[BenchmarkOpportunity], dynamics: SimulationDynamicsEngine, horizon_days: int) -> None:
        pass

class NoActionBaseline(BenchmarkStrategy):
    """
    NO ACTION BASELINE:
    Performs zero recovery interventions.
    Measures natural baseline recovery.
    """
    def __init__(self, constraints: Optional[ResourceConstraints] = None):
        super().__init__("NoAction", constraints)

    def run(self, world: FinancialWorld, opportunities: List[BenchmarkOpportunity], dynamics: SimulationDynamicsEngine, horizon_days: int) -> None:
        for opp in opportunities:
            self.opportunity_actions[opp.opportunity_id] = "NONE"
        # No interventions taken.

class FixedRetryBaseline(BenchmarkStrategy):
    """
    FIXED RETRY BASELINE:
    Conventional schedule: T+4h, T+24h, T+48h for failed payments.
    Respects FSM, policy, authority, idempotency, unknown-state protection.
    """
    def __init__(self, constraints: Optional[ResourceConstraints] = None):
        super().__init__("FixedRetry", constraints)

    def run(self, world: FinancialWorld, opportunities: List[BenchmarkOpportunity], dynamics: SimulationDynamicsEngine, horizon_days: int) -> None:
        delays = [3600 * 4, 86400, 86400 * 2]  # T+4h, T+24h, T+48h
        
        for opp in opportunities:
            if opp.entity_type == "PAYMENT":
                payment = world.payments.get(opp.entity_id)
                if not payment:
                    continue
                
                # Unknown payments cannot be retried without reconciliation (safety check)
                if payment.status == PaymentStatus.UNKNOWN:
                    self.actions_blocked += 1
                    self.opportunity_actions[opp.opportunity_id] = "BLOCKED_UNKNOWN"
                    continue
                
                if payment.status == PaymentStatus.FAILED:
                    self.opportunity_actions[opp.opportunity_id] = "RETRY"
                    for delay in delays:
                        if delay > horizon_days * 86400:
                            continue
                        self.actions_attempted += 1
                        self.intervention_cost += 1.0  # Retry cost
                        dynamics.process_retry_attempt(world, payment.id, delay)
                        self.actions_successful += 1
            else:
                self.opportunity_actions[opp.opportunity_id] = "NONE"

class TraditionalDunningBaseline(BenchmarkStrategy):
    """
    TRADITIONAL DUNNING BASELINE:
    Conventional dunning schedule:
    Day 1 (T+24h) Email -> Day 3 (T+72h) Reminder -> Day 7 (T+168h) Escalation.
    Respects communication frequency policies and opt-out.
    """
    def __init__(self, constraints: Optional[ResourceConstraints] = None):
        super().__init__("TraditionalDunning", constraints)

    def run(self, world: FinancialWorld, opportunities: List[BenchmarkOpportunity], dynamics: SimulationDynamicsEngine, horizon_days: int) -> None:
        for opp in opportunities:
            cust = world.customers.get(opp.customer_id)
            if not cust or cust.opt_out:
                self.actions_blocked += 1
                self.opportunity_actions[opp.opportunity_id] = "OPT_OUT"
                continue

            self.opportunity_actions[opp.opportunity_id] = "DUNNING_SEQUENCE"
            
            # Step 1: Day 1 Email (T+24h)
            if horizon_days >= 1 and cust.recent_contacts < self.constraints.max_contacts_per_customer:
                self.actions_attempted += 1
                self.customer_contacts += 1
                self.intervention_cost += 1.0  # Email cost
                dynamics.process_payment_link_or_message(world, cust.id, opp, "EMAIL")
                self.actions_successful += 1

            # Step 2: Day 3 Reminder (T+72h)
            if horizon_days >= 3 and cust.recent_contacts < self.constraints.max_contacts_per_customer:
                self.actions_attempted += 1
                self.customer_contacts += 1
                self.intervention_cost += 1.0  # SMS cost
                dynamics.process_payment_link_or_message(world, cust.id, opp, "SMS")
                self.actions_successful += 1

            # Step 3: Day 7 Escalation (T+168h)
            if horizon_days >= 7 and cust.recent_contacts < self.constraints.max_contacts_per_customer:
                self.actions_attempted += 1
                self.escalations += 1
                self.intervention_cost += 50.0  # Escalation cost
                dynamics.process_escalation(world, cust.id, opp)
                self.actions_successful += 1

            # Compute relationship cost impact
            rel_state = RelationshipState(
                customer_id=cust.id,
                recent_contacts=cust.recent_contacts,
                recent_responses=cust.recent_responses,
                successful_prior_recoveries=cust.successful_prior_recoveries,
                customer_value=cust.ltv,
                complaints=cust.complaints,
                opt_out=False,
                silence_duration=cust.silence_duration
            )
            self.relationship_cost += rel_state.relationship_cost_proxy()

class RuleBasedRecoveryBaseline(BenchmarkStrategy):
    """
    RULE-BASED RECOVERY BASELINE:
    Credible deterministic business rules without ML/LLM/interference reasoning:
    - Transient failures -> retry with backoff (T+1h, T+4h)
    - Liquidity / Insufficient funds -> Payment link / reminder (T+24h)
    - Credential / Expired -> Payment method update link
    - 3DS / OTP failure -> SMS / WhatsApp payment link
    - Overdue invoice -> Reminder message
    - Checkout abandonment -> Link at T+30m
    - UNKNOWN payment -> Reconcile first
    - Dispute / High LTV Enterprise -> Escalate to human
    """
    def __init__(self, constraints: Optional[ResourceConstraints] = None):
        super().__init__("RuleBasedRecovery", constraints)

    def run(self, world: FinancialWorld, opportunities: List[BenchmarkOpportunity], dynamics: SimulationDynamicsEngine, horizon_days: int) -> None:
        for opp in opportunities:
            cust = world.customers.get(opp.customer_id)
            if not cust:
                continue

            if cust.opt_out:
                self.actions_blocked += 1
                self.opportunity_actions[opp.opportunity_id] = "OPT_OUT_BLOCKED"
                continue

            f_code = opp.failure_type
            
            # Rule 1: High LTV Enterprise with overdue invoice or severe issue -> Escalate
            if cust.segment == "B2B_ENTERPRISE" and (opp.initial_amount > 50000.0 or opp.days_overdue > 14):
                self.actions_attempted += 1
                self.escalations += 1
                self.intervention_cost += 50.0
                dynamics.process_escalation(world, cust.id, opp)
                self.actions_successful += 1
                self.opportunity_actions[opp.opportunity_id] = "ESCALATE"

            # Rule 2: Unknown Payment -> Reconcile
            elif f_code == "UNKNOWN_ERROR" or (opp.entity_type == "PAYMENT" and world.payments[opp.entity_id].status == PaymentStatus.UNKNOWN):
                self.actions_attempted += 1
                self.intervention_cost += 0.5
                dynamics.process_reconciliation(world, opp.entity_id)
                self.actions_successful += 1
                self.opportunity_actions[opp.opportunity_id] = "RECONCILE"

            # Rule 3: Transient Failure -> Immediate / Backoff Retry
            elif f_code in ["TIMEOUT", "NETWORK_ERROR", "GATEWAY_TIMEOUT"]:
                self.actions_attempted += 1
                self.intervention_cost += 1.0
                dynamics.process_retry_attempt(world, opp.entity_id, delay=3600)  # T+1h
                self.actions_successful += 1
                self.opportunity_actions[opp.opportunity_id] = "RETRY"

            # Rule 4: Liquidity Failure -> Delayed Payment Link (T+24h)
            elif f_code in ["INSUFFICIENT_FUNDS", "LIMIT_EXCEEDED"]:
                if cust.recent_contacts < self.constraints.max_contacts_per_customer:
                    self.actions_attempted += 1
                    self.customer_contacts += 1
                    self.intervention_cost += 2.5
                    dynamics.process_payment_link_or_message(world, cust.id, opp, "WHATSAPP")
                    self.actions_successful += 1
                    self.opportunity_actions[opp.opportunity_id] = "SEND_PAYMENT_LINK"

            # Rule 5: Credential / OTP Failure -> SMS / WhatsApp payment link
            elif f_code in ["EXPIRED_CARD", "INVALID_CVV", "3D_SECURE_FAILED", "OTP_REQUIRED"]:
                if cust.recent_contacts < self.constraints.max_contacts_per_customer:
                    self.actions_attempted += 1
                    self.customer_contacts += 1
                    self.intervention_cost += 2.5
                    dynamics.process_payment_link_or_message(world, cust.id, opp, "SMS")
                    self.actions_successful += 1
                    self.opportunity_actions[opp.opportunity_id] = "SEND_PAYMENT_LINK"

            # Rule 6: Overdue Invoice -> Email Reminder
            elif opp.entity_type == "INVOICE":
                if cust.recent_contacts < self.constraints.max_contacts_per_customer:
                    self.actions_attempted += 1
                    self.customer_contacts += 1
                    self.intervention_cost += 1.0
                    dynamics.process_payment_link_or_message(world, cust.id, opp, "EMAIL")
                    self.actions_successful += 1
                    self.opportunity_actions[opp.opportunity_id] = "SEND_MESSAGE"

            # Rule 7: Abandoned Checkout -> WhatsApp Recovery Link (T+30m)
            elif opp.entity_type == "CHECKOUT":
                if cust.recent_contacts < self.constraints.max_contacts_per_customer:
                    self.actions_attempted += 1
                    self.customer_contacts += 1
                    self.intervention_cost += 2.5
                    dynamics.process_payment_link_or_message(world, cust.id, opp, "WHATSAPP")
                    self.actions_successful += 1
                    self.opportunity_actions[opp.opportunity_id] = "SEND_PAYMENT_LINK"

            else:
                self.opportunity_actions[opp.opportunity_id] = "WAIT"

            # Track relationship cost impact
            rel_state = RelationshipState(
                customer_id=cust.id,
                recent_contacts=cust.recent_contacts,
                recent_responses=cust.recent_responses,
                successful_prior_recoveries=cust.successful_prior_recoveries,
                customer_value=cust.ltv,
                complaints=cust.complaints,
                opt_out=False,
                silence_duration=cust.silence_duration
            )
            self.relationship_cost += rel_state.relationship_cost_proxy()
