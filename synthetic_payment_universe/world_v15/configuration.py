import hashlib
import json
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class WorldProfileV15(str, Enum):
    TINY = "tiny"
    DEV = "dev"
    STANDARD = "standard"
    LARGE = "large"
    CIVILIZATION = "civilization"

class ParameterRegistryV15(BaseModel):
    config_id: str = "CONFIG_V15_EVALUATION"
    version: str = "1.5.0"
    natural_recovery_base_p: float = 0.36
    fatigue_decay_daily_rate: float = 0.82
    gateway_congestion_penalty: float = 0.25
    opt_out_threshold_fatigue: float = 0.85
    critical_churn_fatigue: float = 0.90
    ltv_discount_factor: float = 0.95

    def get_config_hash(self) -> str:
        dump = json.dumps(self.model_dump(), sort_keys=True)
        return hashlib.sha256(dump.encode("utf-8")).hexdigest()

class WorldConfigV15(BaseModel):
    profile: WorldProfileV15 = WorldProfileV15.DEV
    customer_count: int = 5000
    merchant_count: int = 50
    horizon_days: int = 30
    storage_dir: str = "d:/Work Space/Project/Ultron/synthetic_payment_universe/datasets_v15"
    params: ParameterRegistryV15 = Field(default_factory=ParameterRegistryV15)

    @classmethod
    def from_profile(cls, profile: WorldProfileV15, storage_dir: Optional[str] = None) -> "WorldConfigV15":
        counts = {
            WorldProfileV15.TINY: (100, 10, 30),
            WorldProfileV15.DEV: (5000, 50, 30),
            WorldProfileV15.STANDARD: (25000, 250, 90),
            WorldProfileV15.LARGE: (100000, 1000, 180),
            WorldProfileV15.CIVILIZATION: (1000000, 5000, 365)
        }
        c, m, h = counts.get(profile, (5000, 50, 30))
        cfg = cls(profile=profile, customer_count=c, merchant_count=m, horizon_days=h)
        if storage_dir:
            cfg.storage_dir = storage_dir
        return cfg
