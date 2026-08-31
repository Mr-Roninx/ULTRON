import random
from typing import Dict, Any

class AlignedCRNManager:
    """
    Manages Common Random Number streams aligned across 11 competitive and adversarial policies.
    """
    def __init__(self, master_seed: int = 12345):
        self.master_seed = master_seed

    def get_stream(self, entity_id: str, policy_name: str) -> random.Random:
        seed_offset = hash(f"{entity_id}_{policy_name}") % (2**31 - 1)
        return random.Random(self.master_seed + seed_offset)
