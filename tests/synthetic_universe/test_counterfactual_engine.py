import pytest
from synthetic_payment_universe.generator.seeds import MasterSeedManager
from synthetic_payment_universe.schema.entities import Customer, Payment, GroundTruthOutcome
from synthetic_payment_universe.counterfactual.counterfactual_engine import UniverseCounterfactualEngine
from synthetic_payment_universe.validators.counterfactual_validator import UniverseCounterfactualValidator

def test_counterfactual_branch_evaluation():
    mgr = MasterSeedManager(42)
    engine = UniverseCounterfactualEngine(mgr)

    cust = Customer(customer_id="c_cf_1", name="CF Test Corp", segment="B2B_ENTERPRISE")
    pmt = Payment(payment_id="p_cf_1", customer_id=cust.customer_id, merchant_id="m_1", amount=24700.0, failure_code="91")
    truth = GroundTruthOutcome(
        truth_id="gt_cf_1",
        payment_id=pmt.payment_id,
        true_root_cause="ISSUER_CORE_BANKING_REBOOT",
        eventual_payment=True,
        eventual_recovery_amount=24700.0,
        natural_recovery_timestamp=1760007200,
        oracle_optimal_action="WAIT"
    )

    outcomes = engine.evaluate_counterfactual_branches(
        decision_point_id="dp_1",
        payment=pmt,
        customer=cust,
        ground_truth=truth,
        current_gateway_health=0.95
    )

    assert len(outcomes) == 5
    is_valid, errs = UniverseCounterfactualValidator.validate_counterfactual_set(outcomes)
    assert is_valid is True
    assert len(errs) == 0

    actions = [o.action_type for o in outcomes]
    assert "WAIT" in actions
    assert "RETRY" in actions
    assert "SEND_PAYMENT_LINK" in actions
