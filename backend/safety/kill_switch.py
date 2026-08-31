from typing import Dict, Set

class KillSwitchController:
    """
    Emergency circuit breaker system with global and customer-level isolation.
    Fail-closed: completely blocks autonomous action execution when activated.
    """
    def __init__(self):
        self.global_active = False
        self.disabled_customers: Set[str] = set()

    def activate_global(self):
        self.global_active = True

    def deactivate_global(self):
        self.global_active = False

    def disable_customer(self, customer_id: str):
        self.disabled_customers.add(customer_id)

    def enable_customer(self, customer_id: str):
        self.disabled_customers.discard(customer_id)

    def is_action_allowed(self, customer_id: str) -> bool:
        if self.global_active:
            return False
        if customer_id in self.disabled_customers:
            return False
        return True

    def reset(self):
        self.global_active = False
        self.disabled_customers.clear()

kill_switch_controller = KillSwitchController()
