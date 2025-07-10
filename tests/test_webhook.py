from yougotmail import YouGotMail
import os
from dotenv import load_dotenv

load_dotenv()

ygm = YouGotMail(
    client_id=os.environ.get("MS_CLIENT_ID"),
    client_secret=os.environ.get("MS_CLIENT_SECRET"),
    tenant_id=os.environ.get("MS_TENANT_ID"),
)


# def test_create_microsoft_graph_webhook():
#     try:
#         create_webhook = ygm.create_microsoft_graph_webhook(
#             inbox=os.environ.get("INBOX_1"),
#             api_url=os.environ.get("WEBHOOK_URL"),
#             client_state=os.environ.get("CLIENT_STATE"),
#         )
#         print(create_webhook)
#     except Exception as e:
#         print(f"Error: {e}")


def test_get_active_subscriptions_for_inbox():
    try:
        active_subscriptions = ygm.get_active_subscriptions_for_inbox(
            inbox=os.environ.get("INBOX_1")
        )
        print(active_subscriptions)
    except Exception as e:
        print(f"Error: {e}")


def test_renew_subscriptions():
    try:
        renew_subscriptions = ygm.renew_subscriptions(inbox=os.environ.get("INBOX_1"))
        print(renew_subscriptions)
    except Exception as e:
        print(f"Error: {e}")
