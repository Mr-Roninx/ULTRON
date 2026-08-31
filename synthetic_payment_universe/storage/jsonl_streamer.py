import os
import json
from typing import List, Dict, Any, Generator
from pydantic import BaseModel

class JSONLEventStreamer:
    """
    Streaming JSON Lines read/write engine for large-scale event datasets.
    Zero memory bottleneck: writes and yields records iteratively.
    """
    @staticmethod
    def write_records(filepath: str, records: List[Any], mode: str = "w"):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, mode, encoding="utf-8") as f:
            for r in records:
                if isinstance(r, BaseModel):
                    f.write(r.model_dump_json() + "\n")
                elif isinstance(r, dict):
                    f.write(json.dumps(r) + "\n")
                else:
                    f.write(json.dumps(r.__dict__) + "\n")

    @staticmethod
    def stream_records(filepath: str) -> Generator[Dict[str, Any], None, None]:
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str:
                    yield json.loads(line_str)
