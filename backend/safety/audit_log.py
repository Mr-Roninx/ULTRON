import hashlib
import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from simulator.clock import clock
from backend.audit.trace import scrub_trace_payload

class ImmutableAuditEvent(BaseModel):
    event_id: str
    actor: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: int
    prev_hash: str
    event_hash: str

class ImmutableAuditLog:
    """
    Hash-chained tamper-evident audit logger for safety-critical agent actions.
    """
    def __init__(self):
        self.chain: List[ImmutableAuditEvent] = []
        self._last_hash = "GENESIS_HASH_0000"

    def record_event(self, actor: str, event_type: str, payload: Dict[str, Any]) -> ImmutableAuditEvent:
        scrubbed = scrub_trace_payload(payload)
        now = clock.now()
        evt_id = f"aud_{len(self.chain) + 1}"
        
        raw_str = f"{evt_id}:{actor}:{event_type}:{json.dumps(scrubbed, sort_keys=True)}:{now}:{self._last_hash}"
        evt_hash = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

        evt = ImmutableAuditEvent(
            event_id=evt_id,
            actor=actor,
            event_type=event_type,
            payload=scrubbed,
            timestamp=now,
            prev_hash=self._last_hash,
            event_hash=evt_hash
        )
        self.chain.append(evt)
        self._last_hash = evt_hash
        return evt

    def verify_integrity(self) -> bool:
        prev = "GENESIS_HASH_0000"
        for evt in self.chain:
            if evt.prev_hash != prev:
                return False
            raw_str = f"{evt.event_id}:{evt.actor}:{evt.event_type}:{json.dumps(evt.payload, sort_keys=True)}:{evt.timestamp}:{prev}"
            expected = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
            if evt.event_hash != expected:
                return False
            prev = evt.event_hash
        return True

    def reset(self):
        self.chain.clear()
        self._last_hash = "GENESIS_HASH_0000"

immutable_audit_log = ImmutableAuditLog()
