from typing import Dict, Any, Optional
import hashlib
import json

class IdempotencyEngine:
    def __init__(self):
        self.records: Dict[str, Dict[str, Any]] = {}
        
    def _generate_key(self, mission_id: str, action_type: str, payload: Dict[str, Any]) -> str:
        # Create deterministic hash of payload
        payload_str = json.dumps(payload, sort_keys=True)
        base = f"{mission_id}_{action_type}_{payload_str}"
        return hashlib.sha256(base.encode()).hexdigest()
        
    def check_and_record(self, mission_id: str, action_type: str, payload: Dict[str, Any], result: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        key = self._generate_key(mission_id, action_type, payload)
        
        if result is None:
            # Just checking
            return self.records.get(key)
            
        # Recording result
        self.records[key] = result
        return result

    def clear(self):
        self.records.clear()

    def reset(self):
        self.records.clear()

idempotency_engine = IdempotencyEngine()
