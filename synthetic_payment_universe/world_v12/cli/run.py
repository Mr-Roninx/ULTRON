import argparse
import time
from synthetic_payment_universe.world_v12.world.factory import load_world

def main():
    parser = argparse.ArgumentParser(description="Run ULTRON World Simulation to Target Time (SWU-1.2)")
    parser.add_argument("--db", type=str, required=True, help="Path to world database")
    parser.add_argument("--advance_seconds", type=int, default=7200, help="Seconds to advance simulation clock")
    args = parser.parse_args()

    world = load_world(args.db)
    if not world:
        print(f"Error: Could not load world database at {args.db}")
        return

    current_t = world.identity.current_time
    target_t = current_t + args.advance_seconds
    print(f"Advancing World '{world.identity.world_id}' from {current_t} to {target_t} (+{args.advance_seconds}s)...")

    processed = world.advance_to(target_t)
    print(f"Simulation Advanced Successfully! Processed {len(processed)} intermediate events.")

if __name__ == "__main__":
    main()
