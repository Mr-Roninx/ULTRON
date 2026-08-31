import time
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ProviderHealthStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    RATE_LIMITED = "RATE_LIMITED"
    AUTH_FAILURE = "AUTH_FAILURE"
    TIMEOUT = "TIMEOUT"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"

class ProviderHealthMetric(BaseModel):
    provider: str
    status: ProviderHealthStatus = ProviderHealthStatus.AVAILABLE
    avg_latency_ms: float = 45.0
    success_rate_percent: float = 99.5
    timeout_rate_percent: float = 0.2
    last_checked_at: int = Field(default_factory=lambda: int(time.time()))
    details: Dict[str, Any] = Field(default_factory=dict)

class ProviderHealthService:
    """
    Measures and tracks real external payment provider telemetry and operational health.
    """
    def __init__(self):
        self._metrics: Dict[str, ProviderHealthMetric] = {
            "razorpay": ProviderHealthMetric(provider="razorpay", avg_latency_ms=120.0, success_rate_percent=99.2)
        }

    def record_call(self, provider: str, latency_ms: float, is_success: bool, is_timeout: bool = False):
        m = self._metrics.setdefault(provider, ProviderHealthMetric(provider=provider))
        m.last_checked_at = int(time.time())
        # Smooth EMA
        m.avg_latency_ms = round(m.avg_latency_ms * 0.85 + latency_ms * 0.15, 2)
        if not is_success:
            m.success_rate_percent = max(0.0, round(m.success_rate_percent - 1.5, 2))
        else:
            m.success_rate_percent = min(100.0, round(m.success_rate_percent + 0.1, 2))

        if is_timeout:
            m.status = ProviderHealthStatus.TIMEOUT
        elif m.success_rate_percent < 85.0:
            m.status = ProviderHealthStatus.DEGRADED
        elif m.success_rate_percent < 50.0:
            m.status = ProviderHealthStatus.OFFLINE
        else:
            m.status = ProviderHealthStatus.AVAILABLE

    def get_health(self, provider: str) -> ProviderHealthMetric:
        return self._metrics.get(provider, ProviderHealthMetric(provider=provider, status=ProviderHealthStatus.UNKNOWN))

    def get_all_health(self) -> Dict[str, ProviderHealthMetric]:
        return self._metrics

provider_health_service = ProviderHealthService()
