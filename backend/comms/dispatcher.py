from typing import Dict, Any, Optional
from backend.comms.policy import communication_policy
from backend.comms.channels import EmailChannel, SMSChannel, WhatsAppChannel
from backend.comms.templates import CommunicationTemplates

class CommunicationDispatcher:
    """
    Central dispatcher for sending customer recovery messages and payment links.
    """
    @staticmethod
    def send_payment_link_message(
        customer_id: str,
        customer_name: str,
        channel: str,
        recipient: str,
        amount_str: str,
        payment_url: str,
        current_24h_count: int = 0
    ) -> Dict[str, Any]:
        # Policy Check
        if not communication_policy.can_contact_customer(customer_id, current_24h_count):
            return {"status": "BLOCKED_BY_POLICY", "reason": "Customer contact limit or opt-out active"}

        msg_body = CommunicationTemplates.render_payment_link(customer_name, amount_str, payment_url)

        ch = channel.upper()
        if ch == "EMAIL":
            res = EmailChannel.send(recipient, "Your Payment Link", msg_body)
        elif ch == "WHATSAPP":
            res = WhatsAppChannel.send(recipient, msg_body)
        elif ch == "SMS":
            res = SMSChannel.send(recipient, msg_body)
        else:
            return {"status": "UNSUPPORTED_CHANNEL", "channel": channel}

        res["message"] = msg_body
        return res

comms_dispatcher = CommunicationDispatcher()
