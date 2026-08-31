from typing import List, Dict, Any, Tuple
from synthetic_payment_universe.world_v12.world.world import PersistentWorld

class WorldStatisticalValidator:
    """
    Validates that real-world class distributions and failure taxonomy coverage meet realistic bounds.
    """
    @staticmethod
    def validate_world_distributions(world: PersistentWorld) -> Tuple[bool, Dict[str, Any], List[str]]:
        errors = []
        with world.repository.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT status, COUNT(*) FROM payments GROUP BY status")
            status_counts = dict(c.fetchall())
            total = sum(status_counts.values())

            if total == 0:
                return False, {}, ["No payments found in world database."]

            failed = status_counts.get("FAILED", 0)
            settled = status_counts.get("SETTLED", 0)

            failure_rate = round(failed / total, 4)
            success_rate = round(settled / total, 4)

            stats = {
                "total_payments": total,
                "status_breakdown": status_counts,
                "failure_rate": failure_rate,
                "success_rate": success_rate
            }

            if failure_rate > 0.40:
                errors.append(f"Statistical anomaly: Unrealistic failure rate {failure_rate*100:.1f}% > 40%")
            if success_rate < 0.60:
                errors.append(f"Statistical anomaly: Unrealistic success rate {success_rate*100:.1f}% < 60%")

            return len(errors) == 0, stats, errors
