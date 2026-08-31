import hashlib
import json
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class WorldIdentity(BaseModel):
    world_id: str
    world_version: str = "ULTRON-SWU-1.2"
    master_seed: int
    partition_name: str = "dev"
    created_at: int = Field(default_factory=lambda: int(time.time()))
    simulation_start: int = 1760000000
    simulation_end: int = 1760000000 + (30 * 86400) # 30 days horizon
    current_time: int = 1760000000
    schema_version: str = "1.2.0"
    generator_version: str = "1.2.0"
    configuration_hash: str = ""

    def compute_configuration_hash(self, config_dict: Dict[str, Any]) -> str:
        serialized = json.dumps(config_dict, sort_keys=True)
        self.configuration_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
        return self.configuration_hash
