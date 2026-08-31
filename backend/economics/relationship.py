from pydantic import BaseModel
from typing import Dict, Any

class RelationshipState(BaseModel):
    customer_id: str
    customer_segment: str = "SMB" # B2B_ENTERPRISE, B2B_MIDMARKET, SMB, CONSUMER
    recent_contacts: int = 0
    recent_responses: int = 0
    successful_prior_recoveries: int = 0
    customer_value: float = 10000.0 # LTV
    complaints: int = 0
    opt_out: bool = False
    silence_duration: int = 86400 * 7 # seconds since last contact

    def calculate_relationship_cost(self, channel_or_action: str) -> float:
        """
        Deterministic formula:
        RelationshipCost = ChannelCost * ContactFrequencyPenalty * CustomerSensitivity * RecentContactFactor
        """
        if self.opt_out:
            return float('inf')

        # 1. Channel Cost (₹)
        CHANNEL_COSTS = {
            "WAIT": 0.0,
            "RECONCILE": 0.0,
            "RETRY": 0.0,
            "RETRY_GATEWAY_A": 0.0,
            "RETRY_GATEWAY_B": 0.0,
            "RETRY_GATEWAY_C": 0.0,
            "SWITCH_PERMITTED_RAIL": 0.0,
            "EMAIL": 2.0,
            "SEND_MESSAGE": 4.0,
            "SMS": 5.0,
            "SEND_PAYMENT_LINK": 4.0,
            "REQUEST_CUSTOMER_ACTION": 8.0,
            "REGISTER_PTP": 5.0,
            "APPLY_DISCOUNT": 0.0,
            "ESCALATE": 50.0,
            "STOP": 0.0
        }
        channel_cost = CHANNEL_COSTS.get(channel_or_action, 5.0)
        if channel_cost == 0.0:
            return 0.0

        # 2. Contact Frequency Penalty
        freq_penalty = 1.0 + ((self.recent_contacts ** 1.5) * 0.5)

        # 3. Customer Sensitivity
        SENSITIVITY_MAP = {
            "B2B_ENTERPRISE": 2.2,
            "B2B_MIDMARKET": 1.6,
            "SMB": 1.0,
            "CONSUMER": 0.8
        }
        sensitivity = SENSITIVITY_MAP.get(self.customer_segment, 1.0)
        if self.complaints > 0:
            sensitivity *= (1.0 + self.complaints * 0.5)

        # 4. Recent Contact Factor
        if self.silence_duration < 3600:
            recent_factor = 2.5 # Contacted within the last hour
        elif self.silence_duration < 86400:
            recent_factor = 1.5 # Contacted within 24 hours
        else:
            recent_factor = 1.0 # Adequate rest period

        cost = channel_cost * freq_penalty * sensitivity * recent_factor

        # Trust credit from successful past recoveries
        trust_discount = min(cost * 0.4, self.successful_prior_recoveries * 5.0)
        final_cost = max(0.0, cost - trust_discount)

        return round(final_cost, 2)

    def relationship_cost_proxy(self) -> float:
        if self.opt_out:
            return float('inf')
        if getattr(self, "complaints", 0) > 0:
            val_cost = (getattr(self, "customer_value", 0.0) * 0.001) if getattr(self, "customer_value", 0.0) else 0.0
            base = (self.recent_contacts * 5.0) + (self.complaints * 100.0) + (val_cost * max(1, self.recent_contacts))
            if base > 0:
                return float(base)
        return self.calculate_relationship_cost("SEND_MESSAGE")

class RelationshipModel:
    def __init__(self):
        self._states: Dict[str, RelationshipState] = {}

    def get_relationship(self, customer_id: str) -> RelationshipState:
        from simulator.world import world
        if customer_id not in self._states:
            cust = world.customers.get(customer_id)
            if cust:
                self._states[customer_id] = RelationshipState(
                    customer_id=customer_id,
                    customer_segment=cust.segment,
                    recent_contacts=cust.recent_contacts,
                    recent_responses=cust.recent_responses,
                    successful_prior_recoveries=cust.successful_prior_recoveries,
                    customer_value=cust.ltv,
                    complaints=cust.complaints,
                    opt_out=cust.opt_out,
                    silence_duration=cust.silence_duration or 86400 * 5
                )
            else:
                self._states[customer_id] = RelationshipState(customer_id=customer_id)
        return self._states[customer_id]

relationship_model = RelationshipModel()
