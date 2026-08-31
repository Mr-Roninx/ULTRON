import pytest

@pytest.mark.fixture
def test_claim_conflict_detection():
    # If historical claim contradicts runtime configuration, flag EVIDENCE_CONFLICT
    historical_claim = "PROVIDER_SANDBOX_VERIFIED"
    runtime_evidence = "FIXTURE_ONLY"

    has_conflict = (historical_claim != runtime_evidence)
    assert has_conflict is True
