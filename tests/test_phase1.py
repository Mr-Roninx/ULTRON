import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.models import PaymentStatus, InvoiceStatus, CheckoutStatus, Payment, Customer
from financial.fsm import PaymentFSM, InvalidStateTransitionError
from simulator.clock import clock
from simulator.world import world
from simulator.event_bus import event_bus
from financial.failure_intelligence import failure_normalizer, failure_classifier, retryability_resolver, reconciliation_resolver, FailureCategory

class TestPhase1(unittest.TestCase):
    def setUp(self):
        world.reset()

    # FSM Tests
    def test_payment_fsm_valid_transitions(self):
        PaymentFSM.validate_transition(PaymentStatus.CREATED, PaymentStatus.INITIATED)
        PaymentFSM.validate_transition(PaymentStatus.INITIATED, PaymentStatus.AUTHORIZING)
        PaymentFSM.validate_transition(PaymentStatus.UNKNOWN, PaymentStatus.RECONCILING)

    def test_payment_fsm_invalid_transitions(self):
        with self.assertRaises(InvalidStateTransitionError):
            PaymentFSM.validate_transition(PaymentStatus.SETTLED, PaymentStatus.CREATED)
        with self.assertRaises(InvalidStateTransitionError):
            PaymentFSM.validate_transition(PaymentStatus.FAILED, PaymentStatus.CAPTURED)

    # Clock Tests
    def test_clock_advance(self):
        clock.reset(100)
        clock.advance(50)
        self.assertEqual(clock.now(), 150)

    def test_clock_schedule_and_fire(self):
        clock.reset(100)
        fired = []
        clock.schedule(150, lambda: fired.append(True))
        clock.advance(49)
        self.assertEqual(len(fired), 0)
        clock.advance(2)
        self.assertEqual(len(fired), 1)
        self.assertEqual(clock.now(), 151)

    def test_clock_cancel_scheduled_event(self):
        clock.reset(100)
        fired = []
        evt = clock.schedule(150, lambda: fired.append(True))
        clock.cancel(evt)
        clock.advance(100)
        self.assertEqual(len(fired), 0)

    def test_clock_run_until(self):
        clock.reset(100)
        fired = []
        clock.schedule(120, lambda: fired.append(1))
        clock.schedule(130, lambda: fired.append(2))
        clock.run_until(125)
        self.assertEqual(fired, [1])
        self.assertEqual(clock.now(), 125)

    def test_clock_negative_advance_rejected(self):
        with self.assertRaises(ValueError):
            clock.advance(-10)

    # Event Tests
    def test_domain_event_created_on_transition(self):
        c = Customer(id="c_1", name="Test", segment="B2B", created_at=0)
        world.add_customer(c)
        p = Payment(id="p_1", customer_id="c_1", amount=100.0, created_at=0)
        world.add_payment(p)
        
        # Clear bus history for isolation
        event_bus.events = []
        world.update_payment_status("p_1", "INITIATED")
        
        self.assertEqual(len(event_bus.events), 1)
        evt = event_bus.events[0]
        self.assertEqual(evt.entity_type, "PAYMENT")
        self.assertEqual(evt.previous_state, "CREATED")
        self.assertEqual(evt.new_state, "INITIATED")

    # Snapshot Test
    def test_world_snapshot_creates_independent_copy(self):
        c = Customer(id="c_1", name="Test", segment="B2B", created_at=0)
        world.add_customer(c)
        p = Payment(id="p_1", customer_id="c_1", amount=100.0, created_at=0)
        world.add_payment(p)

        snapshot = world.snapshot()
        snapshot.update_payment_status("p_1", "INITIATED")

        # Original world should not be affected
        self.assertEqual(world.payments["p_1"].status, PaymentStatus.CREATED)
        # Snapshot world should be affected
        self.assertEqual(snapshot.payments["p_1"].status, PaymentStatus.INITIATED)

    # Failure Intelligence Tests
    def test_failure_normalizer(self):
        res = failure_normalizer.normalize("insufficient_funds", "stripe")
        self.assertEqual(res, "INSUFFICIENT_FUNDS")
        res = failure_normalizer.normalize("unknown_random_error", "stripe")
        self.assertEqual(res, "UNKNOWN_ERROR")

    def test_failure_classifier_all_categories(self):
        self.assertEqual(failure_classifier.classify("INSUFFICIENT_FUNDS"), FailureCategory.LIQUIDITY_RELATED)
        self.assertEqual(failure_classifier.classify("TIMEOUT"), FailureCategory.TRANSIENT)
        self.assertEqual(failure_classifier.classify("UNKNOWN_ERROR"), FailureCategory.UNKNOWN)

    def test_retryability_resolver(self):
        self.assertTrue(retryability_resolver.is_retryable(FailureCategory.TRANSIENT))
        self.assertFalse(retryability_resolver.is_retryable(FailureCategory.LIQUIDITY_RELATED))

if __name__ == '__main__':
    unittest.main()
