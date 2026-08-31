from typing import Dict, Any
from simulator.clock import clock
from datetime import datetime

class FutureInformationLeakageError(Exception):
    pass

class TemporalObservationFirewall:
    @staticmethod
    def sanitize_agent_context(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scrub any future information from the context.
        Raises FutureInformationLeakageError if the context contains
        data originating from a time > clock.now().
        """
        now = clock.now()
        
        # Traverse dictionary and check any 'timestamp' or 'created_at' fields
        def _check_dict(d: Any, path: str):
            if isinstance(d, dict):
                for k, v in d.items():
                    if k in ["timestamp", "created_at", "updated_at", "scheduled_at", "occurred_at"]:
                        if isinstance(v, (int, float)) and v > now:
                            raise FutureInformationLeakageError(f"Future information leak detected at {path}.{k} = {v} (current time: {now})")
                    
                    if k in ["control_outcome", "treatment_outcome", "actual_recovery", "incremental_recovery"]:
                        raise FutureInformationLeakageError(f"Future information leak detected at {path}.{k}")
                        
                    if isinstance(v, (dict, list)):
                        _check_dict(v, f"{path}.{k}")
            elif isinstance(d, list):
                for i, item in enumerate(d):
                    _check_dict(item, f"{path}[{i}]")
                    
        _check_dict(context, "context")
        return context

    @staticmethod
    def verify_time_boundary(timestamp: int) -> None:
        if timestamp > clock.now():
            raise FutureInformationLeakageError(f"Cannot access information from future timestamp {timestamp}")
            
    @staticmethod
    def enforce(context: Dict[str, Any]) -> None:
        TemporalObservationFirewall.sanitize_agent_context(context)

firewall = TemporalObservationFirewall()
FutureInformationFirewall = TemporalObservationFirewall
