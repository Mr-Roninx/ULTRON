import pytest
from simulator.clock import clock
from simulator.world import world
from simulator.models import Customer as SimCustomer, Payment as SimPayment, PaymentStatus
from backend.agent.loop import AgentLoop
from backend.agent.schemas import AgentIntent
from backend.llm.provider import MockProvider
from synthetic_payment_universe.observation.observation_builder import universe_observation_api
from synthetic_payment_universe.world.action_api import universe_action_api

def test_ultron_agent_loop_synthetic_universe_integration():
    world.reset()
    universe_observation_api.reset()
    now = 1760000000
    clock.reset(now)

    cust = SimCustomer(id="c_integ_test", name="Integration Client", segment="B2B_ENTERPRISE", created_at=now)
    pmt = SimPayment(id="pmt_integ_test", customer_id=cust.id, amount=24700.0, status=PaymentStatus.FAILED, rail="CARD", gateway_id="GATEWAY_A", failure_code="91", created_at=now)
    world.add_customer(cust)
    world.add_payment(pmt)

    loop = AgentLoop(
        customer_id=cust.id,
        mission_id="msn_integ_test",
        llm_provider=MockProvider([AgentIntent(action_type="WAIT", candidate_actions=["WAIT", "RETRY_GATEWAY_A"], preferred_action="WAIT", reasoning="Transient outage observation", expected_yield=24700.0, payload={})])
    )
    for _ in range(5):
        loop.tick()

    assert loop.chosen_intent is not None
    # Execute action through Universe Action API
    success, res = universe_action_api.execute_action(
        customer_id=cust.id,
        payment_id=pmt.id,
        action_type=loop.chosen_intent.action_type
    )
    assert success is True
    assert res["status"] == "EXECUTED"
