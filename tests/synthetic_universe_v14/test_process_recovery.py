import os
import pytest
from synthetic_payment_universe.world_v14.cli.create import create_emergent_population_world
from synthetic_payment_universe.world_v14.repository import SQLiteEmergentRepository

def test_process_interruption_recovery(tmp_path):
    w = create_emergent_population_world(master_seed=888, profile_name="tiny", storage_dir=str(tmp_path))
    # Reopen DB to simulate process crash & restart
    new_repo = SQLiteEmergentRepository(w.db_path)
    with new_repo.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM customers")
        assert c.fetchone()[0] == 100
