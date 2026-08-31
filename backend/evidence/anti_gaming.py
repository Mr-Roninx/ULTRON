import os
import re
from typing import Dict, Any, List

SUSPICIOUS_PATTERNS = [
    (r"if\s+seed\s*==\s*\d+", "HARDCODED_SEED_BRANCH"),
    (r"if\s+customer_id\s*==\s*['\"]c_", "HARDCODED_CUSTOMER_BRANCH"),
    (r"if\s+scenario\s*==\s*['\"]", "HARDCODED_SCENARIO_BRANCH"),
    (r"recovery_rate\s*=\s*0\.\d{3,}", "HARDCODED_METRIC_OVERRIDE"),
    (r"future_recovery|actual_recovery", "POTENTIAL_LOOKAHEAD_LEAKAGE")
]

def audit_repository_for_gaming(root_dir: str = ".") -> Dict[str, Any]:
    """
    Scans codebase for benchmark manipulation, hardcoded seed overrides, or future-leakage anti-patterns.
    Distinguishes legitimate test fixtures from production manipulation.
    """
    scanned_files = 0
    flagged_entries: List[Dict[str, Any]] = []

    target_dirs = ["backend", "simulator", "financial", "memory", "evaluator"]
    
    for tdir in target_dirs:
        full_dir = os.path.join(root_dir, tdir)
        if not os.path.exists(full_dir):
            continue

        for root, _, files in os.walk(full_dir):
            for fname in files:
                if not fname.endswith(".py") or "anti_gaming" in fname.lower():
                    continue
                fpath = os.path.join(root, fname)
                scanned_files += 1

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                except Exception:
                    continue

                for line_no, line in enumerate(lines, 1):
                    # Ignore comments
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue

                    for pattern, label in SUSPICIOUS_PATTERNS:
                        if re.search(pattern, line):
                            # Classify whether it is in an adversarial firewall check vs actual gaming
                            is_firewall = "firewall" in fpath.lower() or "firewall" in line.lower()
                            is_test_fixture = "mock" in fpath.lower() or "test" in fpath.lower() or "audit" in fpath.lower()

                            classification = "LEGITIMATE_FIREWALL_RULE" if is_firewall else (
                                "LEGITIMATE_TEST_FIXTURE" if is_test_fixture else "FLAGGED_FOR_REVIEW"
                            )

                            flagged_entries.append({
                                "file": os.path.relpath(fpath, root_dir).replace("\\", "/"),
                                "line": line_no,
                                "pattern": label,
                                "snippet": stripped[:80],
                                "classification": classification
                            })

    # True gaming is present only if an unclassified FLAGGED_FOR_REVIEW item exists outside test/firewall components
    gaming_detected = any(e["classification"] == "FLAGGED_FOR_REVIEW" for e in flagged_entries)

    return {
        "total_files_scanned": scanned_files,
        "flagged_entries_count": len(flagged_entries),
        "gaming_detected": gaming_detected,
        "flagged_entries": flagged_entries
    }
