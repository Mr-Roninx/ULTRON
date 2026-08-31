import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.models import Customer, Payment, PaymentStatus
from simulator.world import world
from simulator.clock import clock
from backend.agent.schemas import AgentIntent
from evaluator.counterfactual import counterfactual_evaluator
from evaluator.replay import replay_engine
from memory.episodic import memory_store, EpisodeRecord
from backend.agent.loop import AgentLoop
from backend.llm.provider import MockProvider
from backend.agent.state_machine import AgentPhase

class TestPhase5(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()
        memory_store.memories = []
        world.add_customer(Customer(id="c_1", name="Test", segment="B2B_ENTERPRISE", created_at=0))

    def test_evaluator_forks_world_state(self):
        # We can observe that evaluating regret does not alter the original world.
        world.add_payment(Payment(id="p_1", customer_id="c_1", amount=100, status=PaymentStatus.UNKNOWN, created_at=0))
        intent = AgentIntent(action_type="WAIT", reasoning="Test", expected_yield=0.0, payload={})
        
        regret = counterfactual_evaluator.calculate_regret("c_1", intent, max_risk=1.0, authority="AUTONOMOUS")
        
        # Check world wasn't mutated permanently
        self.assertEqual(world.payments["p_1"].status, PaymentStatus.UNKNOWN)
        self.assertIn("regret", regret)
        self.assertIn("best_alternative", regret)

    def test_evaluator_calculates_regret_correctly(self):
        intent = AgentIntent(action_type="WAIT", reasoning="Test", expected_yield=0.0, payload={})
        # If WAIT is chosen, NEV is 0. If there is a better action with positive NEV, regret > 0
        regret = counterfactual_evaluator.calculate_regret("c_1", intent, max_risk=1.0, authority="AUTONOMOUS")
        
        self.assertTrue(regret["regret"] >= 0.0)
        self.assertEqual(regret["chosen_action"], "WAIT")

    def test_evaluator_restores_global_world(self):
        import simulator.world
        original_ptr = simulator.world.world
        
        intent = AgentIntent(action_type="WAIT", reasoning="Test", expected_yield=0.0, payload={})
        counterfactual_evaluator.calculate_regret("c_1", intent, max_risk=1.0, authority="AUTONOMOUS")
        
        # Global pointer should be exactly the same object
        self.assertIs(simulator.world.world, original_ptr)

    def test_replay_engine_processes_memories(self):
        # Insert a historical memory
        memory_store.store(EpisodeRecord(
            customer_id="c_1",
            failure_type="UNKNOWN",
            action_taken="WAIT",
            result="SUCCESS",
            recovery_amount=0.0,
            timestamp=0
        ))
        
        results = replay_engine.run_replay_suite("c_1", max_risk=1.0, authority="AUTONOMOUS")
        self.assertEqual(len(results), 1)
        self.assertIn("evaluation", results[0])
        self.assertIn("regret", results[0]["evaluation"])

    def test_loop_incorporates_evaluation_hook(self):
        world.add_payment(Payment(id="p_1", customer_id="c_1", amount=100, status=PaymentStatus.UNKNOWN, created_at=0))
        
        intent = AgentIntent(action_type="WAIT", reasoning="test", expected_yield=0.0, payload={})
        provider = MockProvider([intent])
        
        loop = AgentLoop("c_1", "m_1", llm_provider=provider)
        
        while loop.fsm.current() not in [AgentPhase.COMPLETE, AgentPhase.ESCALATE]:
            loop.tick()
            
        self.assertEqual(loop.fsm.current(), AgentPhase.COMPLETE)
        # Verify the evaluation hook ran and stored regret in context
        self.assertIn("last_regret_evaluation", loop.context)
        self.assertIn("regret", loop.context["last_regret_evaluation"])

if __name__ == '__main__':
    unittest.main()
