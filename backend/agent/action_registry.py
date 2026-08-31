from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

class ActionDefinition(BaseModel):
    action_id: str
    description: str
    required_permissions: List[str] = Field(default_factory=list)
    financial_mutation_allowed: bool = False
    allowed_customer_tiers: List[str] = Field(default_factory=lambda: ["SMB", "B2B_MIDMARKET", "B2B_ENTERPRISE"])
    risk_class: str = "LOW" # LOW, MEDIUM, HIGH, CRITICAL
    policy_constraints: List[str] = Field(default_factory=list)
    execution_handler: str

class UnauthorizedActionError(Exception):
    pass

class ActionRegistry:
    """
    Authoritative Action Registry ensuring only validated, permissioned,
    non-financial-mutating actions can reach the Decision Authority and FSM.
    """
    def __init__(self):
        self._actions: Dict[str, ActionDefinition] = {}
        self._register_default_actions()

    def _register_default_actions(self):
        defaults = [
            ActionDefinition(
                action_id="WAIT",
                description="Temporal backoff awaiting bank/issuer recovery or customer schedule.",
                required_permissions=["AGENT_EXECUTE"],
                financial_mutation_allowed=False,
                risk_class="LOW",
                execution_handler="registry.execution.wait"
            ),
            ActionDefinition(
                action_id="RECONCILE",
                description="Query payment gateway API or bank ledger to verify final settlement status.",
                required_permissions=["GATEWAY_READ"],
                financial_mutation_allowed=False,
                risk_class="LOW",
                execution_handler="registry.execution.reconcile_payment"
            ),
            ActionDefinition(
                action_id="RETRY",
                description="Autonomous smart retry through current payment rail and gateway.",
                required_permissions=["PAYMENT_RETRY"],
                financial_mutation_allowed=False,
                risk_class="LOW",
                execution_handler="registry.execution.schedule_retry"
            ),
            ActionDefinition(
                action_id="RETRY_GATEWAY_A",
                description="Targeted retry through Gateway A (primary high-uptime rail).",
                required_permissions=["PAYMENT_RETRY"],
                financial_mutation_allowed=False,
                risk_class="LOW",
                execution_handler="registry.execution.schedule_retry"
            ),
            ActionDefinition(
                action_id="RETRY_GATEWAY_B",
                description="Targeted retry through Gateway B (secondary card/bank rail).",
                required_permissions=["PAYMENT_RETRY"],
                financial_mutation_allowed=False,
                risk_class="LOW",
                execution_handler="registry.execution.schedule_retry"
            ),
            ActionDefinition(
                action_id="RETRY_GATEWAY_C",
                description="Targeted retry through Gateway C (alternate ACH rail).",
                required_permissions=["PAYMENT_RETRY"],
                financial_mutation_allowed=False,
                risk_class="MEDIUM",
                execution_handler="registry.execution.schedule_retry"
            ),
            ActionDefinition(
                action_id="SWITCH_PERMITTED_RAIL",
                description="Switch to healthy alternative pre-authorized rail (e.g. Card -> UPI).",
                required_permissions=["RAIL_SWITCH"],
                financial_mutation_allowed=False,
                risk_class="MEDIUM",
                execution_handler="registry.execution.switch_permitted_rail"
            ),
            ActionDefinition(
                action_id="ALTERNATE_RAIL",
                description="Switch to alternate approved payment rail.",
                required_permissions=["RAIL_SWITCH"],
                financial_mutation_allowed=False,
                risk_class="MEDIUM",
                execution_handler="registry.execution.switch_permitted_rail"
            ),
            ActionDefinition(
                action_id="SEND_PAYMENT_LINK",
                description="Generate dynamic 1-click checkout invoice link sent via customer channel.",
                required_permissions=["COMMUNICATION_SEND"],
                financial_mutation_allowed=False,
                risk_class="MEDIUM",
                execution_handler="registry.execution.generate_payment_link"
            ),
            ActionDefinition(
                action_id="SEND_MESSAGE",
                description="Send respectful notification or payment reminder to customer contact.",
                required_permissions=["COMMUNICATION_SEND"],
                financial_mutation_allowed=False,
                risk_class="LOW",
                execution_handler="registry.execution.send_customer_message"
            ),
            ActionDefinition(
                action_id="EMAIL",
                description="Send email notification regarding pending invoice.",
                required_permissions=["COMMUNICATION_SEND"],
                financial_mutation_allowed=False,
                risk_class="LOW",
                execution_handler="registry.execution.send_customer_message"
            ),
            ActionDefinition(
                action_id="SMS",
                description="Send urgent SMS alert regarding payment authorization status.",
                required_permissions=["COMMUNICATION_SEND"],
                financial_mutation_allowed=False,
                risk_class="LOW",
                execution_handler="registry.execution.send_customer_message"
            ),
            ActionDefinition(
                action_id="REQUEST_CUSTOMER_ACTION",
                description="Request customer update expired credentials or authenticate 3DS.",
                required_permissions=["COMMUNICATION_SEND"],
                financial_mutation_allowed=False,
                risk_class="MEDIUM",
                execution_handler="registry.execution.send_customer_message"
            ),
            ActionDefinition(
                action_id="REGISTER_PTP",
                description="Register formal Promise-To-Pay agreement on scheduled future date.",
                required_permissions=["PTP_WRITE"],
                financial_mutation_allowed=False,
                risk_class="MEDIUM",
                execution_handler="registry.execution.register_ptp"
            ),
            ActionDefinition(
                action_id="PTP",
                description="Record Promise-To-Pay agreement.",
                required_permissions=["PTP_WRITE"],
                financial_mutation_allowed=False,
                risk_class="MEDIUM",
                execution_handler="registry.execution.register_ptp"
            ),
            ActionDefinition(
                action_id="APPLY_DISCOUNT",
                description="Apply bounded settlement incentive discount for enterprise recovery.",
                required_permissions=["DISCOUNT_APPLY"],
                financial_mutation_allowed=False,
                allowed_customer_tiers=["B2B_ENTERPRISE"],
                risk_class="HIGH",
                policy_constraints=["B2B_ENTERPRISE_ONLY", "MAX_DISCOUNT_BOUND"],
                execution_handler="registry.execution.apply_discount"
            ),
            ActionDefinition(
                action_id="REFUND_PAYMENT",
                description="Issue refund for duplicate or disputed payment.",
                required_permissions=["REFUND_AUTHORIZATION"],
                financial_mutation_allowed=False,
                risk_class="HIGH",
                execution_handler="registry.execution.refund_payment"
            ),
            ActionDefinition(
                action_id="ESCALATE",
                description="Escalate recovery opportunity to human finance representative.",
                required_permissions=["ESCALATE_HUMAN"],
                financial_mutation_allowed=False,
                risk_class="LOW",
                execution_handler="registry.execution.escalate_to_human"
            ),
            ActionDefinition(
                action_id="STOP",
                description="Conclude recovery mission.",
                required_permissions=["AGENT_EXECUTE"],
                financial_mutation_allowed=False,
                risk_class="LOW",
                execution_handler="registry.execution.stop"
            )
        ]
        for a in defaults:
            self._actions[a.action_id] = a

    def is_registered(self, action_id: str) -> bool:
        return action_id in self._actions

    def get_action(self, action_id: str) -> Optional[ActionDefinition]:
        return self._actions.get(action_id)

    def get_all_registered_action_ids(self) -> List[str]:
        return list(self._actions.keys())

    def validate_action(self, action_id: str, customer_segment: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Validates action registration and customer tier constraints."""
        if not self.is_registered(action_id):
            return False, f"Action '{action_id}' is not registered in authoritative ActionRegistry."
        
        act = self._actions[action_id]
        if customer_segment and customer_segment not in act.allowed_customer_tiers:
            return False, f"Action '{action_id}' is not authorized for customer segment '{customer_segment}'."

        return True, None

    def reject_unauthorized_proposals(self, proposed_actions: List[str], customer_segment: Optional[str] = None) -> Tuple[List[str], List[str]]:
        """
        Filters proposed actions, returning (valid_actions, rejected_actions).
        Guarantees fail-closed security against prompt injections and malicious mutations.
        """
        valid = []
        rejected = []
        for act in proposed_actions:
            is_valid, _ = self.validate_action(act, customer_segment)
            if is_valid:
                valid.append(act)
            else:
                rejected.append(act)
        return valid, rejected

action_registry = ActionRegistry()
