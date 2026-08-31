import random

class PopulationCRNManager:
    """
    Common Random Numbers stream provider ensuring aligned stochastic draws across counterfactual branches.
    """
    def __init__(self, master_seed: int = 12345):
        self.master_seed = master_seed

    def get_stream(self, entity_id: str, branch_name: str) -> random.Random:
        seed_offset = hash(f"{entity_id}_{branch_name}") % (2**31 - 1)
        return random.Random(self.master_seed + seed_offset)
