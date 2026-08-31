from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class WorldProfile(str, Enum):
    TINY = "tiny"                   # 100 customers, 1,000 payments (fast tests)
    DEV = "dev"                     # 5,000 customers, 50,000 payments (integration)
    STANDARD = "standard"           # 25,000 customers, 250,000 payments (benchmarks)
    LARGE = "large"                 # 100,000 customers, 1,000,000 payments (large scale)
    CIVILIZATION = "civilization"   # Full continuous economy

PROFILE_SETTINGS: Dict[WorldProfile, Dict[str, Any]] = {
    WorldProfile.TINY: {
        "customer_count": 100,
        "merchant_count": 10,
        "horizon_days": 7,
        "enable_continuous_economy": True
    },
    WorldProfile.DEV: {
        "customer_count": 5000,
        "merchant_count": 50,
        "horizon_days": 14,
        "enable_continuous_economy": True
    },
    WorldProfile.STANDARD: {
        "customer_count": 25000,
        "merchant_count": 250,
        "horizon_days": 30,
        "enable_continuous_economy": True
    },
    WorldProfile.LARGE: {
        "customer_count": 100000,
        "merchant_count": 1000,
        "horizon_days": 90,
        "enable_continuous_economy": True
    },
    WorldProfile.CIVILIZATION: {
        "customer_count": 100000,
        "merchant_count": 5000,
        "horizon_days": 365,
        "enable_continuous_economy": True
    }
}

class WorldConfig(BaseModel):
    profile: WorldProfile = WorldProfile.DEV
    customer_count: int = 5000
    merchant_count: int = 50
    horizon_days: int = 14
    enable_continuous_economy: bool = True
    storage_dir: str = "d:/Work Space/Project/Ultron/synthetic_payment_universe/datasets_v13"

    @classmethod
    def from_profile(cls, profile: WorldProfile, storage_dir: Optional[str] = None) -> "WorldConfig":
        s = PROFILE_SETTINGS.get(profile, PROFILE_SETTINGS[WorldProfile.DEV])
        cfg = cls(
            profile=profile,
            customer_count=s["customer_count"],
            merchant_count=s["merchant_count"],
            horizon_days=s["horizon_days"],
            enable_continuous_economy=s["enable_continuous_economy"]
        )
        if storage_dir:
            cfg.storage_dir = storage_dir
        return cfg
