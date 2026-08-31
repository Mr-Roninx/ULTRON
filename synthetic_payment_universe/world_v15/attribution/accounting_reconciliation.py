from typing import Dict, Any, List

class AccountingReconciliationEngine:
    """
    Prevents double counting and verifies that incremental revenue cannot exceed gross settled transactions.
    """
    @staticmethod
    def verify_conservation(
        gross_settled_volume: float,
        direct_incremental: float,
        natural_recovery: float,
        outstanding_exposure: float
    ) -> Tuple[bool, str]:
        # 1. Total recovery cannot exceed outstanding exposure
        if (direct_incremental + natural_recovery) > (outstanding_exposure + 1e-4):
            return False, f"Recovery violation: {direct_incremental + natural_recovery} > {outstanding_exposure}"

        # 2. Direct incremental cannot exceed gross settled
        if direct_incremental > (gross_settled_volume + 1e-4):
            return False, f"Incremental revenue violation: {direct_incremental} > {gross_settled_volume}"

        return True, "CONSERVATION_VERIFIED"
