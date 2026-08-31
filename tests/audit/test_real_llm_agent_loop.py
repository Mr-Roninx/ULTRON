import pytest
from backend.audit.live_llm_trace import setup_canonical_ananya_scenario
from backend.agent.loop import AgentLoop
from backend.agent.state_machine import AgentPhase
from backend.llm.provider import MockProvider, HuggingFaceProvider
from backend.agent.schemas import AgentIntent
from simulator.clock import clock
from memory.episodic import memory_store

def test_canonical_agent_loop_traversal():
    cust_id = setup_canonical_ananya_scenario()

    mock_llm = MockProvider([
        AgentIntent(
            action_type="WAIT",
            candidate_actions=["WAIT", "RETRY_GATEWAY_A", "SEND_PAYMENT_LINK"],
            preferred_action="WAIT",
            reasoning="Backoff recommended for issuer unavailable.",
            expected_yield=24700.0,
            payload={}
        )
    ])

    loop = AgentLoop(
        customer_id=cust_id,
        mission_id="msn_test_canonical",
        authority="AUTONOMOUS",
        llm_provider=mock_llm
    )

    phases = []
    for _ in range(20):
        current_phase = loop.fsm.current()
        phases.append(current_phase.value)

        if current_phase == AgentPhase.WAIT:
            clock.advance(3600)
            loop.wake()

        next_phase = loop.tick()
        if next_phase in [AgentPhase.COMPLETE, AgentPhase.ESCALATE]:
            phases.append(next_phase.value)
            break

    # Verify key FSM phases executed
    assert "OBSERVE" in phases
    assert "INVESTIGATE" in phases
    assert "HYPOTHESIZE" in phases
    assert "PLAN" in phases
    assert "FEASIBILITY_CHECK" in phases
    assert "AUTHORITY_CHECK" in phases
    assert "RISK_CHECK" in phases
    assert "EXECUTE" in phases
    assert "LEARN" in phases or "COMPLETE" in phases

    # Verify episodic memory stored
    episodes = memory_store.get_episodes(cust_id)
    assert len(episodes) >= 1
    assert episodes[0].expected_value > 0.0
