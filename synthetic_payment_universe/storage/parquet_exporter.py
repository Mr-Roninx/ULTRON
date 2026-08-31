import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel

class UniverseParquetExporter:
    """
    Exports synthetic universe datasets to standard Parquet format for high-throughput ML pipelines.
    Falls back gracefully to structured JSON/JSONL if pyarrow/pandas is unavailable in the environment.
    """
    @staticmethod
    def export_records(filepath: str, records: List[Any]):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        dict_records = [
            r.model_dump() if isinstance(r, BaseModel) else (r if isinstance(r, dict) else r.__dict__)
            for r in records
        ]

        try:
            import pandas as pd
            df = pd.DataFrame(dict_records)
            df.to_parquet(filepath, engine="auto", compression="snappy")
        except Exception:
            # Fallback to json archive
            fallback_path = filepath.replace(".parquet", ".json")
            with open(fallback_path, "w", encoding="utf-8") as f:
                json.dump(dict_records, f, indent=2)
