from yougotmail import YouGotMail
import os
from dotenv import load_dotenv
import json

load_dotenv()

ygm = YouGotMail(
    client_id=os.environ.get("MS_CLIENT_ID"),
    client_secret=os.environ.get("MS_CLIENT_SECRET"),
    tenant_id=os.environ.get("MS_TENANT_ID"),
)


def test_get_emails():
    try:
        emails = ygm.get_emails(
            inbox=[os.environ.get("INBOX_1")],
            # range="last_7_days",
            start_date="2024-06-01",  # can be date: YYYY-MM-DD 
            start_time="00:00:00", # time in 00:00:00, all time is UTC
            end_date="2025-06-03",  # can be date: YYYY-MM-DD 
            end_time="14:00:00", # time in 00:00:00, all time is UTC
            # subject=["Bristol", "7009"],
            # sender_name=[],
            # sender_address=[],
            # recipients=[],
            # cc=[],
            # bcc=[],
            folder_path="0. General/Admin/Banking",
            # drafts=False,
            # archived=False,
            # deleted=False,
            # sent=False,
            # read="all",
            # attachments=True,
            # storage=None,
        )
        with open("emails.json", "w") as f:
            json.dump(emails, f, indent=4)
    except Exception as e:
        print(f"Error: {e}")

def test_get_conversation():
    try:
        conversation = ygm.get_conversation(
            inbox=os.environ.get("INBOX_1"),
            conversation_id=os.environ.get("CONVERSATION_ID"),
            # range="last_7_days",
            # start_date="",
            # start_time="",
            # end_date="",
            # end_time="",
            # subject="",
            # sender_name="",
            # sender_address="",
            # read="all",
            # attachments=False,
        )
        with open("conversation.json", "w") as f:
            json.dump(conversation, f, indent=4)
    except Exception as e:
        print(f"Error: {e}")
