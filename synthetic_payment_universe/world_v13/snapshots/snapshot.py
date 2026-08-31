import os
import sqlite3

class CivilizationSnapshotEngine:
    """
    Creates atomic SQLite snapshots of the economic world database.
    """
    @staticmethod
    def snapshot(source_db_path: str, snapshot_path: str) -> str:
        os.makedirs(os.path.dirname(snapshot_path), exist_ok=True)
        src = sqlite3.connect(source_db_path)
        dst = sqlite3.connect(snapshot_path)
        src.backup(dst)
        dst.close()
        src.close()
        return snapshot_path
