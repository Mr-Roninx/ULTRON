from enum import Enum
from typing import Dict, Any, List, Optional, Callable
import time
import os
from pydantic import BaseModel, Field

class LLMOperatingMode(str, Enum):
    REAL_LLM_MODE = "REAL_LLM_MODE"
    SAFE_MODE = "SAFE_MODE"
    BENCHMARK_MODE = "BENCHMARK_MODE"
    DEMO_MODE = "DEMO_MODE"

class LatencySLA(str, Enum):
    EXCELLENT = "EXCELLENT"      # < 2000 ms
    ACCEPTABLE = "ACCEPTABLE"    # 2000 - 5000 ms
    DEGRADED = "DEGRADED"        # 5000 - 10000 ms
    TIMEOUT_FALLBACK = "TIMEOUT/FALLBACK" # > 10000 ms

class PerformanceRecord(BaseModel):
    request_id: str
    provider: str
    model: str
    mode: str
    start_time: float
    end_time: float
    latency_ms: float
    sla_class: LatencySLA
    status: str # "SUCCESS", "TIMEOUT", "FALLBACK", "ERROR"
    fallback_used: bool = False
    tokens_used: Optional[int] = None
    context_chars: int = 0
    error_message: Optional[str] = None

class LLMPerformanceController:
    """
    Production-grade LLM latency, timeout, and failover controller.
    Ensures ULTRON never blocks indefinitely on cloud inference.
    """
    def __init__(
        self,
        soft_timeout_ms: Optional[float] = None,
        hard_timeout_ms: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        max_context_chars: Optional[int] = None,
        mode: Optional[LLMOperatingMode] = None
    ):
        self.soft_timeout_ms = soft_timeout_ms or float(os.environ.get("LLM_SOFT_TIMEOUT_MS", 5000.0))
        self.hard_timeout_ms = hard_timeout_ms or float(os.environ.get("LLM_HARD_TIMEOUT_MS", 10000.0))
        self.max_output_tokens = max_output_tokens or int(os.environ.get("LLM_MAX_OUTPUT_TOKENS", 300))
        self.max_context_chars = max_context_chars or int(os.environ.get("LLM_MAX_CONTEXT_CHARS", 4000))
        
        env_mode = os.environ.get("ULTRON_OPERATING_MODE", "REAL_LLM_MODE").upper()
        self.mode = mode or LLMOperatingMode(env_mode if env_mode in LLMOperatingMode.__members__ else "REAL_LLM_MODE")
        self.history: List[PerformanceRecord] = []

    def classify_latency(self, latency_ms: float, timed_out: bool = False) -> LatencySLA:
        if timed_out or latency_ms > self.hard_timeout_ms:
            return LatencySLA.TIMEOUT_FALLBACK
        elif latency_ms <= 2000.0:
            return LatencySLA.EXCELLENT
        elif latency_ms <= 5000.0:
            return LatencySLA.ACCEPTABLE
        else:
            return LatencySLA.DEGRADED

    def get_hard_timeout_seconds(self) -> float:
        return self.hard_timeout_ms / 1000.0

    def get_soft_timeout_seconds(self) -> float:
        return self.soft_timeout_ms / 1000.0

    def record_execution(
        self,
        request_id: str,
        provider: str,
        model: str,
        latency_ms: float,
        status: str,
        fallback_used: bool = False,
        tokens_used: Optional[int] = None,
        context_chars: int = 0,
        error_message: Optional[str] = None
    ) -> PerformanceRecord:
        sla = self.classify_latency(latency_ms, timed_out=(status == "TIMEOUT"))
        rec = PerformanceRecord(
            request_id=request_id,
            provider=provider,
            model=model,
            mode=self.mode.value,
            start_time=time.time() - (latency_ms / 1000.0),
            end_time=time.time(),
            latency_ms=round(latency_ms, 2),
            sla_class=sla,
            status=status,
            fallback_used=fallback_used,
            tokens_used=tokens_used,
            context_chars=context_chars,
            error_message=error_message
        )
        self.history.append(rec)
        return rec

    def get_statistics(self) -> Dict[str, Any]:
        if not self.history:
            return {
                "total_requests": 0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "mean_latency_ms": 0.0,
                "fallback_rate": 0.0,
                "timeout_rate": 0.0,
                "success_rate": 0.0,
                "sla_breakdown": {}
            }

        latencies = sorted([r.latency_ms for r in self.history])
        n = len(latencies)
        p50 = latencies[int(n * 0.50)]
        p95 = latencies[min(n - 1, int(n * 0.95))]
        mean_lat = sum(latencies) / n
        fallbacks = sum(1 for r in self.history if r.fallback_used)
        timeouts = sum(1 for r in self.history if r.status == "TIMEOUT")
        successes = sum(1 for r in self.history if r.status == "SUCCESS")

        sla_counts = {}
        for r in self.history:
            sla_counts[r.sla_class.value] = sla_counts.get(r.sla_class.value, 0) + 1

        return {
            "total_requests": n,
            "p50_latency_ms": round(p50, 2),
            "p95_latency_ms": round(p95, 2),
            "mean_latency_ms": round(mean_lat, 2),
            "fallback_rate": round(fallbacks / n, 4),
            "timeout_rate": round(timeouts / n, 4),
            "success_rate": round(successes / n, 4),
            "sla_breakdown": sla_counts
        }

    def reset(self):
        self.history.clear()

llm_performance_controller = LLMPerformanceController()
