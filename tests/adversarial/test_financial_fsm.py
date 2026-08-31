import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from simulator.models import PaymentStatus, InvoiceStatus, CheckoutStatus, Customer, Payment, Invoice, Checkout
from simulator.world import world
from simulator.event_bus import event_bus
from simulator.clock import clock
from financial.fsm import PaymentFSM, InvoiceFSM, CheckoutFSM, InvalidStateTransitionError

class TestAdversarialFinancialFSM(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()

    def test_invalid_payment_fsm_transitions_rejected(self):
        """Hostile invalid payment state transitions."""
        invalid_pairs = [
            (PaymentStatus.SETTLED, PaymentStatus.CREATED),
            (PaymentStatus.FAILED, PaymentStatus.CAPTURED),
            (PaymentStatus.REFUNDED, PaymentStatus.AUTHORIZED),
            (PaymentStatus.REVERSED, PaymentStatus.CAPTURED),
            (PaymentStatus.SETTLED, PaymentStatus.INITIATED),
            (PaymentStatus.CREATED, PaymentStatus.SETTLED)
        ]
        for current, target in invalid_pairs:
            with self.assertRaises(InvalidStateTransitionError, msg=f"Failed to reject {current} -> {target}"):
                PaymentFSM.validate_transition(current, target)

    def test_invalid_invoice_fsm_transitions_rejected(self):
        """Hostile invalid invoice state transitions."""
        invalid_pairs = [
            (InvoiceStatus.PAID, InvoiceStatus.OVERDUE),
            (InvoiceStatus.PAID, InvoiceStatus.CREATED),
            (InvoiceStatus.OVERDUE, InvoiceStatus.CREATED)
        ]
        for current, target in invalid_pairs:
            with self.assertRaises(InvalidStateTransitionError, msg=f"Failed to reject {current} -> {target}"):
                InvoiceFSM.validate_transition(current, target)

    def test_invalid_checkout_fsm_transitions_rejected(self):
        """Hostile invalid checkout state transitions."""
        invalid_pairs = [
            (CheckoutStatus.COMPLETED, CheckoutStatus.STARTED),
            (CheckoutStatus.COMPLETED, CheckoutStatus.ABANDONED),
            (CheckoutStatus.ABANDONED, CheckoutStatus.STARTED)
        ]
        for current, target in invalid_pairs:
            with self.assertRaises(InvalidStateTransitionError, msg=f"Failed to reject {current} -> {target}"):
                CheckoutFSM.validate_transition(current, target)

    def test_exact_one_to_one_domain_event_generation(self):
        """Every valid transition must publish exactly one typed domain event."""
        world.add_customer(Customer(id="c_1", name="Alpha", segment="B2B_ENTERPRISE", created_at=0))
        # Initial customer creation publishes 1 event
        self.assertEqual(len(event_bus.get_history()), 1)

        payment = Payment(id="p_1", customer_id="c_1", amount=100.0, status=PaymentStatus.CREATED, created_at=0)
        world.add_payment(payment)
        # Adding payment publishes 1 event (PAYMENT_CREATED)
        self.assertEqual(len(event_bus.get_history()), 2)

        # Transition: CREATED -> INITIATED
        world.update_payment_status("p_1", PaymentStatus.INITIATED.value)
        self.assertEqual(len(event_bus.get_history()), 3)
        last_event = event_bus.get_history()[-1]
        self.assertEqual(last_event.event_type, "PAYMENT_INITIATED")
        self.assertEqual(last_event.previous_state, "CREATED")
        self.assertEqual(last_event.new_state, "INITIATED")

if __name__ == '__main__':
    unittest.main()
