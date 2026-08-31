import pytest
from synthetic_payment_universe.world_v12.causal.causal_graph import StructuralCausalGraph

def test_causal_lineage_and_upstream_queries():
    dag = StructuralCausalGraph()
    upstream = dag.get_upstream_causes("PaymentOutcome")
    assert "GatewayHealth" in upstream

    downstream = dag.get_downstream_effects("ULTRONAction")
    assert "CustomerResponse" in downstream
    assert "CommunicationFatigue" in downstream
