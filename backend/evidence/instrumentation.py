import hashlib
import json
import time
import uuid
from typing import Dict, Any, Optional
from backend.evidence.models import ExperimentIdentity

SENSITIVE_KEYS = {
    "api_token", "api_key", "authorization", "token", "hf_token",
    "password", "secret", "private_key", "bearer", "cookie"
}

def generate_deterministic_hash(data: Any) -> str:
    """Generates a stable SHA-256 hash using sorted JSON serialization."""
    if isinstance(data, dict):
        serialized = json.dumps(data, sort_keys=True, default=str)
    elif isinstance(data, str):
        serialized = data
    else:
        serialized = str(data)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]

def scrub_sensitive_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively removes confidential keys, secrets, and auth tokens from telemetry payloads."""
    if not isinstance(payload, dict):
        return payload
    scrubbed = {}
    for k, v in payload.items():
        k_lower = str(k).lower()
        if any(secret in k_lower for secret in SENSITIVE_KEYS):
            scrubbed[k] = "[REDACTED_SECRET]"
        elif isinstance(v, dict):
            scrubbed[k] = scrub_sensitive_payload(v)
        elif isinstance(v, list):
            scrubbed[k] = [scrub_sensitive_payload(item) if isinstance(item, dict) else item for item in v]
        else:
            scrubbed[k] = v
    return scrubbed

class TimerContext:
    """Context manager measuring code block execution latency in milliseconds."""
    def __init__(self):
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.latency_ms: float = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.latency_ms = round((self.end_time - self.start_time) * 1000.0, 2)

def create_experiment_identity(
    experiment_id: str,
    seed: int,
    agent_config: Dict[str, Any],
    mechanism_config: Dict[str, bool],
    world_snapshot: Dict[str, Any]
) -> ExperimentIdentity:
    """Builds an immutable, uniquely identifiable ExperimentIdentity with snapshot hashes."""
    world_hash = generate_deterministic_hash(world_snapshot)
    combined_config = {"agent": agent_config, "mechanisms": mechanism_config}
    config_hash = generate_deterministic_hash(combined_config)
    run_id = f"run_{experiment_id}_{seed}_{str(uuid.uuid4())[:8]}"

    return ExperimentIdentity(
        experiment_id=experiment_id,
        run_id=run_id,
        seed=seed,
        world_snapshot_hash=world_hash,
        configuration_hash=config_hash,
        agent_configuration=scrub_sensitive_payload(agent_config),
        mechanism_configuration=mechanism_config,
        timestamp=time.time()
    )
