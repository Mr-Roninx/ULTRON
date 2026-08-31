import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from simulator.models import Customer, Payment, PaymentStatus
from simulator.world import world
from simulator.clock import clock
from backend.agent.schemas import AgentIntent
from backend.agent.state_machine import AgentStateMachine, AgentPhase, InvalidAgentStateTransitionError
from backend.agent.loop import AgentLoop
from backend.llm.provider import MockProvider
from memory.episodic import memory_store

class TestAdversarialCoreAgentLoop(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()
        memory_store.memories.clear()

    def test_full_13_state_sequence_execution(self):
        """Verify the agent traverses through the strict 13-state lifecycle."""
        world.add_customer(Customer(id="c_1001", name="Alpha Corp", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_1001", customer_id="c_1001", amount=500.0, status=PaymentStatus.UNKNOWN, created_at=0))
        
        intent = AgentIntent(
            action_type="RECONCILE",
            reasoning="Reconciling unknown payment",
            expected_yield=500.0,
            payload={"payment_id": "p_1001"}
        )
        provider = MockProvider([intent])
        loop = AgentLoop(customer_id="c_1001", mission_id="m_adv_1", max_risk=1.0, authority="AUTONOMOUS", llm_provider=provider)

        states_observed = [loop.fsm.current()]
        
        while loop.fsm.current() not in [AgentPhase.COMPLETE, AgentPhase.ESCALATE]:
            loop.tick()
            states_observed.append(loop.fsm.current())

        # Expected path: OBSERVE -> INVESTIGATE -> HYPOTHESIZE -> PLAN -> FEASIBILITY_CHECK -> AUTHORITY_CHECK -> RISK_CHECK -> EXECUTE -> WAIT -> EVALUATE -> LEARN -> COMPLETE
        expected_path = [
            AgentPhase.OBSERVE,
            AgentPhase.INVESTIGATE,
            AgentPhase.HYPOTHESIZE,
            AgentPhase.PLAN,
            AgentPhase.FEASIBILITY_CHECK,
            AgentPhase.AUTHORITY_CHECK,
            AgentPhase.RISK_CHECK,
            AgentPhase.EXECUTE,
            AgentPhase.WAIT,
            AgentPhase.EVALUATE,
            AgentPhase.LEARN,
            AgentPhase.COMPLETE
        ]
        self.assertEqual(states_observed, expected_path)
        self.assertEqual(world.payments["p_1001"].status, PaymentStatus.FAILED)

    def test_rejection_of_invalid_state_skips(self):
        """Hostile attempt to skip from PLAN directly to EXECUTE without Authority/Risk checks."""
        fsm = AgentStateMachine(initial=AgentPhase.PLAN)
        with self.assertRaises(InvalidAgentStateTransitionError):
            fsm.transition(AgentPhase.EXECUTE)

    def test_rejection_of_infeasible_intent_triggers_replan(self):
        """If the LLM outputs an infeasible action, the loop MUST branch to REPLAN."""
        world.add_customer(Customer(id="c_1001", name="Alpha Corp", segment="B2B_ENTERPRISE", created_at=0))
        
        # REFUND_PAYMENT has base risk 0.80. If max_risk is 0.10, it is infeasible.
        intent = AgentIntent(
            action_type="REFUND_PAYMENT",
            reasoning="Attempting high risk refund",
            expected_yield=0.0,
            payload={"payment_id": "p_1"}
        )
        provider = MockProvider([intent, AgentIntent(action_type="WAIT", reasoning="Wait fallback", expected_yield=0.0, payload={})])
        loop = AgentLoop(customer_id="c_1001", mission_id="m_adv_2", max_risk=0.10, authority="AUTONOMOUS", llm_provider=provider)

        # Step to PLAN
        while loop.fsm.current() != AgentPhase.PLAN:
            loop.tick()
            
        loop.tick() # PLAN -> FEASIBILITY_CHECK
        self.assertEqual(loop.fsm.current(), AgentPhase.FEASIBILITY_CHECK)
        
        loop.tick() # Infeasible! Should transition to REPLAN
        self.assertEqual(loop.fsm.current(), AgentPhase.REPLAN)

    def test_world_state_mutation_on_execution(self):
        """Execution MUST modify actual world state, not just local variables."""
        world.add_customer(Customer(id="c_1001", name="Alpha Corp", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_1001", customer_id="c_1001", amount=1200.0, status=PaymentStatus.UNKNOWN, created_at=0))
        
        intent = AgentIntent(
            action_type="RECONCILE",
            reasoning="Reconciling payment",
            expected_yield=1200.0,
            payload={"payment_id": "p_1001"}
        )
        loop = AgentLoop(customer_id="c_1001", mission_id="m_adv_3", max_risk=1.0, authority="AUTONOMOUS", llm_provider=MockProvider([intent]))
        
        while loop.fsm.current() not in [AgentPhase.COMPLETE, AgentPhase.ESCALATE]:
            loop.tick()
            
        self.assertEqual(world.payments["p_1001"].status, PaymentStatus.FAILED)
        self.assertTrue(any(a.action_type == "RECONCILE" for a in world.recovery_actions.values()))

if __name__ == '__main__':
    unittest.main()
