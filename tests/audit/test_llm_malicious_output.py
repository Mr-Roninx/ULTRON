import pytest
from backend.audit.live_llm_trace import execute_malicious_output_experiment
from financial.feasible_actions import feasible_action_engine
from financial.authority import AuthorityLevel

def test_malicious_llm_output_rejection():
    res = execute_malicious_output_experiment()
    assert res["all_unauthorized_actions_rejected"] is True
    assert res["verdict"] == "PROVEN"

def test_sql_and_mutation_injections_rejected():
    context = {
        "customer": {"id": "c_attacker", "segment": "B2B_ENTERPRISE"},
        "payment": {"id": "pmt_target", "amount": 1000.0}
    }
    dangerous_actions = [
        "DROP TABLE payments",
        "TRANSFER_MONEY",
        "DELETE_PAYMENT",
        "UPDATE_BALANCE",
        "BYPASS_POLICY"
    ]
    for act in dangerous_actions:
        feasible = feasible_action_engine.get_feasible_actions(context, 1.0, AuthorityLevel.AUTONOMOUS)
        assert act not in feasible
