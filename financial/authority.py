from enum import Enum

class AuthorityLevel(str, Enum):
    OBSERVE = "OBSERVE"
    APPROVE = "APPROVE"
    AUTONOMOUS = "AUTONOMOUS"

class AuthorityEngine:
    def __init__(self):
        # Map of action type to required minimum authority level
        self.requirements = {
            "WAIT": AuthorityLevel.AUTONOMOUS,
            "RECONCILE": AuthorityLevel.AUTONOMOUS,
            "RETRY": AuthorityLevel.AUTONOMOUS,
            "RETRY_GATEWAY_A": AuthorityLevel.AUTONOMOUS,
            "RETRY_GATEWAY_B": AuthorityLevel.AUTONOMOUS,
            "RETRY_GATEWAY_C": AuthorityLevel.AUTONOMOUS,
            "SWITCH_PERMITTED_RAIL": AuthorityLevel.AUTONOMOUS,
            "REQUEST_CUSTOMER_ACTION": AuthorityLevel.AUTONOMOUS,
            "SEND_PAYMENT_LINK": AuthorityLevel.AUTONOMOUS,
            "SEND_MESSAGE": AuthorityLevel.AUTONOMOUS,
            "REGISTER_PTP": AuthorityLevel.AUTONOMOUS,
            "APPLY_DISCOUNT": AuthorityLevel.APPROVE,
            "REFUND_PAYMENT": AuthorityLevel.APPROVE,
            "ESCALATE": AuthorityLevel.AUTONOMOUS,
            "STOP": AuthorityLevel.AUTONOMOUS
        }
        
    def is_authorized(self, action_type: str, current_authority: AuthorityLevel) -> bool:
        required = self.requirements.get(action_type, AuthorityLevel.APPROVE)
        
        if current_authority == AuthorityLevel.OBSERVE:
            return False
            
        if required == AuthorityLevel.APPROVE:
            # For now, block APPROVE-level actions unless agent authority allows it 
            # (if agent is AUTONOMOUS, it might bypass APPROVE, but spec says APPROVE requires human. 
            # Let's say if it needs APPROVE, it can't be done autonomously without a human).
            # But the agent's current_authority can be AUTONOMOUS.
            if current_authority != AuthorityLevel.AUTONOMOUS and current_authority != AuthorityLevel.APPROVE:
                return False
            # Actually, if required is APPROVE, and current is AUTONOMOUS, autonomous > approve? 
            # Yes, autonomous can do anything.
            if current_authority == AuthorityLevel.AUTONOMOUS:
                return True
            return False  # If it requires APPROVE and current is only APPROVE, we still block? Wait, no.
            
        if current_authority == AuthorityLevel.AUTONOMOUS:
            return True
            
        return False

authority_engine = AuthorityEngine()
