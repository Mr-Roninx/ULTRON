from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field

class FatigueThreshold(str, Enum):
    NORMAL = "NORMAL"         # [0.00, 0.40)
    ELEVATED = "ELEVATED"     # [0.40, 0.65)
    HIGH = "HIGH"             # [0.65, 0.85)
    CRITICAL = "CRITICAL"     # [0.85, 1.00]

class LongHorizonFatigueState(BaseModel):
    instantaneous: float = 0.0
    rolling_24h: float = 0.0
    rolling_7d: float = 0.0
    cumulative_contacts: int = 0
    last_contact_time: int = 1760000000

class CustomerFatigueModel:
    """
    Simulates multi-horizon customer fatigue dynamics and behavioral thresholds.
    """
    @staticmethod
    def get_threshold(fatigue: float) -> FatigueThreshold:
        if fatigue >= 0.85:
            return FatigueThreshold.CRITICAL
        elif fatigue >= 0.65:
            return FatigueThreshold.HIGH
        elif fatigue >= 0.40:
            return FatigueThreshold.ELEVATED
        return FatigueThreshold.NORMAL

    @staticmethod
    def apply_contact(state: LongHorizonFatigueState, delta: float, now: int):
        state.instantaneous = min(1.0, round(state.instantaneous + delta, 3))
        state.rolling_24h = min(1.0, round(state.rolling_24h + delta, 3))
        state.rolling_7d = min(1.0, round(state.rolling_7d + delta, 3))
        state.cumulative_contacts += 1
        state.last_contact_time = now

    @staticmethod
    def decay_fatigue(state: LongHorizonFatigueState, days: float):
        factor_24h = 0.50 ** days
        factor_7d = 0.85 ** days
        state.instantaneous = max(0.0, round(state.instantaneous * factor_24h, 3))
        state.rolling_24h = max(0.0, round(state.rolling_24h * factor_24h, 3))
        state.rolling_7d = max(0.0, round(state.rolling_7d * factor_7d, 3))
