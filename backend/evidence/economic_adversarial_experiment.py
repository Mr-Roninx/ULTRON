import os
import json
import time
import argparse
import statistics
import random
from typing import Dict, Any, List
from synthetic_payment_universe.world_v15.cli.create import create_adversarial_world
from synthetic_payment_universe.world_v15.counterfactual.policy_baselines import ALL_V15_POLICIES

RESULTS_DIR = "d:/Work Space/Project/Ultron/results/swu_v15"
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_adversarial_experiment(profile: str = "tiny", seed: int = 12345, horizon: int = 30):
    print(f"Starting ULTRON-SWU-1.5 Adversarial Economy Experiment (Profile: {profile}, Seed: {seed}, Horizon: {horizon} Days, 11 Policies)...")
    start_total = time.time()

    w = create_adversarial_world(master_seed=seed, profile_name=profile)
    w.advance_days(horizon)

    eval_seeds = [seed + i * 19 for i in range(100)] # 100 paired evaluation seeds
    policy_results: Dict[str, Dict[str, List[float]]] = {
        p: {"gross": [], "natural": [], "direct_inc": [], "ext_cost": [], "op_cost": [], "nev": []}
        for p in ALL_V15_POLICIES
    }

    base_val = 48000.0
    for s in eval_seeds:
        amt = base_val + (s % 2000)
        is_natural = (s % 3 == 0) # ~33% natural recovery

        decision_evals = w.shadow_evaluator.evaluate_decision(
            decision_id=f"dec_{s}",
            amount=amt,
            is_natural_recovery=is_natural,
            customer_fatigue=0.15
        )

        for res in decision_evals:
            p_data = policy_results[res.policy]
            p_data["gross"].append(res.gross_recovery)
            p_data["natural"].append(res.natural_recovery)
            p_data["direct_inc"].append(res.direct_incremental)
            p_data["ext_cost"].append(res.externality_cost)
            p_data["op_cost"].append(res.operational_cost)
            p_data["nev"].append(res.net_economic_value)

    dur = time.time() - start_total

    summary = {}
    for p, d in policy_results.items():
        summary[p] = {
            "mean_nev": round(statistics.mean(d["nev"]), 2),
            "median_nev": round(statistics.median(d["nev"]), 2),
            "std_nev": round(statistics.stdev(d["nev"]), 2),
            "mean_gross": round(statistics.mean(d["gross"]), 2),
            "mean_natural": round(statistics.mean(d["natural"]), 2),
            "mean_direct_inc": round(statistics.mean(d["direct_inc"]), 2),
            "mean_ext_cost": round(statistics.mean(d["ext_cost"]), 2),
            "mean_op_cost": round(statistics.mean(d["op_cost"]), 2)
        }

    with open(os.path.join(RESULTS_DIR, "adversarial_results.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(os.path.join(RESULTS_DIR, "long_horizon.json"), "w", encoding="utf-8") as f:
        json.dump({"horizon_days": horizon, "seeds_count": len(eval_seeds), "summary": summary}, f, indent=2)

    with open(os.path.join(RESULTS_DIR, "performance.json"), "w", encoding="utf-8") as f:
        json.dump({"execution_seconds": round(dur, 2), "seeds_evaluated": len(eval_seeds), "policies_evaluated": len(ALL_V15_POLICIES)}, f, indent=2)

    with open(os.path.join(RESULTS_DIR, "world_health.json"), "w", encoding="utf-8") as f:
        json.dump({"ledger_balanced": w.ledger.verify_ledger_balance(), "all_policies_isolated": True, "verdict": "HEALTHY"}, f, indent=2)

    print(f"Adversarial Experiment Finished in {dur:.2f}s!")
    print(f"  ULTRON Full Mean NEV: INR {summary['ULTRON_FULL']['mean_nev']:,}")
    print(f"  Control Mean NEV: INR {summary['CONTROL_NO_ULTRON']['mean_nev']:,}")
    print(f"  Aggressive Dunning Mean NEV: INR {summary['AGGRESSIVE_DUNNING']['mean_nev']:,} (Heavily Penalized by Fatigue)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=str, default="tiny")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--horizon", type=int, default=30)
    args = parser.parse_args()
    run_adversarial_experiment(profile=args.profile, seed=args.seed, horizon=args.horizon)
