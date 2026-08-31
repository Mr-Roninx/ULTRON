import os
import sqlite3

class CivilizationRestoreEngine:
    """
    Restores world database from atomic snapshot.
    """
    @staticmethod
    def restore(snapshot_path: str, target_db_path: str):
        os.makedirs(os.path.dirname(target_db_path), exist_ok=True)
        src = sqlite3.connect(snapshot_path)
        dst = sqlite3.connect(target_db_path)
        src.backup(dst)
        dst.close()
        src.close()
