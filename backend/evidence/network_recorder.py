import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class NetworkCallRecord(BaseModel):
    correlation_id: str
    provider: str
    operation: str
    hostname: str
    path_category: str
    timestamp: int = Field(default_factory=lambda: int(time.time()))
    status_code: int = 200
    latency_ms: float = 0.0
    success: bool = True
    evidence_class: str = "FIXTURE"

class OutboundNetworkRecorder:
    """
    Records safe outbound network activity metadata with strict isolation of auth headers and secrets.
    """
    def __init__(self):
        self._calls: List[NetworkCallRecord] = []

    def record_call(
        self,
        correlation_id: str,
        provider: str,
        operation: str,
        hostname: str,
        path_category: str,
        status_code: int = 200,
        latency_ms: float = 115.0,
        success: bool = True,
        evidence_class: str = "FIXTURE"
    ) -> NetworkCallRecord:
        rec = NetworkCallRecord(
            correlation_id=correlation_id,
            provider=provider,
            operation=operation,
            hostname=hostname,
            path_category=path_category,
            status_code=status_code,
            latency_ms=latency_ms,
            success=success,
            evidence_class=evidence_class
        )
        self._calls.append(rec)
        return rec

    def get_calls_for_correlation(self, correlation_id: str) -> List[NetworkCallRecord]:
        return [c for c in self._calls if c.correlation_id == correlation_id]

    def clear(self):
        self._calls.clear()

network_recorder = OutboundNetworkRecorder()
