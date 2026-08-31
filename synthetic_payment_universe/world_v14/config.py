from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class WorldProfileV14(str, Enum):
    TINY = "tiny"                   # 100 customers, 10 merchants, 1,000 payments
    DEV = "dev"                     # 5,000 customers, 50 merchants, 50,000 payments
    STANDARD = "standard"           # 25,000 customers, 250 merchants, 250,000 payments
    LARGE = "large"                 # 100,000 customers, 1,000 merchants, 1,000,000+ payments
    CIVILIZATION = "civilization"   # 1,000,000+ customers, 10,000,000+ events

PROFILE_SETTINGS_V14: Dict[WorldProfileV14, Dict[str, Any]] = {
    WorldProfileV14.TINY: {
        "customer_count": 100,
        "merchant_count": 10,
        "horizon_days": 30,
        "enable_emergent_demand": True
    },
    WorldProfileV14.DEV: {
        "customer_count": 5000,
        "merchant_count": 50,
        "horizon_days": 30,
        "enable_emergent_demand": True
    },
    WorldProfileV14.STANDARD: {
        "customer_count": 25000,
        "merchant_count": 250,
        "horizon_days": 90,
        "enable_emergent_demand": True
    },
    WorldProfileV14.LARGE: {
        "customer_count": 100000,
        "merchant_count": 1000,
        "horizon_days": 180,
        "enable_emergent_demand": True
    },
    WorldProfileV14.CIVILIZATION: {
        "customer_count": 1000000,
        "merchant_count": 5000,
        "horizon_days": 365,
        "enable_emergent_demand": True
    }
}

class WorldConfigV14(BaseModel):
    profile: WorldProfileV14 = WorldProfileV14.DEV
    customer_count: int = 5000
    merchant_count: int = 50
    horizon_days: int = 30
    enable_emergent_demand: bool = True
    storage_dir: str = "d:/Work Space/Project/Ultron/synthetic_payment_universe/datasets_v14"

    @classmethod
    def from_profile(cls, profile: WorldProfileV14, storage_dir: Optional[str] = None) -> "WorldConfigV14":
        s = PROFILE_SETTINGS_V14.get(profile, PROFILE_SETTINGS_V14[WorldProfileV14.DEV])
        cfg = cls(
            profile=profile,
            customer_count=s["customer_count"],
            merchant_count=s["merchant_count"],
            horizon_days=s["horizon_days"],
            enable_emergent_demand=s["enable_emergent_demand"]
        )
        if storage_dir:
            cfg.storage_dir = storage_dir
        return cfg
