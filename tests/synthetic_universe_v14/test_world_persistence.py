import os
import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world

def test_sqlite_persistence(tmp_path):
    w = create_emergent_population_world(master_seed=55, profile_name="tiny", storage_dir=str(tmp_path))
    assert os.path.exists(w.db_path)
    with w.repository.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM customers")
        cnt = c.fetchone()[0]
        assert cnt == 100
