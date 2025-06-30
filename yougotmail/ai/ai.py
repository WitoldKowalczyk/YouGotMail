from yougotmail.ai._ai_handler import AIHandler
from typing import Any, Dict
from yougotmail.retrieve.retrieve_emails import RetrieveEmails


class AI:
    def __init__(self, client_id, client_secret, tenant_id, open_ai_api_key):
        self.retrieve_emails = RetrieveEmails(client_id, client_secret, tenant_id)
        if all([open_ai_api_key]):
            self.open_ai_api_key = open_ai_api_key
        else:
            self.open_ai_api_key = None

    def ai_structured_output_from_email_body(
        self, *, email_body: str, schema: Dict[str, Any]
    ):
        schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "email_schema",
                "description": "A schema for answering questions about the email and its contents",
                "schema": {
                    "type": "object",
                    "properties": {
                        **schema,
                    },
                    "required": list(schema.keys()),
                    "additionalProperties": False,
                },
            },
        }

        content_for_ai = f"""
            Here is the email content: {email_body}
            """

        ai = AIHandler(
            open_ai_api_key=self.open_ai_api_key,
            prompt_name="EMAIL_EXTRACTION_PROMPT",
            schema=schema,
            content=content_for_ai,
        )

        classification = ai.main()

        return classification

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
        schema={},
    ):
        inboxes = self.retrieve_emails.get_emails(
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
        inbox_list = []
        for inbox in inboxes:
            emails = inbox.get("emails")
            emails_list = []
            for email in emails:
                email_body = email.get("body")
                email["structured_output"] = self.ai_structured_output_from_email_body(
                    email_body=email_body, schema=schema
                )
                emails_list.append(email)
            inbox["emails"] = emails_list
            inbox_list.append(inbox)
        return inbox_list
