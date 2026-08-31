import pytest
from backend.evidence.environment_truth import environment_truth_resolver, ResolvedEnvironment

@pytest.mark.fixture
def test_evidence_classification_rules():
    env, reason = environment_truth_resolver.resolve_environment("razorpay")
    # In absence of exported live environment keys, resolves conservatively to FIXTURE
    assert env in [ResolvedEnvironment.FIXTURE, ResolvedEnvironment.RAZORPAY_TEST]

    env_swu, _ = environment_truth_resolver.resolve_environment("swu")
    assert env_swu == ResolvedEnvironment.SWU
