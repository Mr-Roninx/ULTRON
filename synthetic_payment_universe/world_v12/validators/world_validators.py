from typing import Dict, List, Any, Tuple
from synthetic_payment_universe.world_v12.world.world import PersistentWorld

class WorldIntegrityValidators:
    """
    Automated validation suite verifying fundamental physical and financial invariants of the synthetic world.
    """
    @staticmethod
    def validate_ledger_integrity(world: PersistentWorld) -> Tuple[bool, List[str]]:
        errors = []
        if not world.ledger.verify_ledger_balance():
            errors.append(f"Ledger Imbalance: Sum of accounts {sum(world.ledger.account_balances.values())} != 0.0")
        return len(errors) == 0, errors

    @staticmethod
    def validate_referential_integrity(world: PersistentWorld) -> Tuple[bool, List[str]]:
        errors = []
        with world.repository.get_connection() as conn:
            c = conn.cursor()
            # Check dangling customer_ids in payments
            c.execute("""
                SELECT p.payment_id, p.customer_id FROM payments p
                LEFT JOIN customers c ON p.customer_id = c.customer_id
                WHERE c.customer_id IS NULL;
            """)
            dangling = c.fetchall()
            if dangling:
                errors.append(f"Referential integrity failure: {len(dangling)} payments have missing customer references.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_temporal_monotonicity(world: PersistentWorld) -> Tuple[bool, List[str]]:
        errors = []
        events = list(world.repository.get_events_stream(world.identity.current_time))
        prev_t = 0
        for e in events:
            if e["timestamp"] < prev_t:
                errors.append(f"Temporal monotonicity failure: Event {e['event_id']} timestamp {e['timestamp']} < previous {prev_t}")
            prev_t = e["timestamp"]
        return len(errors) == 0, errors
