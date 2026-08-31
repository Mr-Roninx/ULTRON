import pytest
from synthetic_payment_universe.world_v15.cli.create import create_adversarial_world

def test_large_scale_batch_creation(tmp_path):
    w = create_adversarial_world(master_seed=888, profile_name="tiny", storage_dir=str(tmp_path))
    assert len(w.customers) == 100
    assert len(w.payments) == 100
    with w.repository.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM payments WHERE status = 'SETTLED'")
        settled_cnt = c.fetchone()[0]
        assert settled_cnt > 0
