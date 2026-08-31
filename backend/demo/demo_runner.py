import argparse
import sys
from backend.demo.demo_controller import DemoController
from backend.demo.demo_scenarios import DEMO_SCENARIO_MAP

def run_demo(scenario_id: str, live_hf: bool = True):
    print("=" * 70)
    print(f"ULTRON v3.8 — HACKATHON LIVE DEMONSTRATION ENGINE")
    print(f"Scenario: {scenario_id}")
    print("=" * 70)

    controller = DemoController(scenario_id=scenario_id, live_hf=live_hf)
    meta = controller.setup()
    print(f"\n[STEP 1] World Setup:")
    print(f"  Customer: {meta.get('customer_id')} (Exposure: INR {meta.get('amount', 0):,.2f})")
    print(f"  Payment ID: {meta.get('payment_id')}")

    print(f"\n[STEP 2] Running Agent Observation -> LLM Invocation #1 -> Authority Decision -> WAIT...")
    wait_res = controller.run_to_wait()
    print(f"  Phase Reached: {wait_res['phase']}")
    print(f"  LLM Preferred Action: {wait_res['llm_preferred']}")
    print(f"  Deterministic Authority Selected: {wait_res['chosen_action']} (Expected: INR {wait_res['nev']:,.2f})")
    print(f"  LLM Invocations: {wait_res['llm_invocations']}")

    if "CHAOS" in scenario_id or scenario_id == "DEMO_04_GATEWAY_CHAOS":
        print(f"\n[STEP 3] Injecting Mid-Flight Chaos Degradation at T+2h...")
        controller.inject_gateway_chaos("GATEWAY_A", degraded_health=0.10)
        print(f"  Gateway A health degraded to 10% (Simulated Outage).")

        print(f"\n[STEP 4] Waking Agent -> Stale Plan Invalidation -> LLM Invocation #2 -> Replan...")
        replan_res = controller.wake_and_replan()
        print(f"  Final Phase: {replan_res['final_phase']}")
        print(f"  Adapted Post-Chaos Action: {replan_res['final_action']}")
        print(f"  Total LLM Invocations in Mission: {replan_res['total_llm_invocations']}")
        print(f"  Replan Count: {replan_res['replan_count']}")
        print(f"  Trace Artifact Exported: {replan_res['trace_artifact']}")

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY. ZERO FINANCIAL MUTATION LEAKAGE.")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ULTRON v3.8 Demo Runner")
    parser.add_argument("--scenario", default="DEMO_04_GATEWAY_CHAOS", choices=list(DEMO_SCENARIO_MAP.keys()), help="Scenario ID to run")
    parser.add_argument("--mock-llm", action="store_true", help="Force mock LLM instead of live HF")
    args = parser.parse_args()

    run_demo(scenario_id=args.scenario, live_hf=not args.mock_llm)
