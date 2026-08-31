import time
import statistics
from fastapi.testclient import TestClient
from backend.main import app
from simulator.world import world
from simulator.models import Payment, PaymentStatus
from simulator.clock import clock
from simulator.seed import seed_ananya_textiles
from backend.agent.schemas import AgentIntent
from backend.agent.loop import AgentLoop
from backend.llm.provider import MockProvider
from evaluator.counterfactual import counterfactual_evaluator
from evaluator.replay import replay_engine
from memory.episodic import memory_store, EpisodeRecord

def run_performance_benchmarks():
    results = {}

    # 1. Startup Time (Module import & FastAPI app instantiation)
    start = time.perf_counter()
    from backend.main import app as benchmark_app
    client = TestClient(benchmark_app)
    results["startup_time_ms"] = (time.perf_counter() - start) * 1000.0

    # 2. Dataset Generation (seed_ananya_textiles)
    times = []
    for _ in range(10):
        world.reset()
        t0 = time.perf_counter()
        seed_ananya_textiles()
        times.append(time.perf_counter() - t0)
    results["dataset_generation_avg_ms"] = statistics.mean(times) * 1000.0
    results["dataset_generation_min_ms"] = min(times) * 1000.0
    results["dataset_generation_max_ms"] = max(times) * 1000.0

    # 3. 30-Day Virtual Simulation (Advancing clock 30 days = 2,592,000 seconds with 50 scheduled events)
    world.reset()
    seed_ananya_textiles()
    for day in range(30):
        clock.schedule(clock.now() + (day * 86400), lambda: None)
    t0 = time.perf_counter()
    clock.advance(30 * 86400)
    results["simulation_30_day_ms"] = (time.perf_counter() - t0) * 1000.0

    # 4. Agent Mission Execution (1 Full Loop Cycle)
    times = []
    for _ in range(10):
        world.reset()
        seed_ananya_textiles()
        world.add_payment(Payment(id="pay_unk_bench", customer_id="c_1001", amount=8200.0, status=PaymentStatus.UNKNOWN, created_at=0))
        intent = AgentIntent(
            action_type="RECONCILE",
            reasoning="Benchmarking execution",
            expected_yield=8200.0,
            payload={"payment_id": "pay_unk_bench"}
        )
        provider = MockProvider([intent])
        loop = AgentLoop(customer_id="c_1001", mission_id="m_bench", max_risk=1.0, authority="AUTONOMOUS", llm_provider=provider)
        
        t0 = time.perf_counter()
        while loop.fsm.current().value not in ["COMPLETE", "ESCALATE"]:
            loop.tick()
        times.append(time.perf_counter() - t0)
    results["agent_mission_avg_ms"] = statistics.mean(times) * 1000.0
    results["agent_mission_min_ms"] = min(times) * 1000.0
    results["agent_mission_max_ms"] = max(times) * 1000.0

    # 5. Counterfactual Evaluation Time (Fork + All Feasible Actions NEV Calculation)
    times = []
    for _ in range(10):
        world.reset()
        seed_ananya_textiles()
        world.add_payment(Payment(id="pay_unk_bench", customer_id="c_1001", amount=8200.0, status=PaymentStatus.UNKNOWN, created_at=0))
        intent = AgentIntent(
            action_type="RECONCILE",
            reasoning="Counterfactual benchmark",
            expected_yield=8200.0,
            payload={"payment_id": "pay_unk_bench"}
        )
        t0 = time.perf_counter()
        counterfactual_evaluator.calculate_regret(
            customer_id="c_1001",
            chosen_intent=intent,
            max_risk=1.0,
            authority="AUTONOMOUS"
        )
        times.append(time.perf_counter() - t0)
    results["counterfactual_eval_avg_ms"] = statistics.mean(times) * 1000.0
    results["counterfactual_eval_min_ms"] = min(times) * 1000.0
    results["counterfactual_eval_max_ms"] = max(times) * 1000.0

    # 6. API Response Time (/simulator/world and /agent/mission/start)
    world.reset()
    seed_ananya_textiles()
    
    times_world = []
    for _ in range(50):
        t0 = time.perf_counter()
        res = client.get("/simulator/world")
        times_world.append(time.perf_counter() - t0)
    results["api_get_world_avg_ms"] = statistics.mean(times_world) * 1000.0
    results["api_get_world_p95_ms"] = sorted(times_world)[int(len(times_world) * 0.95)] * 1000.0

    times_mission = []
    for _ in range(50):
        t0 = time.perf_counter()
        res = client.post("/agent/mission/start", json={
            "customer_id": "c_1001",
            "target_recovery": 1000.0,
            "max_risk": 0.5,
            "authority": "AUTONOMOUS"
        })
        times_mission.append(time.perf_counter() - t0)
    results["api_start_mission_avg_ms"] = statistics.mean(times_mission) * 1000.0
    results["api_start_mission_p95_ms"] = sorted(times_mission)[int(len(times_mission) * 0.95)] * 1000.0

    print("--- BENCHMARK RESULTS ---")
    for k, v in results.items():
        print(f"{k}: {v:.3f}")
    return results

if __name__ == "__main__":
    run_performance_benchmarks()
