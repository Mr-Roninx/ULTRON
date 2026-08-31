from typing import Optional

class AdversarialVirtualClock:
    """
    Authoritative monotonic virtual clock for SWU-1.5.
    """
    def __init__(self, start_timestamp: int = 1760000000):
        self._current_time: int = start_timestamp
        self._start_time: int = start_timestamp

    def now(self) -> int:
        return self._current_time

    def start_time(self) -> int:
        return self._start_time

    def elapsed_days(self) -> float:
        return (self._current_time - self._start_time) / 86400.0

    def advance_to(self, target_timestamp: int):
        if target_timestamp < self._current_time:
            raise ValueError(f"Monotonic clock violation: {target_timestamp} < {self._current_time}")
        self._current_time = target_timestamp

    def advance_days(self, days: int):
        self.advance_to(self._current_time + (days * 86400))

    def reset(self, new_timestamp: Optional[int] = None):
        t = new_timestamp if new_timestamp is not None else 1760000000
        self._current_time = t
        self._start_time = t

adversarial_clock = AdversarialVirtualClock()
