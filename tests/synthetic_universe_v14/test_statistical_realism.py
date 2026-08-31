import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def test_statistical_distribution_realism(tmp_path):
    w = create_emergent_population_world(master_seed=909, profile_name="tiny", storage_dir=str(tmp_path))
    with w.repository.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT AVG(amount), MIN(amount), MAX(amount) FROM payments")
        avg_amt, min_amt, max_amt = c.fetchone()
        assert min_amt > 0
        assert avg_amt > 2000
