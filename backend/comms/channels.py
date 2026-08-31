from typing import Dict, Any

class EmailChannel:
    @staticmethod
    def send(to_email: str, subject: str, body: str) -> Dict[str, Any]:
        return {"status": "DELIVERED", "channel": "EMAIL", "recipient": to_email}

class SMSChannel:
    @staticmethod
    def send(to_phone: str, message: str) -> Dict[str, Any]:
        return {"status": "DELIVERED", "channel": "SMS", "recipient": to_phone}

class WhatsAppChannel:
    @staticmethod
    def send(to_phone: str, message: str) -> Dict[str, Any]:
        return {"status": "DELIVERED", "channel": "WHATSAPP", "recipient": to_phone}
