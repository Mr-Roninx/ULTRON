import argparse
import json
from synthetic_payment_universe.world_v13.cli.create import create_economic_civilization
from synthetic_payment_universe.world_v13.metrics.world_metrics import WorldCivilizationMetrics

def main():
    parser = argparse.ArgumentParser(description="Query civilization economic metrics")
    parser.add_argument("--seed", type=int, default=12345, help="Master seed")
    parser.add_argument("--profile", type=str, default="tiny", help="World profile")
    args = parser.parse_args()

    w = create_economic_civilization(master_seed=args.seed, profile_name=args.profile)
    stats = WorldCivilizationMetrics.compute_metrics(w.repository)
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
