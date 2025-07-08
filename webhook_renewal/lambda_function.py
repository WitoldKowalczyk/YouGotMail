import os
from yougotmail import YouGotMail

INBOX = os.environ.get("INBOX")
MS_CLIENT_ID = os.environ.get("MS_CLIENT_ID")
MS_CLIENT_SECRET = os.environ.get("MS_CLIENT_SECRET")
MS_TENANT_ID = os.environ.get("MS_TENANT_ID")

def lambda_handler(event, context):

    ygm = YouGotMail(
        client_id=MS_CLIENT_ID,
        client_secret=MS_CLIENT_SECRET,
        tenant_id=MS_TENANT_ID
    )

    renew_subscriptions = ygm.renew_subscriptions(
        inbox=INBOX)
    
    print(renew_subscriptions)

    return {}
