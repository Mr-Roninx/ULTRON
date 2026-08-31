import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from simulator.models import Customer, Payment, PaymentStatus
from simulator.world import world
from simulator.clock import clock
from backend.tools.registry import registry
from financial.idempotency import idempotency_engine

class TestAdversarialToolIdempotency(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()
        idempotency_engine.clear()
        world.add_customer(Customer(id="c_1", name="Alpha", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_1", customer_id="c_1", amount=1000.0, status=PaymentStatus.UNKNOWN, created_at=0))

    def test_reconcile_payment_idempotency(self):
        """Executing reconcile_payment twice for the same payment in a mission returns cached result without re-executing."""
        res1 = registry.execution.reconcile_payment("m_1", "c_1", "p_1", authority="AUTONOMOUS")
        self.assertTrue(res1.success)
        self.assertEqual(res1.state_change, "RECONCILED")

        # Second call with identical payload
        res2 = registry.execution.reconcile_payment("m_1", "c_1", "p_1", authority="AUTONOMOUS")
        self.assertTrue(res2.success)
        self.assertIn("Duplicate execution suppressed", res2.message)
        self.assertEqual(res2.action_id, res1.action_id)

    def test_send_customer_message_idempotency(self):
        """Duplicate message execution is suppressed to avoid spamming the client."""
        res1 = registry.execution.send_customer_message("m_1", "c_1", channel="EMAIL", message_type="GENTLE_REMINDER", authority="AUTONOMOUS")
        self.assertTrue(res1.success)
        self.assertEqual(len(world.communications), 1)

        # Immediate second send with same parameters
        res2 = registry.execution.send_customer_message("m_1", "c_1", channel="EMAIL", message_type="GENTLE_REMINDER", authority="AUTONOMOUS")
        self.assertTrue(res2.success)
        self.assertIn("Duplicate execution suppressed", res2.message)
        # Communications count must still be 1!
        self.assertEqual(len(world.communications), 1)

    def test_distinct_actions_not_blocked_by_idempotency(self):
        """Different channels or message types must NOT be blocked."""
        res1 = registry.execution.send_customer_message("m_1", "c_1", channel="EMAIL", message_type="GENTLE_REMINDER", authority="AUTONOMOUS")
        res2 = registry.execution.send_customer_message("m_1", "c_1", channel="SMS", message_type="GENTLE_REMINDER", authority="AUTONOMOUS")
        self.assertTrue(res1.success)
        self.assertTrue(res2.success)
        self.assertEqual(len(world.communications), 2)

    def test_generate_payment_link_idempotency(self):
        """Duplicate payment link generation is suppressed."""
        res1 = registry.execution.generate_payment_link("m_1", "c_1", items=["inv_1", "inv_2"], authority="AUTONOMOUS")
        self.assertTrue(res1.success)
        initial_comms = len(world.communications)

        res2 = registry.execution.generate_payment_link("m_1", "c_1", items=["inv_2", "inv_1"], authority="AUTONOMOUS")
        self.assertTrue(res2.success)
        self.assertIn("Duplicate execution suppressed", res2.message)
        self.assertEqual(len(world.communications), initial_comms)

    def test_register_ptp_idempotency(self):
        """Duplicate PTP registration with same date is suppressed."""
        res1 = registry.execution.register_ptp("m_1", "c_1", promise_date=1000, authority="AUTONOMOUS")
        self.assertTrue(res1.success)

        res2 = registry.execution.register_ptp("m_1", "c_1", promise_date=1000, authority="AUTONOMOUS")
        self.assertTrue(res2.success)
        self.assertIn("Duplicate execution suppressed", res2.message)

    def test_escalate_to_human_idempotency(self):
        """Duplicate escalation with same reason is suppressed."""
        res1 = registry.execution.escalate_to_human("m_1", "c_1", reason="Unresponsive", authority="AUTONOMOUS")
        self.assertTrue(res1.success)

        res2 = registry.execution.escalate_to_human("m_1", "c_1", reason="Unresponsive", authority="AUTONOMOUS")
        self.assertTrue(res2.success)
        self.assertIn("Duplicate execution suppressed", res2.message)

if __name__ == '__main__':
    unittest.main()
