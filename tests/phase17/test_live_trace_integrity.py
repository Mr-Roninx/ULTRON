import pytest
from backend.audit.trace_graph import trace_graph_engine

def test_trace_graph_node_metadata():
    trace_graph_engine.reset()
    trace_graph_engine.start_trace(mission_id="msn_trace_test", customer_id="c_trace_test")
    
    node = trace_graph_engine.add_node(
        mission_id="msn_trace_test",
        event_type="LLM_REASON",
        phase="PLAN",
        llm_invocation_id="inv_12345",
        provider="HuggingFace",
        model="Qwen3.8-2.4T",
        latency_ms=450.2,
        preferred_action="WAIT",
        candidate_actions=["WAIT", "RETRY"],
        deterministic_action="RETRY"
    )
    
    assert node.llm_invocation_id == "inv_12345"
    assert node.provider == "HuggingFace"
    assert node.latency_ms == 450.2
    assert node.authority_override is True
