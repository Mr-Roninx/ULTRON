import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.agent.circuit_breakers import CircuitBreaker, CircuitBreakerTripped
from backend.agent.loop import AgentLoop
from backend.llm.provider import MockProvider
from backend.agent.schemas import AgentIntent
from backend.agent.state_machine import AgentPhase
from simulator.world import world
from simulator.models import Customer, Payment, PaymentStatus
from simulator.clock import clock

class TestAdversarialAgentBounds(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()

    def test_circuit_breaker_max_steps_exceeded(self):
        """Exceeding MAX_STEPS (12) must trip CircuitBreakerTripped."""
        cb = CircuitBreaker(max_iterations=12, max_replans=5, max_identical_failures=2)
        with self.assertRaises(CircuitBreakerTripped):
            cb.check(iteration_count=12, replan_count=0, identical_failures=0)

    def test_circuit_breaker_max_replans_exceeded(self):
        """Exceeding MAX_REPLANS (5) must trip CircuitBreakerTripped."""
        cb = CircuitBreaker(max_iterations=12, max_replans=5, max_identical_failures=2)
        with self.assertRaises(CircuitBreakerTripped):
            cb.check(iteration_count=5, replan_count=5, identical_failures=0)

    def test_circuit_breaker_max_identical_failures_exceeded(self):
        """Exceeding MAX_IDENTICAL_FAILURES (2) must trip CircuitBreakerTripped."""
        cb = CircuitBreaker(max_iterations=12, max_replans=5, max_identical_failures=2)
        with self.assertRaises(CircuitBreakerTripped):
            cb.check(iteration_count=5, replan_count=1, identical_failures=2)

    def test_agent_loop_infinite_replan_protection(self):
        """Hostile scenario: LLM continuously emits infeasible intents to force endless replan loops."""
        world.add_customer(Customer(id="c_1", name="Alpha", segment="B2B_SMB", created_at=0))
        
        # Continuously provide an infeasible intent (REFUND_PAYMENT has risk 0.80 > 0.05)
        bad_intent = AgentIntent(action_type="REFUND_PAYMENT", reasoning="Loop trap", expected_yield=0.0, payload={"payment_id": "p_1"})
        infinite_provider = MockProvider([bad_intent] * 30)

        loop = AgentLoop(customer_id="c_1", mission_id="m_loop_trap", max_risk=0.05, authority="AUTONOMOUS", llm_provider=infinite_provider)

        # Loop must trip circuit breaker and terminate, never hang infinitely
        tripped = False
        try:
            for _ in range(50):
                loop.tick()
        except CircuitBreakerTripped:
            tripped = True

        self.assertTrue(tripped, "Agent loop failed to terminate under endless replanning attack!")

if __name__ == '__main__':
    unittest.main()
