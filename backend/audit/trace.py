import re
import uuid
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from simulator.clock import clock

SECRET_PATTERNS = [
    re.compile(r"hf_[a-zA-Z0-9]{30,}", re.IGNORECASE),
    re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),
    re.compile(r"api[_-]?key\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{20,}", re.IGNORECASE),
]

SENSITIVE_KEYS = {
    "hf_token", "api_token", "token", "authorization", "auth",
    "password", "secret", "private_key", "api_key", "prompt",
    "system_prompt", "full_prompt", "chain_of_thought", "private_cot",
    "reasoning_content", "hidden_reasoning", "raw_sql"
}

def scrub_trace_payload(data: Any) -> Any:
    """
    Recursively scrubs secrets, authorization headers, private prompts,
    and raw credentials from telemetry payloads.
    """
    if isinstance(data, dict):
        scrubbed = {}
        for k, v in data.items():
            if str(k).lower() in SENSITIVE_KEYS:
                scrubbed[k] = "[SCRUBBED_SECRET]"
            else:
                scrubbed[k] = scrub_trace_payload(v)
        return scrubbed
    elif isinstance(data, list):
        return [scrub_trace_payload(item) for item in data]
    elif isinstance(data, str):
        cleaned = data
        for pat in SECRET_PATTERNS:
            cleaned = pat.sub("[SCRUBBED_CREDENTIAL]", cleaned)
        return cleaned
    return data

class TraceEvent(BaseModel):
    trace_id: str
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    event_type: str
    timestamp: int
    simulation_time: int
    mission_id: Optional[str] = "SYSTEM"
    actor: str = "ULTRON_CORE"
    payload: Dict[str, Any] = Field(default_factory=dict)

class AuditTrace:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or f"trc_{uuid.uuid4().hex[:8]}"
        self.events: List[TraceEvent] = []

    def log(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        mission_id: str = "SYSTEM",
        actor: str = "ULTRON_CORE"
    ) -> TraceEvent:
        safe_payload = scrub_trace_payload(payload or {})
        sim_time = clock.now()
        import time
        real_time_ms = int(time.time() * 1000)

        event = TraceEvent(
            trace_id=self.trace_id,
            event_type=event_type,
            timestamp=real_time_ms,
            simulation_time=sim_time,
            mission_id=mission_id,
            actor=actor,
            payload=safe_payload
        )
        self.events.append(event)
        return event

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "event_count": len(self.events),
            "events": [e.model_dump() for e in self.events]
        }

    def export_json(self, file_path: str) -> None:
        import os
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

trace_engine = AuditTrace()
