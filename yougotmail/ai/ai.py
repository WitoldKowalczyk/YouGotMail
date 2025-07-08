from yougotmail.retrieve.retrieve_emails import RetrieveEmails
from yougotmail.ai._ai_prompts import AGENT_INSTRUCTIONS
from yougotmail.ai._ai_tools import AI_TOOLS, TOOLS
from typing import Any, Dict


class AI:
    def __init__(self, client_id, client_secret, tenant_id, open_ai_api_key=None):
        self.retrieve_emails = RetrieveEmails(client_id, client_secret, tenant_id)
        self.open_ai_api_key = open_ai_api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

    def _ensure_ai_handler(self):
        """Lazy import of AI Handler to avoid immediate OpenAI dependency"""
        if not self.open_ai_api_key:
            raise ValueError(
                "OpenAI API key is required for AI functionality. Please provide it when initializing the YouGotMail class."
            )

        try:
            from yougotmail.ai._ai_handler import AIHandler

            return AIHandler(
                open_ai_api_key=self.open_ai_api_key
            )
        except ImportError:
            raise ImportError(
                "OpenAI package is not installed. Install it with 'pip install yougotmail[openai]'"
            )

    def ai_structured_output_from_email_body(
        self, *, email_body: str, schema: Dict[str, Any]
    ):
        ai_handler = self._ensure_ai_handler()
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

        return ai_handler.structured_outputs(
            prompt=f"Extract the following information from the email: {schema}",
            schema=schema,
            content=content_for_ai,
            model="gpt-4.1",
        )

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

    def ai_agent_with_tools(self, inbox, prompt):
        try:
            ai_handler = self._ensure_ai_handler()
            return ai_handler.function_calling(
                instructions=AGENT_INSTRUCTIONS,
                prompt=prompt,
                model="gpt-4.1",
                tools=TOOLS,
                ai_tools=AI_TOOLS(self.client_id, self.client_secret, self.tenant_id, inbox),
            )
        except Exception as e:
            print(f"Error in ai_agent_with_tools: {e}")
            return None
