class CircuitBreakerTripped(Exception):
    pass

class CircuitBreaker:
    def __init__(self, max_iterations: int = 50, max_replans: int = 5, max_identical_failures: int = 3):
        self.max_iterations = max_iterations
        self.max_replans = max_replans
        self.max_identical_failures = max_identical_failures
        
    def check(self, iteration_count: int, replan_count: int, identical_failures: int = 0):
        if iteration_count >= self.max_iterations:
            raise CircuitBreakerTripped(f"Max iterations ({self.max_iterations}) exceeded.")
        if replan_count >= self.max_replans:
            raise CircuitBreakerTripped(f"Max replan loops ({self.max_replans}) exceeded.")
        if identical_failures >= self.max_identical_failures:
            raise CircuitBreakerTripped(f"Max identical failures ({self.max_identical_failures}) exceeded.")
        return True

circuit_breaker = CircuitBreaker()
