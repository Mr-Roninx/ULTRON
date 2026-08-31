import os
import json
import pytest
from backend.audit.trace_graph import trace_graph_engine
from simulator.clock import clock

def test_trace_graph_export_and_integrity():
    clock.reset(1700000000)
    trace_graph_engine.reset()
    
    trace_graph_engine.start_trace(mission_id="msn_test_integrity", customer_id="c_test")
    trace_graph_engine.add_node(
        mission_id="msn_test_integrity",
        event_type="OBSERVE",
        phase="OBSERVE",
        details={"status": "OK"}
    )
    trace_graph_engine.add_node(
        mission_id="msn_test_integrity",
        event_type="LLM_REASON",
        phase="PLAN",
        llm_invocation_id="inv_1",
        preferred_action="WAIT",
        candidate_actions=["WAIT", "RETRY"],
        deterministic_action="RETRY"
    )

    out_file = "d:/Work Space/Project/Ultron/results/phase16/traces/test_trace_integrity.json"
    res_path = trace_graph_engine.export_trace(mission_id="msn_test_integrity", filepath=out_file)
    
    assert os.path.exists(res_path)
    with open(res_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data["mission_id"] == "msn_test_integrity"
    assert data["total_llm_invocations"] == 1
    assert len(data["nodes"]) == 2
    assert data["nodes"][1]["authority_override"] is True
