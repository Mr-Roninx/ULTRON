from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class WorldProfile(str, Enum):
    TINY = "tiny"           # 100 customers, 1,000 payments (fast unit tests)
    DEV = "dev"             # 5,000 customers, 50,000 payments (integration)
    STANDARD = "standard"   # 25,000 customers, 250,000 payments (benchmarking)
    LARGE = "large"         # 100,000 customers, 1,000,000 payments (economic scale)

PROFILE_SETTINGS: Dict[WorldProfile, Dict[str, Any]] = {
    WorldProfile.TINY: {
        "customer_count": 100,
        "payments_per_customer": 10,
        "horizon_days": 7,
        "enable_chaos": True,
        "enable_ledger": True
    },
    WorldProfile.DEV: {
        "customer_count": 5000,
        "payments_per_customer": 10,
        "horizon_days": 14,
        "enable_chaos": True,
        "enable_ledger": True
    },
    WorldProfile.STANDARD: {
        "customer_count": 25000,
        "payments_per_customer": 10,
        "horizon_days": 30,
        "enable_chaos": True,
        "enable_ledger": True
    },
    WorldProfile.LARGE: {
        "customer_count": 100000,
        "payments_per_customer": 10,
        "horizon_days": 60,
        "enable_chaos": True,
        "enable_ledger": True
    }
}

class WorldConfig(BaseModel):
    profile: WorldProfile = WorldProfile.DEV
    customer_count: int = 5000
    payments_per_customer: int = 10
    horizon_days: int = 14
    enable_chaos: bool = True
    enable_ledger: bool = True
    storage_dir: str = "d:/Work Space/Project/Ultron/synthetic_payment_universe/datasets_v12"

    @classmethod
    def from_profile(cls, profile: WorldProfile, storage_dir: Optional[str] = None) -> "WorldConfig":
        settings = PROFILE_SETTINGS.get(profile, PROFILE_SETTINGS[WorldProfile.DEV])
        cfg = cls(
            profile=profile,
            customer_count=settings["customer_count"],
            payments_per_customer=settings["payments_per_customer"],
            horizon_days=settings["horizon_days"],
            enable_chaos=settings["enable_chaos"],
            enable_ledger=settings["enable_ledger"]
        )
        if storage_dir:
            cfg.storage_dir = storage_dir
        return cfg
