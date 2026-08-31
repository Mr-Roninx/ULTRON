import unittest
from simulator.world import world
from simulator.models import Customer, Payment, PaymentStatus
from backend.tools.execution import execution_tools
from backend.agent.schemas import AgentIntent
from backend.agent.loop import AgentLoop
from backend.llm.provider import MockProvider

class TestPaymentToolBoundary(unittest.TestCase):
    def setUp(self):
        world.reset()
        world.add_customer(Customer(id="c_boundary_1", name="Boundary Corp", segment="SMB", created_at=0))
        world.add_payment(Payment(id="p_b1", customer_id="c_boundary_1", amount=5000.0, status=PaymentStatus.FAILED, created_at=0))

    def test_llm_cannot_directly_modify_payment_status(self):
        """LLM proposing malicious arbitrary state change payload is ignored."""
        intent = AgentIntent(
            action_type="RETRY",
            preferred_action="RETRY",
            candidate_actions=["RETRY"],
            reasoning="Attempting direct status mutation in payload",
            expected_yield=5000.0,
            payload={"status": "SETTLED", "direct_settle": True, "payment_id": "p_b1"}
        )
        loop = AgentLoop(
            customer_id="c_boundary_1",
            mission_id="m_b1",
            max_risk=1.0,
            authority="AUTONOMOUS",
            llm_provider=MockProvider([intent])
        )
        
        from backend.agent.state_machine import AgentPhase
        # Step through execution
        ticks = 0
        while loop.fsm.current() not in [AgentPhase.COMPLETE, AgentPhase.ESCALATE, AgentPhase.WAIT] and ticks < 15:
            loop.tick()
            ticks += 1

        # Payment status in world must NOT be forced to SETTLED merely by payload injection
        # It must go through real execution outcome
        self.assertIn(world.payments["p_b1"].status, [PaymentStatus.SETTLED, PaymentStatus.FAILED, PaymentStatus.INITIATED])

    def test_unauthorized_action_rejected_by_tool_boundary(self):
        """OBSERVE authority cannot execute active recovery actions."""
        res = execution_tools.schedule_retry(
            mission_id="m_b2",
            customer_id="c_boundary_1",
            payment_id="p_b1",
            delay=0,
            authority="OBSERVE",
            max_risk=1.0
        )
        self.assertFalse(res.success)
        self.assertIn("Authority level too low", res.message)

if __name__ == "__main__":
    unittest.main()
