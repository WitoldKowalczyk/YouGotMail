from yougotmail import YouGotMail
import os
from dotenv import load_dotenv

load_dotenv()

ygm = YouGotMail(
    client_id=os.environ.get("MS_CLIENT_ID"),
    client_secret=os.environ.get("MS_CLIENT_SECRET"),
    tenant_id=os.environ.get("MS_TENANT_ID"),
)

def test_draft_email():
    try:
        draft_email = ygm.draft_email(
            inbox=os.environ.get("INBOX_1"),
            subject="test",
            importance="",
            email_body="<html><body><h1>Test Email</h1><p>This is a test email sent from YouGotMail.</p></body></html>",
            to_recipients=[os.environ.get("INBOX_1")],
            cc_recipients=[],
            bcc_recipients=[],
            attachments=[],
        )
        print(draft_email)
    except Exception as e:
        print(f"Error: {e}")

def test_sending_emails():
    try:
        send_email = ygm.send_email(
            inbox=os.environ.get("INBOX_1"),
            subject="test",
            importance="",
            email_body="<html><body><h1>Test Email</h1><p>This is a test email sent from YouGotMail.</p></body></html>",
            to_recipients=[os.environ.get("INBOX_1")],
            cc_recipients=[],
            bcc_recipients=[],
            attachments=[ # You can pass a URL (make sure it's accessible) or a local file path
                "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
            ]
        )
        print(send_email)
    except Exception as e:
        print(f"Error: {e}")

def test_replying_to_email():
    try:
        reply_to_email = ygm.reply_to_email(
            inbox=os.environ.get("INBOX_1"),
            email_id=os.environ.get("EMAIL_ID"),
            email_body="This is a test reply to the email - AI signature",
            cc_recipients=["ai@delosone.com"]
        )
        print(reply_to_email)
    except Exception as e:
        print(f"Error: {e}")
