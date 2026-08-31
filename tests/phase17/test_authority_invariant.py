import pytest
from simulator.world import world
from simulator.clock import clock
from simulator.models import Customer, Payment, PaymentStatus
from backend.mission.mission_builder import mission_registry
from backend.agent.loop import AgentLoop
from backend.agent.schemas import AgentIntent
from backend.llm.provider import MockProvider

def test_authority_invariant_strict_override():
    world.reset()
    mission_registry.reset()
    clock.reset(1750000000)
    
    cust = Customer(id="c_auth_test", name="Auth Test Corp", segment="B2B_ENTERPRISE", created_at=clock.now())
    pmt = Payment(id="pmt_auth_test", customer_id="c_auth_test", amount=24700.0, status=PaymentStatus.FAILED, rail="CARD", gateway_id="GATEWAY_A", failure_code="91", created_at=clock.now())
    world.add_customer(cust)
    world.add_payment(pmt)

    # LLM preferred is WAIT, but NEV should choose RETRY_GATEWAY_A
    provider = MockProvider([
        AgentIntent(action_type="WAIT", candidate_actions=["WAIT", "RETRY_GATEWAY_A"], preferred_action="WAIT", reasoning="Prefer waiting", expected_yield=0.0, payload={})
    ])

    loop = AgentLoop(customer_id="c_auth_test", mission_id="msn_auth_inv_17", llm_provider=provider)
    for _ in range(5):
        loop.tick()

    assert loop.chosen_intent.action_type in ["RETRY", "RETRY_GATEWAY_A"]
    assert loop.chosen_intent.action_type != "WAIT"
