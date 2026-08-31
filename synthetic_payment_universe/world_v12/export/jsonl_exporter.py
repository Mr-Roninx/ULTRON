import os
import json
from typing import List, Dict, Any, Generator
from synthetic_payment_universe.world_v12.world.world import PersistentWorld

class WorldJSONLExporter:
    """
    Streams world records out to JSON Lines files with zero memory bottlenecks.
    """
    @staticmethod
    def export_world_to_jsonl(world: PersistentWorld, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        with world.repository.get_connection() as conn:
            c = conn.cursor()
            # Customers
            with open(os.path.join(output_dir, "customers.jsonl"), "w", encoding="utf-8") as f:
                c.execute("SELECT raw_json FROM customers")
                for row in c:
                    f.write(row[0] + "\n")

            # Payments
            with open(os.path.join(output_dir, "payments.jsonl"), "w", encoding="utf-8") as f:
                c.execute("SELECT raw_json FROM payments")
                for row in c:
                    f.write(row[0] + "\n")

            # Events
            with open(os.path.join(output_dir, "events.jsonl"), "w", encoding="utf-8") as f:
                c.execute("SELECT event_id, event_type, entity_id, timestamp, visibility, causal_parent_id, payload_json FROM events")
                for row in c:
                    evt_dict = {
                        "event_id": row[0],
                        "event_type": row[1],
                        "entity_id": row[2],
                        "timestamp": row[3],
                        "visibility": row[4],
                        "causal_parent_id": row[5],
                        "payload": json.loads(row[6]) if row[6] else {}
                    }
                    f.write(json.dumps(evt_dict) + "\n")
