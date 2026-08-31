from typing import List, Dict, Any

class FunctionSchemaGenerator:
    def get_tool_schemas(self, feasible_actions: List[str]) -> List[Dict[str, Any]]:
        schemas = []
        
        # We only return schemas for actions that are feasible in the current context
        if "WAIT" in feasible_actions:
            schemas.append({
                "type": "function",
                "function": {
                    "name": "WAIT",
                    "description": "Do nothing and wait for time to pass or external events.",
                    "parameters": {"type": "object", "properties": {}}
                }
            })
            
        if "RECONCILE" in feasible_actions:
            schemas.append({
                "type": "function",
                "function": {
                    "name": "RECONCILE",
                    "description": "Reconcile an unknown payment status with the gateway.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "payment_id": {"type": "string", "description": "The ID of the payment to reconcile"}
                        },
                        "required": ["payment_id"]
                    }
                }
            })
            
        if "RETRY" in feasible_actions:
            schemas.append({
                "type": "function",
                "function": {
                    "name": "RETRY",
                    "description": "Schedule a retry for a failed payment.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "payment_id": {"type": "string", "description": "The ID of the payment to retry"},
                            "delay": {"type": "integer", "description": "Delay in seconds before retrying"}
                        },
                        "required": ["payment_id", "delay"]
                    }
                }
            })
            
        if "SEND_PAYMENT_LINK" in feasible_actions:
            schemas.append({
                "type": "function",
                "function": {
                    "name": "SEND_PAYMENT_LINK",
                    "description": "Generate and send a payment link for overdue items.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of invoice or checkout IDs"
                            }
                        },
                        "required": ["items"]
                    }
                }
            })

        if "SEND_MESSAGE" in feasible_actions:
            schemas.append({
                "type": "function",
                "function": {
                    "name": "SEND_MESSAGE",
                    "description": "Send a communication to the customer.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "channel": {"type": "string", "enum": ["EMAIL", "SMS", "WHATSAPP"]},
                            "message_type": {"type": "string", "enum": ["GENTLE_REMINDER", "URGENT_NOTICE", "APOLOGY"]}
                        },
                        "required": ["channel", "message_type"]
                    }
                }
            })

        if "REGISTER_PTP" in feasible_actions:
            schemas.append({
                "type": "function",
                "function": {
                    "name": "REGISTER_PTP",
                    "description": "Register a Promise To Pay from the customer.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "promise_date": {"type": "integer", "description": "Timestamp when customer promises to pay"}
                        },
                        "required": ["promise_date"]
                    }
                }
            })

        if "APPLY_DISCOUNT" in feasible_actions:
            schemas.append({
                "type": "function",
                "function": {
                    "name": "APPLY_DISCOUNT",
                    "description": "Apply a discount to recover partial value.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "invoice_id": {"type": "string"},
                            "amount": {"type": "number"}
                        },
                        "required": ["invoice_id", "amount"]
                    }
                }
            })

        if "REFUND_PAYMENT" in feasible_actions:
            schemas.append({
                "type": "function",
                "function": {
                    "name": "REFUND_PAYMENT",
                    "description": "Refund a payment.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "payment_id": {"type": "string"}
                        },
                        "required": ["payment_id"]
                    }
                }
            })

        if "ESCALATE" in feasible_actions:
            schemas.append({
                "type": "function",
                "function": {
                    "name": "ESCALATE",
                    "description": "Escalate the mission to a human agent.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {"type": "string", "description": "Reason for escalation"}
                        },
                        "required": ["reason"]
                    }
                }
            })
            
        if "STOP" in feasible_actions:
            schemas.append({
                "type": "function",
                "function": {
                    "name": "STOP",
                    "description": "Terminate the recovery mission.",
                    "parameters": {"type": "object", "properties": {}}
                }
            })

        return schemas

schema_generator = FunctionSchemaGenerator()
