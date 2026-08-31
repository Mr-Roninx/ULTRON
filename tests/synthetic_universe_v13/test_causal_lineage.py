import pytest
from synthetic_payment_universe.world_v13.causal.graph import CivilizationCausalGraph

def test_causal_dag_queries():
    dag = CivilizationCausalGraph()
    upstream = dag.get_upstream_causes("AuthorizationOutcome")
    assert "GatewayHealth" in upstream

    downstream = dag.get_downstream_effects("ULTRONIntervention")
    assert "CommunicationFatigue" in downstream
