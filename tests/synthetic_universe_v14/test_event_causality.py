import pytest
from synthetic_payment_universe.world_v14.causal.structural_dag import PopulationCausalDAG

def test_causal_lineage_dag():
    dag = PopulationCausalDAG()
    upstream = dag.get_upstream_causes("PaymentFailures")
    assert "GatewayCongestion" in upstream

    downstream = dag.get_downstream_effects("ULTRONIntervention")
    assert "ContactFatigue" in downstream
    assert "CustomerResponse" in downstream
