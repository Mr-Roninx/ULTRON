import random
from typing import Dict

class CommonRandomNumberManager:
    """
    Manages isolated, deterministic pseudo-random number generator streams for counterfactual branches.
    """
    def __init__(self, master_seed: int = 12345):
        self.master_seed = master_seed

    def get_branch_rng(self, decision_point_id: str, branch_name: str) -> random.Random:
        seed_offset = hash(f"{decision_point_id}_{branch_name}") % (2**31 - 1)
        return random.Random(self.master_seed + seed_offset)
