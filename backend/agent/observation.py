class PredictionError:
    def __init__(self, expected: float, observed: float):
        self.expected = expected
        self.observed = observed

    def calculate(self) -> float:
        if self.expected == 0:
            return 1.0 if self.observed != 0 else 0.0
        return abs(self.observed - self.expected) / abs(self.expected)

class ObservationEngine:
    def __init__(self, soft_error_threshold: float = 0.2, hard_error_threshold: float = 0.5):
        self.soft_error_threshold = soft_error_threshold
        self.hard_error_threshold = hard_error_threshold

    def evaluate(self, expected_value: float, observed_value: float, actual_status: str) -> dict:
        """
        Returns a dictionary with 'requires_replan' and 'error_type' (None, 'SOFT', 'HARD', 'STATE_FAILURE')
        """
        # If the action resulted in a hard failure state (e.g. FAILED instead of SETTLED)
        if actual_status == "FAILED":
            return {"requires_replan": True, "error_type": "STATE_FAILURE"}
            
        error = PredictionError(expected_value, observed_value).calculate()
        
        if error > self.hard_error_threshold:
            return {"requires_replan": True, "error_type": "HARD"}
        elif error > self.soft_error_threshold:
            return {"requires_replan": False, "error_type": "SOFT"}
            
        return {"requires_replan": False, "error_type": None}

observer = ObservationEngine()
