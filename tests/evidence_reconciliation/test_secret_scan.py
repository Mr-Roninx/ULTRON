import pytest
import os
import json

@pytest.mark.fixture
def test_zero_secrets_in_reconciled_artifacts():
    reconciled_dir = "d:/Work Space/Project/Ultron/results/phase20"
    if os.path.exists(reconciled_dir):
        for fname in os.listdir(reconciled_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(reconciled_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                    assert "sk_live_" not in content
                    assert "rzp_live_" not in content
                    assert "whsec_live_" not in content
