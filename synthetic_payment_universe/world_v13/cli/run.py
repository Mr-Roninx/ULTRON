import argparse
from synthetic_payment_universe.world_v13.cli.create import create_economic_civilization

def main():
    parser = argparse.ArgumentParser(description="Run multi-day civilization simulation")
    parser.add_argument("--days", type=int, default=30, help="Days to simulate")
    parser.add_argument("--seed", type=int, default=12345, help="Master seed")
    parser.add_argument("--profile", type=str, default="dev", help="World profile")
    args = parser.parse_args()

    w = create_economic_civilization(master_seed=args.seed, profile_name=args.profile)
    print(f"Simulating {args.days} days in Economic Civilization '{w.world_id}'...")
    processed = w.advance_days(args.days)
    print(f"Simulation completed! Processed {len(processed)} economic events across {args.days} days.")

if __name__ == "__main__":
    main()
