import hashlib
import json
from typing import Dict, Any, Set

class IdempotencyManager:
    """
    Generates and tracks deterministic idempotency keys for financial and operational actions.
    Guarantees no duplicate execution.
    """
    def __init__(self):
        self._processed_keys: Set[str] = set()

    def generate_key(self, payment_id: str, action_type: str, timestamp_bucket: int) -> str:
        raw = f"{payment_id}:{action_type}:{timestamp_bucket}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def claim_execution(self, key: str) -> bool:
        if key in self._processed_keys:
            return False # Duplicate attempt
        self._processed_keys.add(key)
        return True

    def reset(self):
        self._processed_keys.clear()

idempotency_manager = IdempotencyManager()
