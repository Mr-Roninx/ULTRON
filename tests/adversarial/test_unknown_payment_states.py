import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from simulator.models import Customer, Payment, PaymentStatus
from simulator.world import world
from simulator.clock import clock
from financial.fsm import PaymentFSM, InvalidStateTransitionError
from financial.reconciliation import reconciliation
from backend.tools.registry import registry

class TestAdversarialUnknownPaymentStates(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()

    def test_direct_retry_on_unknown_is_blocked_by_fsm(self):
        """Hostile attempt to retry an UNKNOWN payment directly without reconciliation."""
        world.add_customer(Customer(id="c_1001", name="Delta LLC", segment="B2B_ENTERPRISE", created_at=0))
        payment = Payment(id="p_unk_1", customer_id="c_1001", amount=3000.0, status=PaymentStatus.UNKNOWN, created_at=0)
        world.add_payment(payment)

        # Direct transition UNKNOWN -> INITIATED must be rejected by PaymentFSM
        with self.assertRaises(InvalidStateTransitionError):
            PaymentFSM.validate_transition(PaymentStatus.UNKNOWN, PaymentStatus.INITIATED)

    def test_unknown_reconciles_to_failed_allows_retry(self):
        """UNKNOWN -> RECONCILING -> FAILED lifecycle correctly unblocks safe retry."""
        world.add_customer(Customer(id="c_1001", name="Delta LLC", segment="B2B_ENTERPRISE", created_at=0))
        payment = Payment(id="p_unk_2", customer_id="c_1001", amount=3000.0, status=PaymentStatus.UNKNOWN, created_at=0)
        world.add_payment(payment)

        # 1. Reconcile to FAILED
        success = reconciliation.reconcile("p_unk_2", PaymentStatus.FAILED)
        self.assertTrue(success)
        self.assertEqual(world.payments["p_unk_2"].status, PaymentStatus.FAILED)

    def test_unknown_reconciles_to_settled_prevents_duplicate_charge(self):
        """UNKNOWN -> RECONCILING -> SETTLED prevents duplicate payment collection."""
        world.add_customer(Customer(id="c_1001", name="Delta LLC", segment="B2B_ENTERPRISE", created_at=0))
        payment = Payment(id="p_unk_3", customer_id="c_1001", amount=3000.0, status=PaymentStatus.UNKNOWN, created_at=0)
        world.add_payment(payment)

        # 1. Reconcile to SETTLED
        success = reconciliation.reconcile("p_unk_3", PaymentStatus.SETTLED)
        self.assertTrue(success)
        self.assertEqual(world.payments["p_unk_3"].status, PaymentStatus.SETTLED)

        # Attempting to retry a SETTLED payment must fail FSM
        with self.assertRaises(InvalidStateTransitionError):
            PaymentFSM.validate_transition(PaymentStatus.SETTLED, PaymentStatus.INITIATED)

if __name__ == '__main__':
    unittest.main()
