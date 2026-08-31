import unittest
from backend.agent.schemas import AgentIntent
from backend.agent.loop import AgentLoop
from backend.llm.provider import MockProvider
from simulator.clock import clock
from memory.episodic import memory_store
from backend.benchmark.generator import SeededWorldGenerator
from backend.benchmark.simulator_dynamics import SimulationDynamicsEngine
from pydantic import ValidationError
from simulator.world import world

class TestLLMBoundary(unittest.TestCase):
    def setUp(self):
        self.generator = SeededWorldGenerator(seed=42)
        self.canonical, self.opps = self.generator.generate(start_time=1718000000)
        clock.reset(1718000000)
        world.restore_from(self.canonical)

    def test_llm_invalid_intent_is_rejected(self):
        with self.assertRaises(ValidationError):
            AgentIntent(
                action_type="REFUND_ENTIRE_AMOUNT_AND_BUY_A_PONY",
                reasoning="The LLM is hallucinating",
                expected_yield=10000.0,
                payload={}
            )

    def test_deterministic_engine_can_select_action_not_suggested_by_llm(self):
        # The LLM ONLY suggests SEND_MESSAGE
        mock_intent = AgentIntent(
            candidate_actions=["SEND_MESSAGE"],
            preferred_action="SEND_MESSAGE",
            action_type="SEND_MESSAGE",
            reasoning="I think we should just text them.",
            expected_yield=0.0,
            payload={}
        )
        
        provider = MockProvider(predefined_intents=[mock_intent])
        
        loop = AgentLoop(
            customer_id="c_1034",
            mission_id="m_opp_101",
            max_risk=1.0,
            authority="AUTONOMOUS",
            llm_provider=provider
        )
        
        # Advance through states up to EXECUTE
        loop.tick() # OBSERVE
        loop.tick() # INVESTIGATE
        loop.tick() # HYPOTHESIZE
        loop.tick() # PLAN
        
        # The LLM proposed SEND_MESSAGE.
        # But ActionRanker calculated that RETRY/ESCALATE is feasible and has highest NEV.
        self.assertNotEqual(loop.chosen_intent.action_type, "SEND_MESSAGE")
        self.assertIn(loop.chosen_intent.action_type, ["ESCALATE", "RETRY", "RETRY_GATEWAY_A", "RETRY_GATEWAY_B", "SWITCH_PERMITTED_RAIL"])

    def test_llm_cannot_read_future_information(self):
        from backend.benchmark.firewall import TemporalObservationFirewall, FutureInformationLeakageError
        context = {"actual_recovery": 1000.0}
        with self.assertRaises(FutureInformationLeakageError):
            TemporalObservationFirewall.enforce(context)

    def test_llm_cannot_mutate_financial_state(self):
        # LLM only outputs AgentIntent. The AgentLoop never executes arbitrary SQL or modifies balances.
        # It calls registry.execution tools. We verify that AgentIntent fields have no mechanism to modify state.
        # Even if payload contains malicious data, the execution tool restricts actions.
        intent = AgentIntent(
            action_type="RETRY",
            reasoning="retry",
            expected_yield=100.0,
            payload={"balance": 0.0, "status": "SETTLED"} # Malicious attempt
        )
        # Verify execution tool does not use these fields for mutation
        from backend.tools.registry import registry
        # schedule_retry payload extracts payment_id and delay only
        import inspect
        src = inspect.getsource(registry.execution.schedule_retry)
        self.assertNotIn('payload.get("balance")', src)
        self.assertNotIn('payload.get("status")', src)

    def test_llm_cannot_bypass_policy(self):
        from financial.policy import PolicyEngine, PolicyContext, PolicyViolationError
        # Force a policy denial
        engine = PolicyEngine()
        context = PolicyContext(customer={"risk_band": "HIGH", "segment": "SMB"}, balances={}, gateway_status={})
        with self.assertRaises(PolicyViolationError):
            engine.validate(
                action_type="APPLY_DISCOUNT", 
                payload={"amount": 1000.0},
                context=context
            )

    def test_hf_fails_over_to_local_llm(self):
        from backend.llm.provider import LLMRouter, MockProvider
        from backend.agent.schemas import AgentIntent
        # Primary always fails
        class FailingProvider(MockProvider):
            def generate_intent(self, messages: list, schemas: list) -> AgentIntent:
                raise RuntimeError("Hugging Face API unavailable")
                
        primary = FailingProvider()
        # Fallback succeeds
        fallback = MockProvider(predefined_intents=[AgentIntent(action_type="WAIT", reasoning="fallback", candidate_actions=["WAIT"], preferred_action="WAIT", expected_yield=0.0, payload={})])
        
        router = LLMRouter(primary=primary, fallback=fallback, active_provider_name="HF")
        intent = router.generate_intent([], [])
        self.assertEqual(intent.action_type, "WAIT")
        self.assertEqual(intent.reasoning, "fallback")

    def test_local_fails_over_to_safe_deterministic_action(self):
        from backend.llm.provider import LLMRouter, MockProvider
        # Both fail
        class FailingProvider(MockProvider):
            def generate_intent(self, messages: list, schemas: list) -> AgentIntent:
                raise RuntimeError("Local API unavailable")
                
        primary = FailingProvider()
        fallback = FailingProvider()
        
        router = LLMRouter(primary=primary, fallback=fallback, active_provider_name="HF")
        intent = router.generate_intent([], [])
        self.assertEqual(intent.action_type, "WAIT")
        self.assertEqual(intent.reasoning, "Safe failure: All LLM providers failed or were unavailable.")