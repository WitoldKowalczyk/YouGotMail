from yougotmail.quick.quick import Quick
from yougotmail.retrieve.retrieve_emails import RetrieveEmails
from yougotmail.retrieve.retrieve_conversations import RetrieveConversations
from yougotmail.retrieve.retrieve_attachments import RetrieveAttachments
from yougotmail.send.send import Send
from yougotmail.send.reply import Reply
from yougotmail._utils._ms_webhook import MSWebhook
from yougotmail._utils._validation import (
    validate_inputs,
    EMAIL_VALIDATION_RULES,
    ValidationError,
)

class YouGotMail:
    def __init__(
        self,
        client_id,
        client_secret,
        tenant_id,
        open_ai_api_key="",
        mongo_url="",
        mongo_db_name="",
        email_collection="",
        conversation_collection="",
        attachment_collection="",
        aws_access_key_id="",
        aws_secret_access_key="",
        region_name="",
        bucket_name="",
    ):
        if client_id is None or client_secret is None or tenant_id is None:
            raise ValueError("client_id, client_secret and tenant_id are required")

        self.send = Send(client_id, client_secret, tenant_id)
        self.retrieve_emails = RetrieveEmails(
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
        self.retrieve_conversations = RetrieveConversations(
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
        self.retrieve_attachments = RetrieveAttachments(
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
        self.quick = Quick(
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
        self.reply = Reply(client_id, client_secret, tenant_id)
        # Store credentials for lazy AI initialization
        self._ai_credentials = {
            "client_id": client_id,
            "client_secret": client_secret,
            "tenant_id": tenant_id,
            "open_ai_api_key": open_ai_api_key,
        }
        self._ai_instance = None
        self.ms_webhook = MSWebhook(client_id, client_secret, tenant_id)

    def _get_ai(self):
        """Lazy initialization of AI component"""
        if self._ai_instance is None:
            try:
                from yougotmail.ai.ai import AI

                self._ai_instance = AI(**self._ai_credentials)
            except ImportError:
                raise ImportError(
                    "OpenAI dependencies are not installed. Install them with 'pip install yougotmail[openai]'"
                )
        return self._ai_instance

    # Functions handling email retrieval and conversation retrieval
    @validate_inputs(**EMAIL_VALIDATION_RULES)
    def get_emails(
        self,
        *,
        inbox=[],
        range="",
        start_date="",  # can be date: YYYY-MM-DD or datetime YYYY-MM-DDT00:00:00Z
        start_time="",
        end_date="",  # can be date: YYYY-MM-DD or datetime YYYY-MM-DDT00:00:00Z
        end_time="",
        subject=[],
        sender_name=[],
        sender_address=[],
        recipients=[],
        cc=[],
        bcc=[],
        folder_path="",
        drafts=False,
        archived=False,
        deleted=False,
        sent=False,
        read="all",
        attachments=False,
        storage=None
    ):
        # Add custom validation logic specific to this function
        if range and (start_date or end_date or start_time or end_time):
            raise ValidationError(
                "Cannot specify both 'range' and custom date/time parameters"
            )

        return self.retrieve_emails.get_emails(
            inbox=inbox,
            range=range,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            subject=subject,
            sender_name=sender_name,
            sender_address=sender_address,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            folder_path=folder_path,
            drafts=drafts,
            archived=archived,
            deleted=deleted,
            sent=sent,
            read=read,
            attachments=attachments,
            storage=storage,
        )

    def get_conversation(
        self,
        inbox="",
        conversation_id="",
        range="last_365_days",
        start_date="",
        start_time="",
        end_date="",
        end_time="",
        subject="",
        sender_name="",
        sender_address="",
        read="all",
        attachments=False,
        storage=None
    ):
        return self.retrieve_conversations.get_conversation(
            inbox=inbox,
            conversation_id=conversation_id,
            range=range,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            subject=subject,
            sender_name=sender_name,
            sender_address=sender_address,
            read=read,
            attachments=attachments,
            storage=storage,
        )

    def get_attachments(
        self,
        inbox=[],
        range="",
        start_date="",  # can be date: YYYY-MM-DD or datetime YYYY-MM-DDT00:00:00Z
        start_time="",
        end_date="",  # can be date: YYYY-MM-DD or datetime YYYY-MM-DDT00:00:00Z
        end_time="",
        subject=[],
        sender_name=[],
        sender_address=[],
        recipients=[],
        cc=[],
        bcc=[],
        folder_path=[],
        drafts=False,
        archived=False,
        deleted=False,
        sent=False,
        read="all",
        storage=None,
    ):
        return self.retrieve_attachments.get_attachments(
            inbox=inbox,
            range=range,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            subject=subject,
            sender_name=sender_name,
            sender_address=sender_address,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            folder_path=folder_path,
            drafts=drafts,
            archived=archived,
            deleted=deleted,
            sent=sent,
            read=read,
            storage=storage,
        )

    # Functions handling email sending
    def draft_email(
        self,
        inbox="",
        subject="",
        importance="",
        email_body="",
        to_recipients=[],
        cc_recipients=[],
        bcc_recipients=[],
        attachments=[],
    ):

        return self.send.draft_email(
            inbox=inbox,
            subject=subject,
            importance=importance,
            email_body=email_body,
            to_recipients=to_recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            attachments=attachments,
        )

    def send_email_draft(self, inbox, id):
        return self.send.send_email_draft(inbox, id)

    def send_email(
        self,
        inbox="",
        subject="",
        importance="",
        email_body="",
        to_recipients=[],
        cc_recipients=[],
        bcc_recipients=[],
        attachments=[],
    ):
        return self.send.send_email(
            inbox,
            subject,
            importance,
            email_body,
            to_recipients,
            cc_recipients,
            bcc_recipients,
            attachments,
        )

    # Quick action functions for simplified usage
    def get_last_hour_emails(self, inbox):
        return self.quick.get_last_hour_emails(inbox)

    def get_unread_emails(self, inbox):
        return self.quick.get_unread_emails(inbox)

    def draft_reply_to_email(self, inbox="", email="", email_id=""):
        return self.reply.draft_reply_to_email(inbox, email, email_id)

    # Functions handling email replies
    def reply_to_email(
        self, inbox="", email_id="", email_body="", cc_recipients=[], bcc_recipients=[]
    ):
        return self.reply.reply_to_email(
            inbox, email_id, email_body, cc_recipients, bcc_recipients
        )

    def ai_structured_output_from_email_body(self, email_body, schema):
        ai = self._get_ai()
        return ai.ai_structured_output_from_email_body(
            email_body=email_body, schema=schema
        )

    @validate_inputs(**EMAIL_VALIDATION_RULES)
    def ai_get_emails_with_structured_output(
        self,
        *,
        inbox=[],
        range="",
        start_date="",  # can be date: YYYY-MM-DD or datetime YYYY-MM-DDT00:00:00Z
        start_time="",
        end_date="",  # can be date: YYYY-MM-DD or datetime YYYY-MM-DDT00:00:00Z
        end_time="",
        subject=[],
        sender_name=[],
        sender_address=[],
        recipients=[],
        cc=[],
        bcc=[],
        folder_path=[],
        drafts=False,
        archived=False,
        deleted=False,
        sent=False,
        read="all",
        attachments=True,
        storage=None,
        schema={}
    ):
        ai = self._get_ai()
        # Add custom validation logic specific to this function
        if range and (start_date or end_date or start_time or end_time):
            raise ValidationError(
                "Cannot specify both 'range' and custom date/time parameters"
            )

        return ai.ai_get_emails_with_structured_output(
            inbox=inbox,
            range=range,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            subject=subject,
            sender_name=sender_name,
            sender_address=sender_address,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            folder_path=folder_path,
            drafts=drafts,
            archived=archived,
            deleted=deleted,
            sent=sent,
            read=read,
            attachments=attachments,
            storage=storage,
            schema=schema,
        )

    def ai_agent_with_tools(self, inbox,prompt):
        ai = self._get_ai()
        return ai.ai_agent_with_tools(inbox=inbox, prompt=prompt)

    def create_microsoft_graph_webhook(self, inbox, api_url, client_state):
        return self.ms_webhook.create_microsoft_graph_webhook(
            inbox, api_url, client_state
        )

    def get_active_subscriptions_for_inbox(self, inbox):
        return self.ms_webhook.get_active_subscriptions_for_inbox(inbox)

    def delete_subscription(self, subscription_id):
        return self.ms_webhook.delete_subscription(subscription_id)

    def renew_subscriptions(self, inbox):
        return self.ms_webhook.renew_subscriptions(inbox)
