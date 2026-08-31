import pytest
from synthetic_payment_universe.generator.universe_builder import PARTITION_SEED_RANGES

def test_partition_seed_ranges_are_disjoint():
    ranges = list(PARTITION_SEED_RANGES.values())
    for i in range(len(ranges)):
        start_i, end_i = ranges[i]
        for j in range(i + 1, len(ranges)):
            start_j, end_j = ranges[j]
            # Verify no overlap
            overlap = max(0, min(end_i, end_j) - max(start_i, start_j) + 1)
            assert overlap == 0, f"Partition overlap detected between {ranges[i]} and {ranges[j]}"
