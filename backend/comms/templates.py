from typing import Dict, Any

class CommunicationTemplates:
    @staticmethod
    def render_payment_link(customer_name: str, amount_str: str, payment_url: str) -> str:
        return f"Hi {customer_name}, your payment of {amount_str} is pending. Please complete your transaction securely here: {payment_url}"

    @staticmethod
    def render_reminder(customer_name: str, invoice_ref: str) -> str:
        return f"Dear {customer_name}, this is a gentle reminder regarding payment reference {invoice_ref}."
