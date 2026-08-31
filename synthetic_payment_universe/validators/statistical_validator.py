from typing import List, Dict, Any, Tuple
from synthetic_payment_universe.schema.entities import Payment

class UniverseStatisticalValidator:
    """
    Validates statistical realism, realistic class balance, and long-tail coverage.
    Rejects artificial 100% failure rates or 100% success rates.
    """
    @staticmethod
    def validate_distributions(payments: List[Payment]) -> Tuple[bool, Dict[str, Any], List[str]]:
        errors: List[str] = []
        total = len(payments)
        if total == 0:
            return False, {}, ["Payment list is empty."]

        status_counts: Dict[str, int] = {}
        failure_code_counts: Dict[str, int] = {}

        for p in payments:
            st = p.status
            status_counts[st] = status_counts.get(st, 0) + 1
            if st == "FAILED":
                code = p.failure_code or "UNKNOWN"
                failure_code_counts[code] = failure_code_counts.get(code, 0) + 1

        failed_count = status_counts.get("FAILED", 0)
        settled_count = status_counts.get("SETTLED", 0)

        failure_rate = round(failed_count / total, 4)
        success_rate = round(settled_count / total, 4)

        stats = {
            "total_payments": total,
            "status_breakdown": status_counts,
            "failure_rate": failure_rate,
            "success_rate": success_rate,
            "failure_code_breakdown": failure_code_counts
        }

        # Sanity Bounds Check
        if failure_rate > 0.40:
            errors.append(f"Statistical Anomaly: Unrealistic failure rate {failure_rate*100:.1f}% > 40.0%")
        if failure_rate < 0.02:
            errors.append(f"Statistical Anomaly: Unrealistic failure rate {failure_rate*100:.1f}% < 2.0%")
        if success_rate < 0.60:
            errors.append(f"Statistical Anomaly: Unrealistic success rate {success_rate*100:.1f}% < 60.0%")

        # Check key failure taxonomy coverage in larger samples
        if failed_count > 20:
            if "91" not in failure_code_counts:
                errors.append("Statistical Anomaly: ISO 91 missing from failure sample.")
            if "51" not in failure_code_counts:
                errors.append("Statistical Anomaly: ISO 51 missing from failure sample.")

        return len(errors) == 0, stats, errors
