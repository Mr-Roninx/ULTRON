import pytest
from simulator.clock import clock
from synthetic_payment_universe.oracle.hidden_oracle import hidden_oracle
from synthetic_payment_universe.schema.entities import GroundTruthOutcome
from synthetic_payment_universe.observation.firewall import UniverseObservationFirewall

def test_ground_truth_oracle_isolation():
    hidden_oracle.reset()
    now = 1760000000
    clock.reset(now)

    gt = GroundTruthOutcome(
        truth_id="gt_iso_1",
        payment_id="p_iso_1",
        true_root_cause="SWITCH_CORE_REBOOT",
        eventual_payment=True,
        eventual_recovery_amount=24700.0,
        oracle_optimal_action="WAIT",
        created_at=now
    )
    hidden_oracle.register_ground_truth(gt)

    # Oracle has the ground truth
    assert hidden_oracle.get_ground_truth("p_iso_1").true_root_cause == "SWITCH_CORE_REBOOT"

    # Firewall completely rejects passing ground truth fields to agent
    sanitized = UniverseObservationFirewall.sanitize_for_agent(gt.model_dump(), 1760000000)
    assert "true_root_cause" not in sanitized
    assert "oracle_optimal_action" not in sanitized
