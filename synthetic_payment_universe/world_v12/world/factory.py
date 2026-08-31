import os
import shutil
from typing import Optional
from synthetic_payment_universe.world_v12.world.identity import WorldIdentity
from synthetic_payment_universe.world_v12.world.config import WorldConfig, WorldProfile
from synthetic_payment_universe.world_v12.world.world import PersistentWorld
from synthetic_payment_universe.world_v12.state.repository import SQLiteWorldRepository

def create_world(
    master_seed: int = 12345,
    partition_name: str = "dev",
    profile: WorldProfile = WorldProfile.DEV,
    storage_dir: Optional[str] = None
) -> PersistentWorld:
    config = WorldConfig.from_profile(profile, storage_dir=storage_dir)
    world_id = f"world_{partition_name}_{master_seed}_{profile.value}"
    target_dir = os.path.join(config.storage_dir, world_id)
    os.makedirs(target_dir, exist_ok=True)
    db_path = os.path.join(target_dir, "world.db")

    identity = WorldIdentity(
        world_id=world_id,
        master_seed=master_seed,
        partition_name=partition_name
    )
    return PersistentWorld(identity=identity, config=config, db_path=db_path)

def load_world(db_path: str) -> Optional[PersistentWorld]:
    if not os.path.exists(db_path):
        return None
    repo = SQLiteWorldRepository(db_path)
    with repo.get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT world_id FROM world_metadata LIMIT 1")
        row = c.fetchone()
        if not row:
            return None
        meta = repo.load_world_metadata(row[0])
        if not meta:
            return None
        identity = WorldIdentity(
            world_id=meta["world_id"],
            master_seed=meta["master_seed"],
            partition_name=meta["partition_name"],
            created_at=meta["created_at"],
            simulation_start=meta["simulation_start"],
            simulation_end=meta["simulation_end"],
            current_time=meta["current_time"],
            schema_version=meta["schema_version"],
            configuration_hash=meta["configuration_hash"]
        )
        config = WorldConfig(**meta["config"])
        return PersistentWorld(identity=identity, config=config, db_path=db_path)

def snapshot_world(world: PersistentWorld) -> str:
    return world.snapshot()

def restore_world(snapshot_path: str, target_db_path: str) -> PersistentWorld:
    shutil.copy2(snapshot_path, target_db_path)
    loaded = load_world(target_db_path)
    if not loaded:
        raise ValueError(f"Failed to restore world from snapshot: {snapshot_path}")
    return loaded

def fork_world(source_world: PersistentWorld, fork_name: str) -> PersistentWorld:
    fork_db_path = f"{source_world.db_path}.fork_{fork_name}"
    shutil.copy2(source_world.db_path, fork_db_path)
    forked = load_world(fork_db_path)
    if not forked:
        raise ValueError(f"Failed to fork world {source_world.identity.world_id}")
    forked.identity.world_id = f"{source_world.identity.world_id}_fork_{fork_name}"
    return forked
