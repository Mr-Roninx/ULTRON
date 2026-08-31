import pytest
from synthetic_payment_universe.world_v13.causal.lineage import causal_lineage_engine, RecoveryProvenance

def test_explain_recovery_provenance():
    prov = RecoveryProvenance(
        payment_id="pmt_prov_1",
        failure_timestamp=1760000000,
        failure_code="91",
        observed_by_agent_timestamp=1760000100,
        diagnosis="TRANSIENT_ISSUER_TIMEOUT",
        selected_action="WAIT",
        action_execution_timestamp=1760000150,
        recovery_timestamp=1760007200,
        recovered_amount=45000.0,
        settlement_batch_id="stl_batch_1",
        ledger_entry_id="ent_1",
        customer_relationship_delta=0.05
    )
    causal_lineage_engine.record_provenance(prov)

    explanation = causal_lineage_engine.explain_recovery("pmt_prov_1")
    assert explanation is not None
    assert explanation["recovered_amount"] == 45000.0
    assert explanation["selected_action"] == "WAIT"
