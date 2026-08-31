import sys
import os
import unittest
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from simulator.models import Customer, Payment, PaymentStatus
from simulator.world import world
from simulator.clock import clock
from backend.llm.context import context_manager
from backend.tools.registry import registry
from backend.agent.loop import AgentLoop
from backend.llm.provider import MockProvider
from evaluator.counterfactual import counterfactual_evaluator

class TestAdversarialFutureInformationLeakage(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()

    def test_no_future_or_counterfactual_leakage_in_context_snapshot(self):
        """Hostile inspection of all context fields passed to LLM."""
        world.add_customer(Customer(id="c_1001", name="Beta Ltd", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_1001", customer_id="c_1001", amount=1500.0, status=PaymentStatus.UNKNOWN, created_at=0))

        context = registry.investigation.get_customer_context("c_1001")
        state_str = context_manager.format_state(context, ["RECONCILE", "WAIT"])

        # Forbidden keys that must NEVER appear in agent context before action resolution
        forbidden_keywords = [
            "control_outcome",
            "treatment_outcome",
            "incremental_recovery",
            "actual_recovery",
            "future_status",
            "ground_truth_outcome",
            "hidden_evaluator_state",
            "counterfactual_branch"
        ]

        for kw in forbidden_keywords:
            self.assertNotIn(kw, state_str, f"Critical leakage detected: '{kw}' was found in agent context!")

    def test_evaluator_state_cannot_be_injected_into_observation(self):
        """Ensure evaluator results are not leaked into the observation context."""
        world.add_customer(Customer(id="c_1001", name="Beta Ltd", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_1001", customer_id="c_1001", amount=1500.0, status=PaymentStatus.UNKNOWN, created_at=0))
        
        loop = AgentLoop(customer_id="c_1001", mission_id="m_leak_1")
        # Step through OBSERVE and INVESTIGATE
        loop.tick() # OBSERVE
        loop.tick() # INVESTIGATE
        
        # Verify loop context does not contain future/evaluator outcomes
        context_json = json.dumps(loop.context, default=str)
        self.assertNotIn("control_outcome", context_json)
        self.assertNotIn("treatment_outcome", context_json)
        self.assertNotIn("actual_future_state", context_json)

    def test_tools_cannot_query_future_clock_state(self):
        """Tools should only read state at the current virtual clock timestamp."""
        world.add_customer(Customer(id="c_1001", name="Beta Ltd", segment="B2B_ENTERPRISE", created_at=0))
        
        # Schedule future event at t=100
        future_executed = False
        def _future_event():
            nonlocal future_executed
            future_executed = True
        clock.schedule(100, _future_event)

        # Current time is 0
        self.assertEqual(clock.now(), 0)
        
        # Investigation tool snapshot should not reflect future scheduled changes
        context = registry.investigation.get_customer_context("c_1001")
        self.assertFalse(future_executed)

if __name__ == '__main__':
    unittest.main()
