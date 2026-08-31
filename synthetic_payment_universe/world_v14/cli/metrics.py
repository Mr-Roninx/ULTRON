import argparse
import json
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def main():
    parser = argparse.ArgumentParser(description="Query emergent world telemetry")
    parser.add_argument("--seed", type=int, default=12345, help="Master seed")
    parser.add_argument("--profile", type=str, default="tiny", help="World profile")
    args = parser.parse_args()

    w = create_emergent_population_world(master_seed=args.seed, profile_name=args.profile)
    with w.repository.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT status, COUNT(*) FROM payments GROUP BY status")
        pmt_stats = dict(c.fetchall())

    telemetry = {
        "world_id": w.world_id,
        "customer_count": len(w.customers),
        "merchant_count": len(w.merchants),
        "payment_status_distribution": pmt_stats,
        "ledger_balanced": w.ledger.verify_ledger_balance()
    }
    print(json.dumps(telemetry, indent=2))

if __name__ == "__main__":
    main()
