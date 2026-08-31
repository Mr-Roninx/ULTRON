import pytest
from synthetic_payment_universe.world_v13.scheduler.capacity_guard import AgentCapacityGuard

def test_agent_capacity_guard_bounds():
    guard = AgentCapacityGuard(max_actions_per_customer_per_day=2)
    now = 1760000000

    assert guard.can_execute_action("c_1", now) is True
    guard.record_action("c_1", now)

    assert guard.can_execute_action("c_1", now + 100) is True
    guard.record_action("c_1", now + 100)

    # 3rd action in same 24h period blocked
    assert guard.can_execute_action("c_1", now + 200) is False

    # After 24h -> permitted
    assert guard.can_execute_action("c_1", now + 86500) is True
