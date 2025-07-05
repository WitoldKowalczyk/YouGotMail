from yougotmail.send.send import Send
from yougotmail.retrieve.retrieve_emails import RetrieveEmails


class Quick:
    def __init__(
        self,
        client_id,
        client_secret,
        tenant_id,
        mongo_url="",
        mongo_db_name="",
        aws_access_key_id="",
        aws_secret_access_key="",
        region_name="",
        bucket_name="",
        email_collection="",
        conversation_collection="",
        attachment_collection="",
    ):
        self.send = Send(client_id, client_secret, tenant_id)
        self.retrieve = RetrieveEmails(
            client_id,
            client_secret,
            tenant_id,
            mongo_url=mongo_url,
            mongo_db_name=mongo_db_name,
            email_collection=email_collection,
            conversation_collection=conversation_collection,
            attachment_collection=attachment_collection,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            bucket_name=bucket_name,
        )

    # Quick action functions for simplified usage
    def get_last_hour_emails(self, inbox):
        """Returns all emails from the last hour"""
        try:
            emails = self.retrieve.get_emails(inbox=inbox, range="last_hour")
            print(f"Found {len(emails)} emails in the last hour")
            return emails
        except Exception as e:
            print(f"Error in last_hour_emails: {e}")
            return None

    def get_unread_emails(self, inbox):
        """Returns all unread emails from the last 24 hours"""
        try:
            emails = self.retrieve.get_emails(
                inbox=inbox, range="last_24_hours", read=False
            )
            return emails
        except Exception as e:
            print(f"Error in unread_emails: {e}")
            return None
