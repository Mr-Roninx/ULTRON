import hashlib
import json
from typing import List, Dict, Any
from synthetic_payment_universe.world_v14.repository import SQLiteEmergentRepository

class PopulationReplayEngine:
    """
    Reconstructs event history and computes cryptographic state hashes.
    """
    def __init__(self, repository: SQLiteEmergentRepository):
        self.repository = repository

    def compute_state_hash(self, target_timestamp: int) -> str:
        events = list(self.repository.get_events_stream(target_timestamp))
        dump = json.dumps(events, sort_keys=True)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()
