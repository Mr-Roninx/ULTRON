import pytest
from backend.demo.demo_controller import DemoController

def test_demo_04_gateway_chaos_end_to_end():
    controller = DemoController(scenario_id="DEMO_04_GATEWAY_CHAOS", live_hf=False)
    meta = controller.setup()
    
    assert meta["scenario_id"] == "DEMO_04_GATEWAY_CHAOS"
    assert meta["amount"] == 24700.0

    wait_res = controller.run_to_wait()
    assert wait_res["phase"] == "WAIT"
    assert wait_res["llm_invocations"] == 1

    controller.inject_gateway_chaos("GATEWAY_A", degraded_health=0.10)
    replan_res = controller.wake_and_replan()
    
    assert replan_res["final_phase"] in ["COMPLETE", "LEARN"]
    assert replan_res["total_llm_invocations"] == 2
    assert replan_res["replan_count"] >= 1
