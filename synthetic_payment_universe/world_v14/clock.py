from typing import Optional

class EmergentVirtualClock:
    """
    Deterministic virtual clock for ULTRON-SWU-1.4 Emergent Population Economy.
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
            raise ValueError(f"Cannot rewind virtual clock: {target_timestamp} < {self._current_time}")
        self._current_time = target_timestamp

    def advance_by(self, seconds: int):
        self.advance_to(self._current_time + seconds)

    def advance_days(self, days: int):
        self.advance_by(days * 86400)

    def reset(self, new_timestamp: Optional[int] = None):
        t = new_timestamp if new_timestamp is not None else 1760000000
        self._current_time = t
        self._start_time = t

emergent_clock = EmergentVirtualClock()
