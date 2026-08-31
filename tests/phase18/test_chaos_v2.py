import pytest
from simulator.clock import clock
from backend.production_sim.chaos_v2 import chaos_engine_v2

def test_chaos_engine_v2_evaluation():
    chaos_engine_v2.reset()
    clock.reset(1760000000)
    
    chaos_engine_v2.inject_gateway_degradation("GATEWAY_A", health=0.10)
    eval_res = chaos_engine_v2.evaluate_chaos_response(agent_replan_count=1, initial_plan_valid=False)
    
    assert eval_res["chaos_detected"] is True
    assert eval_res["replan_required"] is True
    assert eval_res["replan_triggered"] is True
    assert eval_res["successful_replan"] is True
