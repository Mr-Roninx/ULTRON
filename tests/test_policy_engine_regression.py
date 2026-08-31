import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial.policy import policy_engine, PolicyViolationError, PolicyContext
from simulator.customer_state import customer_state_engine
from simulator.models import Customer, Payment, PaymentStatus
from simulator.world import world

class TestPolicyEngineRegression(unittest.TestCase):
    def setUp(self):
        world.reset()

    def test_b2b_enterprise_discount_policy_pass(self):
        world.add_customer(Customer(id="c_ent", name="Enterprise Client", segment="B2B_ENTERPRISE", created_at=0))
        context = customer_state_engine.get_snapshot("c_ent")
        # Should pass validation for positive amount
        self.assertTrue(policy_engine.validate("APPLY_DISCOUNT", context, {"amount": 500.0}))

    def test_b2b_smb_discount_policy_rejected(self):
        world.add_customer(Customer(id="c_smb", name="SMB Client", segment="B2B_SMB", created_at=0))
        context = customer_state_engine.get_snapshot("c_smb")
        with self.assertRaises(PolicyViolationError) as cm:
            policy_engine.validate("APPLY_DISCOUNT", context, {"amount": 100.0})
        self.assertIn("only allowed for B2B_ENTERPRISE", str(cm.exception))

    def test_negative_or_zero_discount_rejected(self):
        world.add_customer(Customer(id="c_ent", name="Enterprise Client", segment="B2B_ENTERPRISE", created_at=0))
        context = customer_state_engine.get_snapshot("c_ent")
        with self.assertRaises(PolicyViolationError) as cm:
            policy_engine.validate("APPLY_DISCOUNT", context, {"amount": -50.0})
        self.assertIn("must be strictly positive", str(cm.exception))

    def test_communication_blocked_during_active_processing(self):
        world.add_customer(Customer(id="c_ent", name="Enterprise Client", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_proc", customer_id="c_ent", amount=1000.0, status=PaymentStatus.AUTHORIZING, created_at=0))
        context = customer_state_engine.get_snapshot("c_ent")
        
        for comm_action in ["SEND_MESSAGE", "SEND_PAYMENT_LINK", "REQUEST_CUSTOMER_ACTION"]:
            with self.assertRaises(PolicyViolationError) as cm:
                policy_engine.validate(comm_action, context, {})
            self.assertIn("actively processing", str(cm.exception))

    def test_communication_allowed_when_no_active_processing(self):
        world.add_customer(Customer(id="c_ent", name="Enterprise Client", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_failed", customer_id="c_ent", amount=1000.0, status=PaymentStatus.FAILED, created_at=0))
        context = customer_state_engine.get_snapshot("c_ent")
        self.assertTrue(policy_engine.validate("SEND_MESSAGE", context, {}))

    def test_malformed_context_rejected_safely(self):
        with self.assertRaises(PolicyViolationError):
            policy_engine.validate("SEND_MESSAGE", {}, {})
        with self.assertRaises(PolicyViolationError):
            policy_engine.validate("SEND_MESSAGE", "invalid_string_context", {})

if __name__ == '__main__':
    unittest.main()
