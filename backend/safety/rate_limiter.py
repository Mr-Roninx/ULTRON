from typing import Dict, List, Any
from simulator.clock import clock

class ActionRateLimiter:
    """
    Enforces frequency caps per customer and action type within moving time windows.
    """
    DEFAULT_LIMITS = {
        "RETRY": 3,
        "RETRY_GATEWAY_A": 3,
        "RETRY_GATEWAY_B": 3,
        "SEND_PAYMENT_LINK": 2,
        "SEND_MESSAGE": 2,
        "APPLY_DISCOUNT": 1
    }

    def __init__(self):
        self._action_log: Dict[str, List[int]] = {}

    def check_and_record(self, customer_id: str, action_type: str, window_seconds: int = 86400) -> bool:
        now = clock.now()
        key = f"{customer_id}:{action_type}"
        if key not in self._action_log:
            self._action_log[key] = []

        # Filter outside window
        valid_log = [t for t in self._action_log[key] if (now - t) <= window_seconds]
        self._action_log[key] = valid_log

        max_allowed = self.DEFAULT_LIMITS.get(action_type, 3)
        if len(valid_log) >= max_allowed:
            return False

        self._action_log[key].append(now)
        return True

    def reset(self):
        self._action_log.clear()

action_rate_limiter = ActionRateLimiter()
