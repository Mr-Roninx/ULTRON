import os
import json
import time
from typing import Dict, Any, List, Optional
from simulator.world import world
from simulator.clock import clock
from simulator.models import Customer, Payment, PaymentStatus
from memory.episodic import memory_store
from backend.payment_intelligence.rail_health import rail_health_engine
from backend.mission.mission_builder import mission_registry
from backend.agent.loop import AgentLoop
from backend.agent.schemas import AgentIntent
from backend.agent.state_machine import AgentPhase
from backend.llm.provider import LLMRouter, HuggingFaceProvider, MockProvider
from backend.llm.performance import llm_performance_controller, LatencySLA
from backend.audit.trace_graph import trace_graph_engine

RESULTS_DIR = "d:/Work Space/Project/Ultron/results/phase16"
os.makedirs(RESULTS_DIR, exist_ok=True)

def setup_canonical_ananya_scenario() -> str:
    """Sets up the canonical Ananya Textiles enterprise failure scenario."""
    world.reset()
    mission_registry.reset()
    clock.reset(1700000000)
    memory_store.clear()
    rail_health_engine.reset()

    cust = Customer(
        id="c_ananya_enterprise",
        name="Ananya Textiles Pvt Ltd",
        segment="B2B_ENTERPRISE",
        created_at=clock.now()
    )
    world.add_customer(cust)

    pmt = Payment(
        id="pmt_ananya_24700",
        customer_id=cust.id,
        amount=24700.0,
        status=PaymentStatus.FAILED,
        rail="CARD",
        gateway_id="GATEWAY_A",
        created_at=clock.now(),
        failure_code="91",
        metadata={"failure_reason": "ISSUER_UNAVAILABLE"}
    )
    world.add_payment(pmt)
    return cust.id

def execute_llm_performance_benchmark(n_requests: int = 15) -> Dict[str, Any]:
    """
    Executes live latency and throughput benchmark across 10-30 requests.
    Measures P50, P95, mean latency, fallback rates, and SLA adherence.
    """
    llm_performance_controller.reset()
    hf_token = os.environ.get("HF_TOKEN", "")
    hf_model = os.environ.get("HF_MODEL", "Qwen/Qwen3.8-2.4T-A95B:novita")

    provider = HuggingFaceProvider(api_token=hf_token, model_name=hf_model, timeout_seconds=6.0) if hf_token else MockProvider([
        AgentIntent(action_type="WAIT", candidate_actions=["WAIT", "RETRY_GATEWAY_A"], preferred_action="WAIT", reasoning="Mock benchmark latency test.", expected_yield=24700.0, payload={})
    ])

    sample_messages = [
        {"role": "system", "content": "You are ULTRON payment intelligence engine."},
        {"role": "user", "content": "Payment failed with ISO 91 ISSUER_UNAVAILABLE. Propose candidate actions."}
    ]

    benchmark_records = []
    for i in range(n_requests):
        t0 = time.time()
        try:
            intent = provider.generate_intent(sample_messages, [])
            lat = (time.time() - t0) * 1000.0
            benchmark_records.append({
                "iteration": i + 1,
                "latency_ms": round(lat, 2),
                "status": "SUCCESS",
                "action_type": intent.action_type,
                "provider": "HuggingFace" if hf_token else "MockProvider"
            })
        except Exception as e:
            lat = (time.time() - t0) * 1000.0
            benchmark_records.append({
                "iteration": i + 1,
                "latency_ms": round(lat, 2),
                "status": "FALLBACK",
                "error": str(e)[:100],
                "provider": "Fallback"
            })

    stats = llm_performance_controller.get_statistics()
    output = {
        "benchmark": "LLM_PERFORMANCE_BENCHMARK",
        "provider": "HuggingFace" if hf_token else "MockProvider",
        "model": hf_model if hf_token else "MockQwen",
        "total_requests": n_requests,
        "statistics": stats,
        "records": benchmark_records
    }

    with open(os.path.join(RESULTS_DIR, "llm_performance.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    return output

def execute_chaos_replanning_experiment() -> Dict[str, Any]:
    """
    Executes the Canonical Golden Demo Chaos Test:
    T0: Failure -> LLM Invocation #1 -> Plan -> Execute RETRY -> Wait
    T+2h: Gateway A degraded -> Wake -> Replan -> LLM Invocation #2 -> Alternate Action -> Execute -> Learn -> Memory
    """
    cust_id = setup_canonical_ananya_scenario()

    # Step 1: Initial Plan at T+0 (Gateway A Healthy)
    loop = AgentLoop(customer_id=cust_id, mission_id="msn_golden_demo")
    
    # Progress through OBSERVE -> INVESTIGATE -> HYPOTHESIZE -> PLAN -> FEASIBILITY -> AUTHORITY -> RISK -> EXECUTE -> WAIT
    for _ in range(8):
        loop.tick()

    initial_action = loop.chosen_intent.action_type if loop.chosen_intent else "RETRY_GATEWAY_A"
    initial_invocations = loop.llm_invocation_count

    # Step 2: At T+2h, inject chaos degradation on Gateway A
    clock.advance(7200)
    rail_health_engine.update_gateway_health("GATEWAY_A", success_probability=0.10, latency_ms=4500.0)

    # Step 3: Wake agent and trigger EVALUATE -> REPLAN
    loop.wake()
    phase_after_wake = loop.fsm.current()
    loop.tick() # EVALUATE detects degradation -> transitions to REPLAN
    replan_triggered = (loop.fsm.current() == AgentPhase.REPLAN)

    # Step 4: Execute REPLAN -> INVESTIGATE -> HYPOTHESIZE -> PLAN (LLM Invocation #2) -> EXECUTE -> LEARN -> COMPLETE
    for _ in range(10):
        if loop.fsm.current() in [AgentPhase.COMPLETE, AgentPhase.ESCALATE]:
            break
        loop.tick()

    new_action = loop.chosen_intent.action_type if loop.chosen_intent else "UNKNOWN"
    action_adapted = (new_action != initial_action)
    total_invocations = loop.llm_invocation_count

    # Export Golden Demo Trace
    trace_path = os.path.join(RESULTS_DIR, "golden_demo_trace.json")
    trace_graph_engine.export_trace(mission_id="msn_golden_demo", filepath=trace_path)

    res = {
        "experiment": "REAL_LLM_CHAOS_REPLANNING",
        "scenario": "Ananya Textiles (₹24,700, ISO 91)",
        "t0_initial_action": initial_action,
        "initial_llm_invocations": initial_invocations,
        "chaos_injected_at_sim_time": clock.now(),
        "phase_after_wake": phase_after_wake.value,
        "replan_triggered": replan_triggered,
        "post_chaos_adapted_action": new_action,
        "action_adapted": action_adapted,
        "total_llm_invocations": total_invocations,
        "replan_count": loop.replan_count,
        "trace_artifact": trace_path,
        "verdict": "PROVEN" if (replan_triggered and action_adapted and total_invocations >= 2) else "PARTIAL"
    }

    with open(os.path.join(RESULTS_DIR, "chaos_replanning.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)

    return res

if __name__ == "__main__":
    p_res = execute_llm_performance_benchmark(10)
    print("LLM Performance Benchmark Complete.")
    c_res = execute_chaos_replanning_experiment()
    print(f"Chaos Replanning Test Complete: Verdict = {c_res['verdict']}")
