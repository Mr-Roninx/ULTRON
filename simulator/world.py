import copy
import uuid
from typing import Dict
from simulator.models import Customer, Payment, Invoice, Checkout, Gateway, PaymentAttempt, RecoveryAction, Communication, PaymentStatus, InvoiceStatus, CheckoutStatus
from simulator.event_bus import event_bus
from simulator.events import DomainEvent
from simulator.clock import clock
from backend.audit.ledger import audit_ledger

class FinancialWorld:
    def __init__(self):
        self.customers: Dict[str, Customer] = {}
        self.payments: Dict[str, Payment] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.checkouts: Dict[str, Checkout] = {}
        self.gateways: Dict[str, Gateway] = {}
        self.payment_attempts: Dict[str, PaymentAttempt] = {}
        self.recovery_actions: Dict[str, RecoveryAction] = {}
        self.communications: Dict[str, Communication] = {}
        
    def reset(self):
        self.customers.clear()
        self.payments.clear()
        self.invoices.clear()
        self.checkouts.clear()
        self.gateways.clear()
        self.payment_attempts.clear()
        self.recovery_actions.clear()
        self.communications.clear()
        clock.reset()
        event_bus.reset()
        audit_ledger.reset()
        
    def snapshot(self) -> "FinancialWorld":
        # Deep copy to create an isolated world for counterfactuals
        new_world = FinancialWorld()
        new_world.customers = copy.deepcopy(self.customers)
        new_world.payments = copy.deepcopy(self.payments)
        new_world.invoices = copy.deepcopy(self.invoices)
        new_world.checkouts = copy.deepcopy(self.checkouts)
        new_world.gateways = copy.deepcopy(self.gateways)
        new_world.payment_attempts = copy.deepcopy(self.payment_attempts)
        new_world.recovery_actions = copy.deepcopy(self.recovery_actions)
        new_world.communications = copy.deepcopy(self.communications)
        return new_world

    def restore_from(self, other: "FinancialWorld"):
        self.customers = copy.deepcopy(other.customers)
        self.payments = copy.deepcopy(other.payments)
        self.invoices = copy.deepcopy(other.invoices)
        self.checkouts = copy.deepcopy(other.checkouts)
        self.gateways = copy.deepcopy(other.gateways)
        self.payment_attempts = copy.deepcopy(other.payment_attempts)
        self.recovery_actions = copy.deepcopy(other.recovery_actions)
        self.communications = copy.deepcopy(other.communications)

    def _publish_event(self, event_type: str, entity_type: str, entity_id: str, customer_id: str, new_state: str, payload: dict, previous_state: str = None):
        event = DomainEvent(
            event_id=f"E_{str(uuid.uuid4())[:8]}",
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            customer_id=customer_id,
            timestamp=clock.get_time(),
            previous_state=previous_state,
            new_state=new_state,
            payload=payload
        )
        event_bus.publish(event)
        audit_ledger.log(
            event_type=event_type,
            actor="SYSTEM_SIMULATOR",
            payload={"entity_type": entity_type, "entity_id": entity_id, "customer_id": customer_id, "previous_state": previous_state, "new_state": new_state, "payload": payload},
            mission_id=customer_id,
            timestamp=clock.get_time()
        )
        
    def add_customer(self, customer: Customer):
        self.customers[customer.id] = customer
        self._publish_event("CUSTOMER_CREATED", "CUSTOMER", customer.id, customer.id, "CREATED", customer.model_dump())
        
    def add_payment(self, payment: Payment):
        self.payments[payment.id] = payment
        self._publish_event(f"PAYMENT_{payment.status.value}", "PAYMENT", payment.id, payment.customer_id, payment.status.value, payment.model_dump())
        
    def add_invoice(self, invoice: Invoice):
        self.invoices[invoice.id] = invoice
        self._publish_event(f"INVOICE_{invoice.status.value}", "INVOICE", invoice.id, invoice.customer_id, invoice.status.value, invoice.model_dump())
        
    def add_checkout(self, checkout: Checkout):
        self.checkouts[checkout.id] = checkout
        self._publish_event(f"CHECKOUT_{checkout.status.value}", "CHECKOUT", checkout.id, checkout.customer_id, checkout.status.value, checkout.model_dump())

    def add_gateway(self, gateway: Gateway):
        self.gateways[gateway.id] = gateway

    def add_payment_attempt(self, attempt: PaymentAttempt):
        self.payment_attempts[attempt.id] = attempt
        
    def add_recovery_action(self, action: RecoveryAction):
        self.recovery_actions[action.id] = action

    def add_communication(self, comm: Communication):
        self.communications[comm.id] = comm

    def update_payment_status(self, payment_id: str, new_status: str, failure_code: str = None):
        from financial.fsm import PaymentFSM
        if payment_id not in self.payments:
            raise ValueError("Payment not found")
        payment = self.payments[payment_id]
        target_status = PaymentStatus(new_status)
        previous_status = payment.status.value
        
        PaymentFSM.validate_transition(payment.status, target_status)
        
        payment.status = target_status
        if failure_code:
            payment.failure_code = failure_code
            
        self._publish_event(f"PAYMENT_{payment.status.value}", "PAYMENT", payment.id, payment.customer_id, payment.status.value, payment.model_dump(), previous_state=previous_status)
        
    def update_invoice_status(self, invoice_id: str, new_status: str):
        from financial.fsm import InvoiceFSM
        if invoice_id not in self.invoices:
            raise ValueError("Invoice not found")
        invoice = self.invoices[invoice_id]
        target_status = InvoiceStatus(new_status)
        previous_status = invoice.status.value
        
        InvoiceFSM.validate_transition(invoice.status, target_status)
        
        invoice.status = target_status
        self._publish_event(f"INVOICE_{invoice.status.value}", "INVOICE", invoice.id, invoice.customer_id, invoice.status.value, invoice.model_dump(), previous_state=previous_status)

    def update_checkout_status(self, checkout_id: str, new_status: str):
        from financial.fsm import CheckoutFSM
        if checkout_id not in self.checkouts:
            raise ValueError("Checkout not found")
        checkout = self.checkouts[checkout_id]
        target_status = CheckoutStatus(new_status)
        previous_status = checkout.status.value

        CheckoutFSM.validate_transition(checkout.status, target_status)

        checkout.status = target_status
        self._publish_event(f"CHECKOUT_{checkout.status.value}", "CHECKOUT", checkout.id, checkout.customer_id, checkout.status.value, checkout.model_dump(), previous_state=previous_status)

world = FinancialWorld()
