from typing import Dict, List, Tuple
from synthetic_payment_universe.generator.seeds import MasterSeedManager, PARTITION_SEED_RANGES
from synthetic_payment_universe.generator.customer_gen import CustomerGenerator

class UniverseSeedIsolationValidator:
    """
    Validates mathematical seed isolation and cross-partition independence.
    """
    @staticmethod
    def validate_partition_domains() -> Tuple[bool, List[str]]:
        errors: List[str] = []
        ranges = list(PARTITION_SEED_RANGES.items())

        for i in range(len(ranges)):
            pname_i, (start_i, end_i) = ranges[i]
            for j in range(i + 1, len(ranges)):
                pname_j, (start_j, end_j) = ranges[j]
                overlap = max(0, min(end_i, end_j) - max(start_i, start_j) + 1)
                if overlap > 0:
                    errors.append(f"Domain Overlap: Partition '{pname_i}' ({start_i}-{end_i}) overlaps with '{pname_j}' ({start_j}-{end_j})")

        return len(errors) == 0, errors

    @staticmethod
    def verify_reproducibility_and_independence(sample_size: int = 5) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        # 1. Identical seed reproducibility
        mgr_a1 = MasterSeedManager(100, partition_name="dev")
        mgr_a2 = MasterSeedManager(100, partition_name="dev")
        gen_a1 = CustomerGenerator(mgr_a1)
        gen_a2 = CustomerGenerator(mgr_a2)

        c_a1 = [gen_a1.generate_customer(i) for i in range(sample_size)]
        c_a2 = [gen_a2.generate_customer(i) for i in range(sample_size)]

        for c1, c2 in zip(c_a1, c_a2):
            if c1.average_transaction_value != c2.average_transaction_value:
                errors.append(f"Reproducibility failure on customer {c1.customer_id}")

        # 2. Partition independence
        mgr_b = MasterSeedManager(100, partition_name="evaluation")
        gen_b = CustomerGenerator(mgr_b)
        c_b = [gen_b.generate_customer(i) for i in range(sample_size)]

        # Dev vs Evaluation must differ due to distinct seed mapping
        diff_count = sum(1 for c1, cb in zip(c_a1, c_b) if c1.average_transaction_value != cb.average_transaction_value)
        if diff_count == 0:
            errors.append("Partition independence failure: Dev and Evaluation produced identical values")

        return len(errors) == 0, errors
