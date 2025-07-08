from yougotmail import YouGotMail
import os
from dotenv import load_dotenv
import json

load_dotenv()

ygm = YouGotMail(
    client_id=os.environ.get("MS_CLIENT_ID"),
    client_secret=os.environ.get("MS_CLIENT_SECRET"),
    tenant_id=os.environ.get("MS_TENANT_ID"),
    mongo_url=os.environ.get("MONGO_URL"),
    mongo_db_name=os.environ.get("MONGO_DB_NAME"),
    email_collection=os.environ.get("EMAIL_COLLECTION"),
    conversation_collection=os.environ.get("CONVERSATION_COLLECTION"),
    attachment_collection=os.environ.get("ATTACHMENT_COLLECTION"),
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("REGION_NAME"),
    bucket_name=os.environ.get("BUCKET_NAME")
)

def test_retrieving_emails_with_storage():
    try:
        emails = ygm.get_emails(
            inbox=[os.environ.get("INBOX_1")],
            range="last_8_hours",
            storage="emails_and_attachments"
        )
        print(json.dumps(emails, indent=4))
    except Exception as e:
        print(f"Error: {e}")