import hashlib
import json
from typing import List, Dict, Any
from synthetic_payment_universe.world_v13.repository import SQLiteCivilizationRepository

class CivilizationReplayEngine:
    """
    Replays historical event streams up to target timestamp and computes deterministic SHA-256 state hashes.
    """
    def __init__(self, repository: SQLiteCivilizationRepository):
        self.repository = repository

    def replay_to(self, target_timestamp: int) -> List[Dict[str, Any]]:
        return list(self.repository.get_events_stream(target_timestamp))

    def compute_state_hash(self, target_timestamp: int) -> str:
        events = self.replay_to(target_timestamp)
        serialized = json.dumps(events, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
