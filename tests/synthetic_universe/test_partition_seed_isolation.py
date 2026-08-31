import pytest
from synthetic_payment_universe.generator.seeds import MasterSeedManager, PARTITION_SEED_RANGES
from synthetic_payment_universe.validators.seed_isolation_validator import UniverseSeedIsolationValidator

def test_partition_seed_isolation_and_domain_disjointness():
    # 1. Verify all partition ranges are strictly disjoint
    is_valid, errs = UniverseSeedIsolationValidator.validate_partition_domains()
    assert is_valid is True
    assert len(errs) == 0

    # 2. Verify partition master seed is mapped within its partition range
    mgr_dev = MasterSeedManager(12345, partition_name="dev")
    assert PARTITION_SEED_RANGES["dev"][0] <= mgr_dev.partition_seed <= PARTITION_SEED_RANGES["dev"][1]

    mgr_eval = MasterSeedManager(12345, partition_name="evaluation")
    assert PARTITION_SEED_RANGES["evaluation"][0] <= mgr_eval.partition_seed <= PARTITION_SEED_RANGES["evaluation"][1]

    assert mgr_dev.partition_seed != mgr_eval.partition_seed

    # 3. Verify statistical independence
    is_rep, rep_errs = UniverseSeedIsolationValidator.verify_reproducibility_and_independence()
    assert is_rep is True
    assert len(rep_errs) == 0
