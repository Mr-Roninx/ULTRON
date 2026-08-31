import pytest
from backend.evidence.llm_performance import setup_canonical_ananya_scenario
from backend.agent.loop import AgentLoop
from backend.agent.schemas import AgentIntent
from backend.llm.provider import MockProvider

def test_final_authority_invariant_llm_preferred_overridden_by_nev():
    cust_id = setup_canonical_ananya_scenario()
    
    # LLM explicitly prefers WAIT, but RETRY_GATEWAY_A has much higher NEV
    mock_llm = MockProvider([
        AgentIntent(
            action_type="WAIT",
            candidate_actions=["WAIT", "RETRY_GATEWAY_A", "SEND_PAYMENT_LINK"],
            preferred_action="WAIT",
            reasoning="LLM suggests waiting.",
            expected_yield=24700.0,
            payload={}
        )
    ])

    loop = AgentLoop(customer_id=cust_id, mission_id="msn_test_authority_invariant", llm_provider=mock_llm)
    
    # Progress through PLAN
    for _ in range(5):
        loop.tick()

    # Deterministic authority must override LLM preference to choose highest NEV action (RETRY)
    assert loop.chosen_intent.preferred_action == "WAIT"
    assert loop.chosen_intent.action_type.startswith("RETRY")
    assert loop.chosen_intent.action_type != "WAIT"
    assert loop.chosen_intent.expected_yield > 0.0
