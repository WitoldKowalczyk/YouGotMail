from yougotmail import YouGotMail
import os
from dotenv import load_dotenv
import json

load_dotenv()

ygm = YouGotMail(
            client_id=os.environ.get("MS_CLIENT_ID"),
            client_secret=os.environ.get("MS_CLIENT_SECRET"),
            tenant_id=os.environ.get("MS_TENANT_ID")
            )

def test_get_emails():
    try:
        emails = ygm.get_emails(
            inbox=[os.environ.get("INBOX_1")],
            range="last_30_minutes",
            attachments=False
            )
        with open("emails.json", "w") as f:
            json.dump(emails, f, indent=4)
    except Exception as e:
        print(f"Error: {e}")
