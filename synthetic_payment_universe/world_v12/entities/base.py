from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class WorldEntity(BaseModel):
    schema_version: str = "1.2.0"
    created_at: int = 1760000000
    updated_at: int = 1760000000
    metadata: Dict[str, Any] = Field(default_factory=dict)
