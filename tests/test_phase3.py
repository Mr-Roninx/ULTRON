import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agent.state_machine import AgentStateMachine, AgentPhase, InvalidAgentStateTransitionError
from backend.agent.circuit_breakers import circuit_breaker, CircuitBreakerTripped
from backend.agent.observation import observer, PredictionError
from memory.episodic import memory_store, EpisodeRecord
from backend.agent.schemas import AgentIntent
from backend.agent.loop import AgentLoop
from simulator.clock import clock
from simulator.world import world
from simulator.models import Customer, Payment, PaymentStatus

class TestPhase3(unittest.TestCase):
    def setUp(self):
        world.reset()
        clock.reset()
        memory_store.memories = []

    def test_state_machine_valid_transitions(self):
        fsm = AgentStateMachine()
        self.assertEqual(fsm.current(), AgentPhase.OBSERVE)
        fsm.transition(AgentPhase.INVESTIGATE)
        fsm.transition(AgentPhase.HYPOTHESIZE)
        fsm.transition(AgentPhase.PLAN)
        fsm.transition(AgentPhase.FEASIBILITY_CHECK)
        fsm.transition(AgentPhase.AUTHORITY_CHECK)
        fsm.transition(AgentPhase.RISK_CHECK)
        fsm.transition(AgentPhase.EXECUTE)
        fsm.transition(AgentPhase.WAIT)
        fsm.transition(AgentPhase.EVALUATE)
        fsm.transition(AgentPhase.LEARN)
        fsm.transition(AgentPhase.COMPLETE)
        self.assertEqual(fsm.current(), AgentPhase.COMPLETE)

    def test_state_machine_invalid_transition(self):
        fsm = AgentStateMachine()
        with self.assertRaises(InvalidAgentStateTransitionError):
            fsm.transition(AgentPhase.EXECUTE)

    def test_circuit_breaker_max_iterations(self):
        with self.assertRaises(CircuitBreakerTripped):
            circuit_breaker.check(51, 0, 0)

    def test_circuit_breaker_max_replans(self):
        with self.assertRaises(CircuitBreakerTripped):
            circuit_breaker.check(5, 6, 0)

    def test_circuit_breaker_identical_failures(self):
        with self.assertRaises(CircuitBreakerTripped):
            circuit_breaker.check(5, 2, 3)

    def test_observation_engine_hard_error(self):
        res = observer.evaluate(expected_value=100.0, observed_value=40.0, actual_status="SETTLED")
        # error = 0.6 > 0.5 (hard threshold)
        self.assertTrue(res["requires_replan"])
        self.assertEqual(res["error_type"], "HARD")

    def test_observation_engine_soft_error(self):
        res = observer.evaluate(expected_value=100.0, observed_value=75.0, actual_status="SETTLED")
        # error = 0.25 > 0.2 (soft threshold) but < 0.5
        self.assertFalse(res["requires_replan"])
        self.assertEqual(res["error_type"], "SOFT")

    def test_observation_engine_state_failure(self):
        res = observer.evaluate(expected_value=100.0, observed_value=0.0, actual_status="FAILED")
        self.assertTrue(res["requires_replan"])
        self.assertEqual(res["error_type"], "STATE_FAILURE")

    def test_episodic_memory_store_retrieve(self):
        record = EpisodeRecord(
            customer_id="c_1",
            failure_type="INSUFFICIENT_FUNDS",
            action_taken="RETRY",
            result="SUCCESS",
            recovery_amount=100.0,
            timestamp=clock.now()
        )
        memory_store.store(record)
        retrieved = memory_store.retrieve("c_1", "INSUFFICIENT_FUNDS")
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0].action_taken, "RETRY")

    def test_agent_intent_validation(self):
        intent = AgentIntent(action_type="WAIT", reasoning="test", expected_yield=0.0, payload={})
        self.assertEqual(intent.action_type, "WAIT")
        with self.assertRaises(ValueError):
            AgentIntent(action_type="INVALID_ACTION", reasoning="test", expected_yield=0.0, payload={})

    def test_agent_loop_execution(self):
        world.add_customer(Customer(id="c_1", name="Test", segment="B2B_ENTERPRISE", created_at=0))
        world.add_payment(Payment(id="p_1", customer_id="c_1", amount=100, status=PaymentStatus.UNKNOWN, created_at=0))
        
        from backend.llm.provider import MockProvider
        intent = AgentIntent(
            action_type="RECONCILE",
            reasoning="Testing loop",
            expected_yield=100.0,
            payload={"payment_id": "p_1"}
        )
        provider = MockProvider([intent])
        loop = AgentLoop("c_1", "m_1", llm_provider=provider)
        
        # Run until complete
        while loop.fsm.current() not in [AgentPhase.COMPLETE, AgentPhase.ESCALATE]:
            loop.tick()
            
        self.assertEqual(loop.fsm.current(), AgentPhase.COMPLETE)
        # Check memory was stored
        mem = memory_store.retrieve("c_1", "UNKNOWN")
        self.assertEqual(len(mem), 1)
        self.assertEqual(mem[0].action_taken, "RECONCILE")

if __name__ == '__main__':
    unittest.main()
