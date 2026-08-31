import argparse
import time
from synthetic_payment_universe.world_v12.world.config import WorldProfile
from synthetic_payment_universe.world_v12.world.factory import create_world
from synthetic_payment_universe.world_v12.generator.world_generator import WorldDataPopulator

def main():
    parser = argparse.ArgumentParser(description="Create ULTRON Synthetic Economic World (SWU-1.2)")
    parser.add_argument("--seed", type=int, default=12345, help="Master seed")
    parser.add_argument("--partition", type=str, default="dev", help="Partition name (dev, validation, evaluation, hard_cases, chaos, adversarial)")
    parser.add_argument("--profile", type=str, default="dev", choices=["tiny", "dev", "standard", "large"], help="World scale profile")
    args = parser.parse_args()

    prof = WorldProfile(args.profile)
    print(f"Creating Persistent World: Seed={args.seed}, Partition={args.partition}, Profile={prof.value}...")
    start_t = time.time()
    world = create_world(master_seed=args.seed, partition_name=args.partition, profile=prof)

    print(f"Populating economic entities and temporal histories...")
    populator = WorldDataPopulator(world)
    stats = populator.populate()

    elapsed = time.time() - start_t
    print(f"World {world.identity.world_id} Created Successfully in {elapsed:.2f}s!")
    print(f"  Customers: {stats['customers']:,}")
    print(f"  Payments: {stats['payments']:,}")
    print(f"  Ledger Balanced: {stats['ledger_balanced']}")
    print(f"  Database Path: {world.db_path}")

if __name__ == "__main__":
    main()
