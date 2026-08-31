import random
import hashlib
from typing import Dict, Any, Optional
from simulator.models import (
    Customer, Payment, Invoice, Checkout, 
    PaymentStatus, InvoiceStatus, CheckoutStatus, RecoveryAction, Communication
)
from simulator.world import FinancialWorld
from simulator.clock import clock
from backend.benchmark.models import BenchmarkOpportunity

class SimulationDynamicsEngine:
    """
    Handles realistic, deterministic state transitions for payments, invoices, 
    and checkouts in response to actions or natural customer behavior over time.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed

    def _deterministic_prob(self, key: str, salt: str = "") -> float:
        h = hashlib.sha256(f"{self.seed}_{key}_{salt}".encode()).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF

    def simulate_natural_progression(self, world: FinancialWorld, current_time: int, horizon_seconds: int):
        """
        Simulates natural customer recovery (customers fixing issues on their own without intervention).
        Natural recovery rate is modest (5-12% depending on failure type).
        """
        for p_id, payment in list(world.payments.items()):
            if payment.status == PaymentStatus.FAILED:
                f_code = payment.failure_code or "UNKNOWN"
                # Transient errors have higher natural recovery probability
                base_prob = 0.12 if f_code in ["TIMEOUT", "NETWORK_ERROR"] else 0.04
                if self._deterministic_prob(p_id, "natural_payment_recovery") < base_prob:
                    # Naturally recovers at a random time within the horizon
                    recovery_delay = int(self._deterministic_prob(p_id, "natural_delay") * (horizon_seconds * 0.7))
                    def _natural_settle(pay_id=p_id):
                        if pay_id in world.payments and world.payments[pay_id].status == PaymentStatus.FAILED:
                            # Direct recovery
                            world.payments[pay_id].status = PaymentStatus.SETTLED
                    clock.schedule(current_time + recovery_delay, _natural_settle)

        for inv_id, inv in list(world.invoices.items()):
            if inv.status == InvoiceStatus.OVERDUE:
                if self._deterministic_prob(inv_id, "natural_invoice_recovery") < 0.08:
                    recovery_delay = int(self._deterministic_prob(inv_id, "natural_inv_delay") * (horizon_seconds * 0.8))
                    def _natural_pay_inv(i_id=inv_id):
                        if i_id in world.invoices and world.invoices[i_id].status == InvoiceStatus.OVERDUE:
                            world.update_invoice_status(i_id, InvoiceStatus.PAID.value)
                    clock.schedule(current_time + recovery_delay, _natural_pay_inv)

        for chk_id, chk in list(world.checkouts.items()):
            if chk.status == CheckoutStatus.ABANDONED:
                if self._deterministic_prob(chk_id, "natural_chk_recovery") < 0.05:
                    recovery_delay = int(self._deterministic_prob(chk_id, "natural_chk_delay") * min(86400 * 3, horizon_seconds))
                    def _natural_complete_chk(c_id=chk_id):
                        if c_id in world.checkouts and world.checkouts[c_id].status == CheckoutStatus.ABANDONED:
                            world.update_checkout_status(c_id, CheckoutStatus.COMPLETED.value)
                    clock.schedule(current_time + recovery_delay, _natural_complete_chk)

    def process_retry_attempt(self, world: FinancialWorld, payment_id: str, delay: int) -> bool:
        """
        Calculates whether a retry succeeds based on failure category, delay, and gateway health.
        """
        if payment_id not in world.payments:
            return False
        payment = world.payments[payment_id]
        if payment.status != PaymentStatus.FAILED:
            return False

        gw = world.gateways.get(payment.gateway_id or "gw_razorpay")
        gw_health = gw.health if gw else 1.0

        f_code = payment.failure_code or "UNKNOWN"
        # Success probability model:
        # 1. Transient (TIMEOUT, NETWORK_ERROR, GATEWAY_TIMEOUT): 80-90% if delay >= 1h
        # 2. Liquidity (INSUFFICIENT_FUNDS, LIMIT_EXCEEDED): 35-50% if delay >= 24h, else 15%
        # 3. Non-retryable (DO_NOT_HONOR, STOLEN_CARD): 0%
        # 4. Credential / Customer action: 5% (needs customer intervention)
        if f_code in ["TIMEOUT", "NETWORK_ERROR", "GATEWAY_TIMEOUT"]:
            success_rate = 0.85 * gw_health
        elif f_code in ["INSUFFICIENT_FUNDS", "LIMIT_EXCEEDED"]:
            success_rate = 0.45 if delay >= 86400 else 0.15
        elif f_code in ["DO_NOT_HONOR", "STOLEN_CARD"]:
            success_rate = 0.0
        else:
            success_rate = 0.10

        prob = self._deterministic_prob(payment_id, f"retry_{delay}")
        is_success = prob < success_rate

        def _execute_retry_outcome(p_id=payment_id, success=is_success):
            if p_id in world.payments and world.payments[p_id].status == PaymentStatus.FAILED:
                if success:
                    world.payments[p_id].status = PaymentStatus.SETTLED
                else:
                    # Remains failed
                    pass
        clock.schedule(clock.now() + delay, _execute_retry_outcome)
        return is_success

    def process_payment_link_or_message(self, world: FinancialWorld, customer_id: str, opportunity: BenchmarkOpportunity, channel: str) -> bool:
        """
        Calculates customer response to payment link or message.
        """
        if customer_id not in world.customers:
            return False
        cust = world.customers[customer_id]
        if cust.opt_out:
            return False

        # Relationship fatigue penalties:
        # Each contact increases fatigue unless response history is strong
        fatigue_penalty = cust.recent_contacts * 0.08
        complaint_penalty = cust.complaints * 0.25
        response_affinity = (cust.recent_responses / max(1, cust.recent_contacts)) * 0.20

        # Base conversion by channel & segment:
        base_conversion = {
            "B2B_ENTERPRISE": 0.70,
            "SMB": 0.60,
            "RETAIL": 0.45,
            "D2C": 0.40
        }.get(cust.segment, 0.50)

        conversion_prob = max(0.05, min(0.95, base_conversion + response_affinity - fatigue_penalty - complaint_penalty))
        prob = self._deterministic_prob(opportunity.entity_id, f"link_{channel}_{cust.recent_contacts}")
        is_paid = prob < conversion_prob

        # Response latency: 2 hours to 48 hours
        latency = int(3600 * 2 + (self._deterministic_prob(opportunity.entity_id, "latency") * 3600 * 46))

        def _execute_link_outcome(opp=opportunity, paid=is_paid):
            if opp.entity_type == "PAYMENT" and opp.entity_id in world.payments:
                if paid and world.payments[opp.entity_id].status == PaymentStatus.FAILED:
                    world.payments[opp.entity_id].status = PaymentStatus.SETTLED
            elif opp.entity_type == "INVOICE" and opp.entity_id in world.invoices:
                if paid and world.invoices[opp.entity_id].status == InvoiceStatus.OVERDUE:
                    world.update_invoice_status(opp.entity_id, InvoiceStatus.PAID.value)
            elif opp.entity_type == "CHECKOUT" and opp.entity_id in world.checkouts:
                if paid and world.checkouts[opp.entity_id].status == CheckoutStatus.ABANDONED:
                    world.update_checkout_status(opp.entity_id, CheckoutStatus.COMPLETED.value)

        clock.schedule(clock.now() + latency, _execute_link_outcome)
        cust.recent_contacts += 1
        if is_paid:
            cust.recent_responses += 1
            cust.successful_prior_recoveries += 1
        return is_paid

    def process_reconciliation(self, world: FinancialWorld, payment_id: str) -> bool:
        """
        Reconciles UNKNOWN payment with gateway.
        """
        if payment_id not in world.payments:
            return False
        payment = world.payments[payment_id]
        if payment.status != PaymentStatus.UNKNOWN:
            return False

        # 60% of UNKNOWN payments were actually settled at gateway
        prob = self._deterministic_prob(payment_id, "reconcile")
        if prob < 0.60:
            payment.status = PaymentStatus.SETTLED
            return True
        else:
            payment.status = PaymentStatus.FAILED
            return False

    def process_escalation(self, world: FinancialWorld, customer_id: str, opportunity: BenchmarkOpportunity) -> bool:
        """
        Human account manager escalation (expensive: 50.0 cost, but 85% success for Enterprise/SMB).
        """
        if customer_id not in world.customers:
            return False
        cust = world.customers[customer_id]
        
        prob = self._deterministic_prob(opportunity.entity_id, "escalation")
        success_rate = 0.88 if cust.segment in ["B2B_ENTERPRISE", "SMB"] else 0.50
        is_recovered = prob < success_rate

        latency = 86400 * 2  # 2 business days
        def _execute_escalation(opp=opportunity, success=is_recovered):
            if opp.entity_type == "PAYMENT" and opp.entity_id in world.payments:
                if success and world.payments[opp.entity_id].status == PaymentStatus.FAILED:
                    world.payments[opp.entity_id].status = PaymentStatus.SETTLED
            elif opp.entity_type == "INVOICE" and opp.entity_id in world.invoices:
                if success and world.invoices[opp.entity_id].status == InvoiceStatus.OVERDUE:
                    world.update_invoice_status(opp.entity_id, InvoiceStatus.PAID.value)
            elif opp.entity_type == "CHECKOUT" and opp.entity_id in world.checkouts:
                if success and world.checkouts[opp.entity_id].status == CheckoutStatus.ABANDONED:
                    world.update_checkout_status(opp.entity_id, CheckoutStatus.COMPLETED.value)

        clock.schedule(clock.now() + latency, _execute_escalation)
        return is_recovered
