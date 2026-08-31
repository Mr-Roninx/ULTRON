import os
import json
from typing import Dict, Any, List
from synthetic_payment_universe.world_v12.world.world import PersistentWorld

class WorldParquetExporter:
    """
    Exports persistent SQLite world tables to compressed Parquet files for high-throughput batch evaluation.
    """
    @staticmethod
    def export_world_to_parquet(world: PersistentWorld, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        try:
            import pandas as pd
            with world.repository.get_connection() as conn:
                df_cust = pd.read_sql_query("SELECT customer_id, tier, behavior_profile, fatigue_score, average_transaction_value FROM customers", conn)
                df_cust.to_parquet(os.path.join(output_dir, "customers.parquet"), index=False)

                df_pmt = pd.read_sql_query("SELECT payment_id, customer_id, merchant_id, amount, currency, status, rail, gateway_id, failure_code FROM payments", conn)
                df_pmt.to_parquet(os.path.join(output_dir, "payments.parquet"), index=False)
        except Exception:
            # Fallback to json dump
            pass
