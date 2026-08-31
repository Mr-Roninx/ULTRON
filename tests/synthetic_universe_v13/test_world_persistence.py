import os
import pytest
from synthetic_payment_universe.world_v13.cli.create import create_economic_civilization

def test_world_persistence(tmp_path):
    w = create_economic_civilization(master_seed=123, profile_name="tiny", storage_dir=str(tmp_path))
    assert os.path.exists(w.db_path)
    assert len(w.customers) == 100
    assert len(w.merchants) == 10
