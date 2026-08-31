import os
import json
import time
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

RESULTS_DIR = "d:/Work Space/Project/Ultron/results/phase17"
os.makedirs(RESULTS_DIR, exist_ok=True)

class ProviderHealthStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    RATE_LIMITED = "RATE_LIMITED"         # 429
    CREDIT_EXHAUSTED = "CREDIT_EXHAUSTED" # 402
    TIMEOUT = "TIMEOUT"
    INVALID_RESPONSE = "INVALID_RESPONSE"
    OFFLINE = "OFFLINE"

class ProviderTruthRecord(BaseModel):
    provider: str
    model: str
    credential_available: bool
    request_attempted: bool
    request_success: bool
    status: ProviderHealthStatus
    failure_reason: Optional[str] = None
    http_status: Optional[int] = None
    latency_ms: float = 0.0
    fallback_used: bool = False
    timestamp: float = Field(default_factory=time.time)

class ProviderHealthTracker:
    """
    Transparently tracks live LLM provider connection truth.
    Ensures depleted credits or fallbacks are never misrepresented as live successes.
    """
    def __init__(self):
        self.health_states: Dict[str, ProviderHealthStatus] = {
            "HuggingFace": ProviderHealthStatus.AVAILABLE,
            "LocalQwen": ProviderHealthStatus.AVAILABLE,
            "MockProvider": ProviderHealthStatus.AVAILABLE
        }
        self.history: List[ProviderTruthRecord] = []

    def record_attempt(
        self,
        provider: str,
        model: str,
        credential_available: bool,
        request_success: bool,
        status: ProviderHealthStatus,
        latency_ms: float,
        failure_reason: Optional[str] = None,
        http_status: Optional[int] = None,
        fallback_used: bool = False
    ) -> ProviderTruthRecord:
        self.health_states[provider] = status
        
        rec = ProviderTruthRecord(
            provider=provider,
            model=model,
            credential_available=credential_available,
            request_attempted=True,
            request_success=request_success,
            status=status,
            failure_reason=failure_reason,
            http_status=http_status,
            latency_ms=round(latency_ms, 2),
            fallback_used=fallback_used
        )
        self.history.append(rec)
        self.export_truth()
        return rec

    def export_truth(self, filepath: Optional[str] = None) -> str:
        out_path = filepath or os.path.join(RESULTS_DIR, "live_provider_truth.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        hf_recs = [r for r in self.history if r.provider == "HuggingFace"]
        total_hf_attempts = len(hf_recs)
        hf_successes = sum(1 for r in hf_recs if r.request_success)
        hf_credit_exhausted = sum(1 for r in hf_recs if r.status == ProviderHealthStatus.CREDIT_EXHAUSTED or r.http_status == 402)
        
        summary = {
            "timestamp": time.time(),
            "active_health_states": {k: v.value for k, v in self.health_states.items()},
            "hugging_face_summary": {
                "total_requests_attempted": total_hf_attempts,
                "live_hf_successes": hf_successes,
                "live_hf_success_rate": round(hf_successes / max(1, total_hf_attempts), 4),
                "credit_exhausted_count": hf_credit_exhausted,
                "fallback_rate": round(sum(1 for r in hf_recs if r.fallback_used) / max(1, total_hf_attempts), 4),
                "truth_verdict": "LIVE_HF_OPERATIONAL" if hf_successes > 0 else (
                    "HF_CREDIT_EXHAUSTED_FALLBACK_ACTIVE" if hf_credit_exhausted > 0 else "HF_NOT_AVAILABLE"
                )
            },
            "records": [r.model_dump() for r in self.history[-30:]]
        }
        
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return out_path

    def reset(self):
        self.history.clear()
        self.health_states = {
            "HuggingFace": ProviderHealthStatus.AVAILABLE,
            "LocalQwen": ProviderHealthStatus.AVAILABLE,
            "MockProvider": ProviderHealthStatus.AVAILABLE
        }

provider_health_tracker = ProviderHealthTracker()
