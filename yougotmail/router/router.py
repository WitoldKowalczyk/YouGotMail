from yougotmail.send.send import Send
from yougotmail.send.reply import Reply
from yougotmail.retrieve.retrieve_emails import RetrieveEmails
from yougotmail.retrieve.retrieve_conversations import RetrieveConversations
from yougotmail.retrieve.retrieve_attachments import RetrieveAttachments
from yougotmail.storage.storage import Storage
from yougotmail.quick.quick import Quick
from yougotmail._utils._validation import (
    validate_inputs,
    EMAIL_VALIDATION_RULES,
    ValidationError,
)
from yougotmail.ai.ai import AI


class YouGotMail:
    def __init__(
        self,
        client_id,
        client_secret,
        tenant_id,
        open_ai_api_key="",
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
        if client_id is None or client_secret is None or tenant_id is None:
            raise ValueError("client_id, client_secret and tenant_id are required")

        self.send = Send(
            client_id,
            client_secret,
            tenant_id,
            mongo_url,
            mongo_db_name,
            aws_access_key_id,
            aws_secret_access_key,
            region_name,
        )
        self.retrieve_emails = RetrieveEmails(
            client_id,
            client_secret,
            tenant_id,
            mongo_url,
            mongo_db_name,
            aws_access_key_id,
            aws_secret_access_key,
            region_name,
            bucket_name,
            email_collection,
            conversation_collection,
            attachment_collection,
        )
        self.retrieve_conversations = RetrieveConversations(
            client_id,
            client_secret,
            tenant_id,
            mongo_url,
            mongo_db_name,
            aws_access_key_id,
            aws_secret_access_key,
            region_name,
            bucket_name,
            email_collection,
            conversation_collection,
            attachment_collection,
        )
        self.retrieve_attachments = RetrieveAttachments(
            client_id,
            client_secret,
            tenant_id,
            mongo_url,
            mongo_db_name,
            aws_access_key_id,
            aws_secret_access_key,
            region_name,
            bucket_name,
            email_collection,
            conversation_collection,
            attachment_collection,
        )
        self.storage = Storage(
            mongo_url,
            mongo_db_name,
            aws_access_key_id,
            aws_secret_access_key,
            region_name,
            bucket_name,
            email_collection,
            conversation_collection,
            attachment_collection,
        )
        self.quick = Quick(
            client_id,
            client_secret,
            tenant_id,
            mongo_url,
            mongo_db_name,
            aws_access_key_id,
            aws_secret_access_key,
            region_name,
            bucket_name,
            email_collection,
            conversation_collection,
            attachment_collection,
        )
        self.reply = Reply(client_id, client_secret, tenant_id)
        self.ai = AI(client_id, client_secret, tenant_id, open_ai_api_key)

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
        folder_path=[],
        drafts=False,
        archived=False,
        deleted=False,
        sent=False,
        read="all",
        attachments=True,
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
        storage=False,
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

    # Functions handling email replies
    def reply_to_email(
        self, inbox="", email_id="", email_body="", cc_recipients=[], bcc_recipients=[]
    ):
        return self.reply.reply_to_email(
            inbox, email_id, email_body, cc_recipients, bcc_recipients
        )

    def ai_structured_output_from_email_body(self, email_body, schema):
        return self.ai.ai_structured_output_from_email_body(
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
        # Add custom validation logic specific to this function
        if range and (start_date or end_date or start_time or end_time):
            raise ValidationError(
                "Cannot specify both 'range' and custom date/time parameters"
            )

        return self.ai.ai_get_emails_with_structured_output(
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
