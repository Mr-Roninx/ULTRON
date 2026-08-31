import argparse
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.benchmark.runner import BenchmarkRunner

def main():
    parser = argparse.ArgumentParser(description="ULTRON v3.2 Phase 10 Master Benchmark Runner")
    parser.add_argument("--partition", choices=["dev", "val", "eval", "all", "smoke"], default="smoke",
                        help="Seed partition: dev (1-60), val (61-80), eval (81-180), smoke (1-5)")
    parser.add_argument("--seed", type=int, default=None, help="Specific single seed")
    parser.add_argument("--seeds", type=str, default=None, help="Comma-separated list of seeds (e.g. 1,2,3)")
    parser.add_argument("--horizons", type=str, default="7,14,30,60", help="Comma-separated horizons in days")
    parser.add_argument("--no-chaos", action="store_true", help="Disable chaos benchmark suite")

    args = parser.parse_args()

    if args.seed is not None:
        seed_list = [args.seed]
    elif args.seeds is not None:
        seed_list = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    elif args.partition == "smoke":
        seed_list = list(range(1, 6))
    elif args.partition == "dev":
        seed_list = list(range(1, 61))
    elif args.partition == "val":
        seed_list = list(range(61, 81))
    elif args.partition == "eval":
        seed_list = list(range(81, 181))
    elif args.partition == "all":
        seed_list = list(range(1, 181))
    else:
        seed_list = [42]

    horizons = [int(h.strip()) for h in args.horizons.split(",") if h.strip()]

    runner = BenchmarkRunner(output_dir="results")
    results = runner.run_benchmark_suite(
        seeds=seed_list,
        horizons=horizons,
        include_chaos=not args.no_chaos
    )

    print(f"\nSuccessfully evaluated {len(seed_list)} seeds.")
    print("Aggregate Summary for FULL_ULTRON:")
    full_ultron = results["aggregated_metrics"].get("FULL_ULTRON", {})
    print(f"  Gross Recovery Mean: INR {full_ultron.get('gross_recovery_mean', 0):,.2f} (95% CI: INR {full_ultron.get('gross_recovery_ci95', [0,0])[0]:,.2f} - INR {full_ultron.get('gross_recovery_ci95', [0,0])[1]:,.2f})")
    print(f"  Incremental Recovery Mean: INR {full_ultron.get('incremental_recovery_mean', 0):,.2f}")
    print(f"  Net Incremental Recovery Mean: INR {full_ultron.get('net_incremental_recovery_mean', 0):,.2f}")
    print(f"  Recovery Rate Mean: {full_ultron.get('recovery_rate_mean', 0) * 100:.2f}%")

if __name__ == "__main__":
    main()
