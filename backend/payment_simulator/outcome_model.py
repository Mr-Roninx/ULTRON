from typing import Dict, Any, Optional, Tuple
from simulator.world import world
from simulator.models import PaymentStatus, InvoiceStatus, CheckoutStatus
from simulator.clock import clock
from simulator.event_bus import event_bus
from simulator.events import DomainEvent
from backend.payment_simulator.payment_outcomes import payment_outcome_simulator
from backend.payment_simulator.customer_behavior import customer_behavior_simulator
from backend.payment_intelligence.schemas import CustomerResponseCode

class OutcomeModel:
    """
    Executes simulated financial outcome transitions when recovery actions
    are executed by the agent loop or baseline strategies.
    """
    def process_payment_retry(
        self,
        payment_id: str,
        gateway_id: str = "GATEWAY_A"
    ) -> Tuple[PaymentStatus, Dict[str, Any]]:
        payment = world.payments.get(payment_id)
        if not payment:
            return PaymentStatus.FAILED, {"error": "Payment not found"}

        status, details = payment_outcome_simulator.simulate_retry_outcome(
            payment_id=payment_id,
            gateway_id=gateway_id,
            rail=payment.rail or "CARD",
            failure_code=payment.failure_code or "UNKNOWN_ERROR"
        )

        payment.status = status
        now = clock.now()

        # Emit domain event
        event_bus.publish(DomainEvent(
            event_id=f"evt_retry_{payment_id}_{now}",
            event_type="PAYMENT_RETRY_OUTCOME",
            entity_type="PAYMENT",
            entity_id=payment_id,
            customer_id=payment.customer_id,
            timestamp=now,
            new_state=status.value,
            payload=details
        ))

        return status, details

    def process_customer_communication(
        self,
        customer_id: str,
        channel: str,
        message_type: str
    ) -> Tuple[CustomerResponseCode, str]:
        customer = world.customers.get(customer_id)
        segment = customer.segment if customer else "SMB"
        recent = customer.recent_contacts if customer else 0
        opt_out = customer.opt_out if customer else False

        code, msg = customer_behavior_simulator.simulate_response(
            customer_segment=segment,
            channel=channel,
            message_type=message_type,
            recent_contacts=recent,
            historical_opt_out=opt_out
        )

        if customer:
            customer.recent_contacts += 1
            if code == CustomerResponseCode.OPTOUT:
                customer.opt_out = True
            elif code == CustomerResponseCode.PAY_NOW:
                for p in world.payments.values():
                    if p.customer_id == customer_id and p.status in [PaymentStatus.FAILED, PaymentStatus.UNKNOWN, PaymentStatus.INITIATED, PaymentStatus.CREATED]:
                        p.status = PaymentStatus.SETTLED
                for inv in world.invoices.values():
                    if inv.customer_id == customer_id and inv.status == InvoiceStatus.OVERDUE:
                        inv.status = InvoiceStatus.PAID
                for chk in world.checkouts.values():
                    if chk.customer_id == customer_id and chk.status == CheckoutStatus.ABANDONED:
                        chk.status = CheckoutStatus.COMPLETED

        now = clock.now()
        event_bus.publish(DomainEvent(
            event_id=f"evt_comm_{customer_id}_{now}",
            event_type="CUSTOMER_RESPONSE_RECEIVED",
            entity_type="CUSTOMER",
            entity_id=customer_id,
            customer_id=customer_id,
            timestamp=now,
            new_state=code.value,
            payload={"channel": channel, "message_type": message_type, "response_message": msg}
        ))

        return code, msg

outcome_model = OutcomeModel()
