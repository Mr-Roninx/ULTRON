import os
import pytest
from synthetic_payment_universe.world_v13.cli.create import create_economic_civilization

def test_atomic_world_snapshot(tmp_path):
    w = create_economic_civilization(master_seed=888, profile_name="tiny", storage_dir=str(tmp_path))
    snap_path = w.snapshot()
    assert os.path.exists(snap_path)
