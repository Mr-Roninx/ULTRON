import argparse
from synthetic_payment_universe.world_v15.cli.create import create_adversarial_world

def main():
    parser = argparse.ArgumentParser(description="Simulate adversarial economic world across horizon days")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--profile", type=str, default="dev")
    args = parser.parse_args()

    w = create_adversarial_world(master_seed=args.seed, profile_name=args.profile)
    print(f"Simulating {args.days} days in Adversarial World '{w.world_id}'...")
    w.advance_days(args.days)
    print(f"Simulation completed! Ledger balanced: {w.ledger.verify_ledger_balance()}")

if __name__ == "__main__":
    main()
