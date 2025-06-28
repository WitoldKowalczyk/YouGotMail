from yougotmail import YouGotMail
import os
from dotenv import load_dotenv
import json

load_dotenv()

ygm = YouGotMail(
            client_id=os.environ.get("MS_CLIENT_ID"),
            client_secret=os.environ.get("MS_CLIENT_SECRET"),
            tenant_id=os.environ.get("MS_TENANT_ID"),
            open_ai_api_key=os.environ.get("OPENAI_API_KEY")
            )

def test_ai_parsing():
    try:
        emails = ygm.ai_get_emails_with_structured_output(
            inbox=[os.environ.get("INBOX_1"), os.environ.get("INBOX_2")],
            range="last_8_hours",
            attachments=False,
            schema={
                "topic": {
                    "type": "string",
                    "description": "The topic of the email"
                },
                "sentiment": {
                    "type": "string",
                    "description": "what was the mood of the email and the sender writing it"
                }
            }
            )
        with open("emails_structured_output.json", "w") as f:
            json.dump(emails, f, indent=4)
    except Exception as e:
        print(f"Error: {e}")
