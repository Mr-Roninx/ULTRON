import pytest
from synthetic_payment_universe.world_v14.economy.feedback_loops import EconomicFeedbackLoops

def test_relationship_feedback_loop_a():
    initial_trust = 0.80
    t_success = EconomicFeedbackLoops.apply_loop_a_relationship(initial_trust, recovery_success=True)
    t_failure = EconomicFeedbackLoops.apply_loop_a_relationship(initial_trust, recovery_success=False)

    assert t_success > initial_trust
    assert t_failure < initial_trust
