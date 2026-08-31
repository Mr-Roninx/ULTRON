import pytest
from backend.llm.provider import LLMRouter, MockProvider
from backend.agent.schemas import AgentIntent

def test_router_failover_ladder():
    class FailingProvider(MockProvider):
        def generate_intent(self, messages, schemas):
            raise RuntimeError("402 Payment Required: monthly credits depleted")

    primary = FailingProvider()
    fallback = MockProvider([AgentIntent(action_type="RETRY_GATEWAY_A", candidate_actions=["RETRY_GATEWAY_A", "WAIT"], preferred_action="RETRY_GATEWAY_A", reasoning="Local fallback operational", expected_yield=10000.0, payload={})])

    router = LLMRouter(primary=primary, fallback=fallback)
    intent = router.generate_intent([], [])
    assert intent.action_type == "RETRY_GATEWAY_A"
