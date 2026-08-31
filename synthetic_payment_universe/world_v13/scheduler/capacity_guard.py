from typing import Dict

class AgentCapacityGuard:
    """
    Enforces bounded agent throughput to model realistic operational limits and prevent over-contacting.
    """
    def __init__(self, max_actions_per_hour: int = 50, max_actions_per_customer_per_day: int = 2):
        self.max_actions_per_hour = max_actions_per_hour
        self.max_actions_per_customer_per_day = max_actions_per_customer_per_day
        self.action_history: Dict[str, list] = {} # customer_id -> list of timestamps

    def can_execute_action(self, customer_id: str, current_timestamp: int) -> bool:
        times = self.action_history.get(customer_id, [])
        # Filter for past 24 hours
        recent_times = [t for t in times if current_timestamp - t <= 86400]
        self.action_history[customer_id] = recent_times
        return len(recent_times) < self.max_actions_per_customer_per_day

    def record_action(self, customer_id: str, timestamp: int):
        if customer_id not in self.action_history:
            self.action_history[customer_id] = []
        self.action_history[customer_id].append(timestamp)
