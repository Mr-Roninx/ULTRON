import argparse
import json
from synthetic_payment_universe.world_v15.cli.create import create_adversarial_world

def main():
    parser = argparse.ArgumentParser(description="Query adversarial world telemetry")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--profile", type=str, default="tiny")
    args = parser.parse_args()

    w = create_adversarial_world(master_seed=args.seed, profile_name=args.profile)
    res = {
        "world_id": w.world_id,
        "config_hash": w.config.params.get_config_hash(),
        "customer_count": len(w.customers),
        "payment_count": len(w.payments),
        "ledger_balanced": w.ledger.verify_ledger_balance(),
        "active_gateways": len(w.gateway_externalities.gateways)
    }
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
