import pytest
from simulator.world import world
from simulator.clock import clock
from simulator.models import Customer, Payment, PaymentStatus
from backend.mission.mission_builder import mission_registry
from backend.agent.loop import AgentLoop
from backend.agent.schemas import AgentIntent
from backend.llm.provider import MockProvider

def test_phase18_authority_invariant():
    world.reset()
    mission_registry.reset()
    clock.reset(1760000000)
    
    cust = Customer(id="c_auth_p18", name="Authority Test Corp", segment="B2B_ENTERPRISE", created_at=clock.now())
    pmt = Payment(id="pmt_auth_p18", customer_id=cust.id, amount=24700.0, status=PaymentStatus.FAILED, rail="CARD", gateway_id="GATEWAY_A", failure_code="91", created_at=clock.now())
    world.add_customer(cust)
    world.add_payment(pmt)

    # LLM preferred WAIT, but deterministic NEV argmax enforces RETRY
    loop = AgentLoop(
        customer_id=cust.id,
        mission_id="msn_auth_p18",
        llm_provider=MockProvider([AgentIntent(action_type="WAIT", candidate_actions=["WAIT", "RETRY_GATEWAY_A"], preferred_action="WAIT", reasoning="Prefer wait", expected_yield=0.0, payload={})])
    )
    for _ in range(5):
        loop.tick()

    assert loop.chosen_intent.action_type in ["RETRY", "RETRY_GATEWAY_A"]
    assert loop.chosen_intent.action_type != "WAIT"
