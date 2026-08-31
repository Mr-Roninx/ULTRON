import hashlib
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict
from simulator.clock import clock

class AuditEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: str
    mission_id: str
    timestamp: int
    actor: str
    event_type: str
    input_hash: str
    previous_hash: str
    current_hash: str
    payload: Dict[str, Any]

class AuditLedger:
    def __init__(self):
        self._chain: List[AuditEvent] = []

    def reset(self):
        self._chain.clear()

    @staticmethod
    def canonical_json(data: Dict[str, Any]) -> str:
        """Deterministic canonical JSON serialization with sorted keys and no whitespace."""
        def default_serializer(obj):
            if isinstance(obj, BaseModel):
                return obj.model_dump()
            if hasattr(obj, "value"): # Enum support
                return obj.value
            return str(obj)
        return json.dumps(data, sort_keys=True, separators=(",", ":"), default=default_serializer)

    def calculate_input_hash(self, payload: Dict[str, Any]) -> str:
        canonical = self.canonical_json(payload)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def calculate_block_hash(self, event_id: str, mission_id: str, timestamp: int, actor: str, event_type: str, input_hash: str, previous_hash: str, payload: Dict[str, Any]) -> str:
        canonical_payload = self.canonical_json(payload)
        block_content = f"{event_id}|{mission_id}|{timestamp}|{actor}|{event_type}|{input_hash}|{previous_hash}|{canonical_payload}"
        return hashlib.sha256(block_content.encode("utf-8")).hexdigest()

    def log(
        self,
        event_type: str,
        actor: str,
        payload: Dict[str, Any],
        mission_id: str = "SYSTEM",
        input_hash: Optional[str] = None,
        timestamp: Optional[int] = None
    ) -> AuditEvent:
        ts = clock.now() if timestamp is None else timestamp
        event_id = f"aud_{str(uuid.uuid4())[:8]}"
        
        # Calculate input hash if not provided
        computed_input_hash = input_hash or self.calculate_input_hash(payload)
        
        # Determine previous hash
        previous_hash = self._chain[-1].current_hash if self._chain else "GENESIS"
        
        # Compute immutable block hash
        current_hash = self.calculate_block_hash(
            event_id=event_id,
            mission_id=mission_id,
            timestamp=ts,
            actor=actor,
            event_type=event_type,
            input_hash=computed_input_hash,
            previous_hash=previous_hash,
            payload=payload
        )
        
        event = AuditEvent(
            event_id=event_id,
            mission_id=mission_id,
            timestamp=ts,
            actor=actor,
            event_type=event_type,
            input_hash=computed_input_hash,
            previous_hash=previous_hash,
            current_hash=current_hash,
            payload=payload
        )
        
        self._chain.append(event)
        return event

    def get_trace(self, mission_id: Optional[str] = None) -> List[AuditEvent]:
        if mission_id is None:
            return list(self._chain)
        return [e for e in self._chain if e.mission_id == mission_id]

    def verify_chain(self) -> Tuple[bool, Optional[str]]:
        """
        Cryptographically validates the entire ledger chain.
        Detects tampering with payloads, timestamps, previous hashes,
        event deletions, insertions, or reorderings.
        """
        if not self._chain:
            return True, None

        expected_prev = "GENESIS"
        for idx, event in enumerate(self._chain):
            # 1. Verify previous hash chaining
            if event.previous_hash != expected_prev:
                return False, f"Broken hash chain at index {idx}: expected previous_hash '{expected_prev}', got '{event.previous_hash}'"

            # 2. Verify input hash integrity
            expected_input_hash = self.calculate_input_hash(event.payload)
            if event.input_hash != expected_input_hash and event.input_hash != "EXTERNAL":
                return False, f"Tampered input payload hash at index {idx}: expected '{expected_input_hash}', got '{event.input_hash}'"

            # 3. Verify block hash calculation
            expected_block_hash = self.calculate_block_hash(
                event_id=event.event_id,
                mission_id=event.mission_id,
                timestamp=event.timestamp,
                actor=event.actor,
                event_type=event.event_type,
                input_hash=event.input_hash,
                previous_hash=event.previous_hash,
                payload=event.payload
            )
            if event.current_hash != expected_block_hash:
                return False, f"Tampered block hash at index {idx}: expected '{expected_block_hash}', got '{event.current_hash}'"

            expected_prev = event.current_hash

        return True, None

audit_ledger = AuditLedger()
