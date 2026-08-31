from typing import List, Dict, Any, Optional
from synthetic_payment_universe.world_v12.state.repository import SQLiteWorldRepository

class ReplayEngine:
    """
    Replay Engine for inspecting historical world trajectories and replaying events up to time T.
    """
    def __init__(self, repository: SQLiteWorldRepository):
        self.repo = repository

    def inspect_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        with self.repo.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM events WHERE event_id = ?", (event_id,))
            row = c.fetchone()
            if not row:
                return None
            import json
            return {
                "event_id": row[0],
                "event_type": row[1],
                "entity_id": row[2],
                "timestamp": row[3],
                "visibility": row[4],
                "causal_parent_id": row[5],
                "payload": json.loads(row[6]) if row[6] else {}
            }

    def replay_to(self, target_timestamp: int) -> List[Dict[str, Any]]:
        """Yields all historical events chronologically up to target_timestamp."""
        return list(self.repo.get_events_stream(target_timestamp))
