from yougotmail.send.send import Send

TOOLS = [
    {
        "type": "function",
        "name": "send_email",
        "description": "Send an email to a given recipient based on instructions received from the user.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Subject of the email",
                },
                "email_body": {
                    "type": "string",
                    "description": "Body of the email",
                },
                "to_recipients": {
                    "type": "array",
                    "description": "Email address of the recipient",
                    "items": {
                        "type": "string",
                    }
                }
            },
            "required": ["subject", "email_body", "to_recipients"],
            "additionalProperties": False,
        },
    }
]


class AI_TOOLS:
    def __init__(self, client_id, client_secret, tenant_id, inbox):
        self.send = Send(client_id, client_secret, tenant_id)
        self.inbox = inbox

    def _ai_function_router(self, name, args):
        if name == "send_email":
            return self.send_email(args["subject"], args["email_body"], args["to_recipients"])
        else:
            return "Function not found"

    def send_email(self, subject, email_body, to_recipients):
        response = self.send.send_email(
            inbox=self.inbox,
            subject=subject,
            email_body=email_body,
            to_recipients=to_recipients
        )
        print(f"Email sent: {response}")
        return response