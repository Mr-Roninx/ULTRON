import pytest
from backend.evidence.evidence_graph import EvidenceGraph

@pytest.mark.fixture
def test_evidence_graph_connectivity():
    graph = EvidenceGraph(correlation_id="corr_reconciled_demo_01")
    graph.add_node("EXTERNAL_PROVIDER_EVENT", "evt_01", "TEST_FIXTURE", "FIXTURE")
    graph.add_node("WEBHOOK_RECEIVED", "evt_02", "APPLICATION", "FIXTURE")
    graph.add_node("ACTION_AUTHORITY", "evt_03", "APPLICATION", "FIXTURE")
    graph.add_node("PROVIDER_ACTION", "evt_04", "APPLICATION", "FIXTURE")
    graph.add_node("RECONCILIATION", "evt_05", "APPLICATION", "FIXTURE")
    graph.add_node("LEDGER", "evt_06", "APPLICATION", "FIXTURE")

    summary = graph.get_provenance_summary()
    assert summary["all_connected"] is True
    assert summary["total_nodes"] == 6
