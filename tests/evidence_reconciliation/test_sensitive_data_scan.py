import pytest
import os

@pytest.mark.fixture
def test_zero_raw_pan_or_cvv_in_results():
    results_dir = "d:/Work Space/Project/Ultron/results/phase20"
    if os.path.exists(results_dir):
        for fname in os.listdir(results_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(results_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    assert '"cvv"' not in content
                    assert '"card_cvv"' not in content
                    assert '"bank_password"' not in content
