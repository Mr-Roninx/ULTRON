import hashlib
from typing import Dict, Any, Tuple

PARTITION_SEED_RANGES: Dict[str, Tuple[int, int]] = {
    "dev": (1, 1000),
    "validation": (1001, 2000),
    "evaluation": (2001, 5000),
    "hard_cases": (5001, 6000),
    "chaos": (6001, 7000),
    "adversarial": (7001, 8000)
}

class MasterSeedManager:
    """
    Deterministic hierarchical seed manager enforcing strict partition isolation.
    Generates reproducible, statistically independent sub-seeds across all simulation domains.
    """
    def __init__(self, master_seed: int = 12345, partition_name: str = "dev"):
        self.partition_name = partition_name.lower()
        self.partition_range = PARTITION_SEED_RANGES.get(self.partition_name, (1, 1000))
        # Ensure master seed is mapped deterministically within partition range
        range_span = self.partition_range[1] - self.partition_range[0] + 1
        self.partition_seed = self.partition_range[0] + (abs(int(master_seed)) % range_span)
        self.master_seed = self.partition_seed

    def get_subseed(self, domain: str, index: int = 0) -> int:
        raw = f"{self.partition_name}:{self.partition_seed}:{domain}:{index}"
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        # Convert first 8 bytes into positive 31-bit integer for random.seed()
        return int(digest[:8], 16) & 0x7FFFFFFF

    def get_customer_seed(self, customer_index: int) -> int:
        return self.get_subseed("CUSTOMER", customer_index)

    def get_merchant_seed(self, merchant_index: int) -> int:
        return self.get_subseed("MERCHANT", merchant_index)

    def get_payment_seed(self, payment_index: int) -> int:
        return self.get_subseed("PAYMENT", payment_index)

    def get_gateway_seed(self, step_index: int) -> int:
        return self.get_subseed("GATEWAY", step_index)

    def get_behavior_seed(self, entity_index: int) -> int:
        return self.get_subseed("BEHAVIOR", entity_index)

    def get_chaos_seed(self, chaos_index: int) -> int:
        return self.get_subseed("CHAOS", chaos_index)

    def get_counterfactual_seed(self, branch_index: int) -> int:
        return self.get_subseed("COUNTERFACTUAL", branch_index)
