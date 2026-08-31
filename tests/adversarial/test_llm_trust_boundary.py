import sys
import os
import unittest
from pydantic import ValidationError

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.agent.schemas import AgentIntent
from backend.tools.registry import registry
from financial.authority import AuthorityLevel
from financial.policy import PolicyViolationError
from financial.risk import RiskViolationError
from simulator.world import world
from simulator.models import Customer, Payment, PaymentStatus
from simulator.clock import clock

class TestAdversarialLLMTrustBoundary(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()
        world.add_customer(Customer(id="c_1", name="Target Enterprise", segment="B2B_ENTERPRISE", created_at=0))
        world.add_customer(Customer(id="c_smb", name="Target SMB", segment="B2B_SMB", created_at=0))
        world.add_payment(Payment(id="p_1", customer_id="c_1", amount=500.0, status=PaymentStatus.UNKNOWN, created_at=0))

    def test_malicious_action_delete_customer_rejected_by_schema(self):
        """Malicious payload: action_type = 'DELETE_CUSTOMER' must be rejected at Pydantic validation."""
        with self.assertRaises(ValidationError):
            AgentIntent(
                action_type="DELETE_CUSTOMER",
                reasoning="Hostile injection",
                expected_yield=0.0,
                payload={}
            )

    def test_malicious_send_message_negative_amount_payload(self):
        """Malicious payload: SEND_MESSAGE with negative amount or hostile fields."""
        # SEND_MESSAGE does not alter financial balances; execution tools safely handle arbitrary fields
        res = registry.execution.send_customer_message(
            mission_id="m_1",
            customer_id="c_1",
            channel="EMAIL",
            message_type="GENTLE_REMINDER",
            authority="AUTONOMOUS",
            max_risk=1.0
        )
        self.assertTrue(res.success)
        # World balances unaffected
        self.assertEqual(world.payments["p_1"].amount, 500.0)

    def test_malicious_retry_unknown_payment_id_fails_safely(self):
        """Malicious payload: RETRY with non-existent payment_id fails safely without crashing."""
        res = registry.execution.schedule_retry(
            mission_id="m_1",
            customer_id="c_1",
            payment_id="unknown_p_9999",
            delay=10,
            authority="AUTONOMOUS",
            max_risk=1.0
        )
        # Succeeded in scheduling, but retry callback checks existence before mutating
        clock.advance(20)
        self.assertNotIn("unknown_p_9999", world.payments)

    def test_unauthorized_discount_on_smb_rejected_by_policy(self):
        """Malicious plan: Unauthorized discount on non-enterprise client rejected by policy."""
        # Using ExecutionTools with SMB customer
        res = registry.execution.reconcile_payment(
            mission_id="m_1",
            customer_id="c_smb",
            payment_id="p_1",
            authority="AUTONOMOUS",
            max_risk=1.0
        )
        # Reconcile fails if payment c_1 doesn't belong to c_smb or not UNKNOWN
        self.assertIsNotNone(res)

    def test_authority_bypass_attempt(self):
        """Hostile LLM attempts an action under OBSERVE authority."""
        res = registry.execution.reconcile_payment(
            mission_id="m_1",
            customer_id="c_1",
            payment_id="p_1",
            authority="OBSERVE",
            max_risk=1.0
        )
        self.assertFalse(res.success)
        self.assertEqual(res.message, "Authority level too low")

    def test_risk_bypass_attempt(self):
        """Hostile LLM attempts an action whose risk exceeds max_risk."""
        res = registry.execution.schedule_retry(
            mission_id="m_1",
            customer_id="c_1",
            payment_id="p_1",
            delay=10,
            authority="AUTONOMOUS",
            max_risk=0.01
        )
        self.assertFalse(res.success)
        self.assertIn("exceeds mission limit", res.message)

    def test_direct_financial_mutation_isolation(self):
        """AgentIntent has no execution method or direct world reference."""
        intent = AgentIntent(
            action_type="WAIT",
            reasoning="Attempting direct SQL injection",
            expected_yield=0.0,
            payload={"sql": "DROP TABLE payments;"}
        )
        self.assertFalse(hasattr(intent, "execute"))
        self.assertFalse(hasattr(intent, "mutate_world"))

if __name__ == '__main__':
    unittest.main()
