import requests
import base64
from yougotmail._utils._utils import Utils
from yougotmail.send.send import Send
import os
from urllib.parse import urlparse, unquote, quote
import json


class Reply:
    def __init__(self, client_id, client_secret, tenant_id):
        self.utils = Utils()
        self.send = Send(client_id, client_secret, tenant_id)
        self.token = self.utils._generate_MS_graph_token(
            client_id, client_secret, tenant_id
        )

    # def _draft_reply(self, inbox, email_id, reply_body):
    #     try:
    #         # URL encode the message ID for the API call
    #         encoded_email_id = quote(email_id, safe="")
    #         url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{encoded_email_id}/createReply"
    #         print(f"📝 Creating reply at URL: {url}")
    #         headers = {
    #             "Authorization": f"Bearer {self.token}"
    #         }

    #         email = self._get_email_by_id(inbox, email_id)
    #         sender = self._find_email_sender(inbox, email_id)

    #         # Extract email content safely
    #         email_subject = email.get("subject", "No Subject")
    #         email_body_content = ""
    #         if email.get("body") and email.get("body").get("content"):
    #             email_body_content = email.get("body").get("content")

    #         email_split = f"""<div style="border-top: 1px solid #ccc; margin: 20px 0; padding: 10px 0;">
    #         <strong>From:</strong> &lt;{sender}&gt;<br>
    #         <strong>Date:</strong> {email.get("receivedDateTime")}<br>
    #         <strong>To:</strong> {self.INBOX}<br>
    #         <strong>Subject:</strong> {email_subject}<br>
    #         <div style="margin-top: 10px;">
    #         {email_body_content}
    #         </div>
    #         </div>"""

    #         # Generate AI reply
    #         is_reply_needed, ai_reply_content = self.ai_reply_draft(
    #             email_subject, email_body_content
    #         )
    #         if is_reply_needed == False:
    #             print("❌ No reply needed to the email")
    #             return None
    #         else:
    #             data = {
    #                 "message": {
    #                     "subject": "Re: " + email_subject,
    #                     "toRecipients": [{"emailAddress": {"address": sender}}],
    #                     "body": {
    #                         "contentType": "HTML",
    #                         "content": ai_reply_content
    #                         + email_split,
    #                     },
    #                 }
    #             }

    #             response = requests.post(url, headers=headers, json=data)
    #             if response.status_code == 201:  # createReply returns 201 on success
    #                 print("✅ Reply draft created successfully")
    #                 return response.json()
    #             else:
    #                 print(
    #                     f"❌ Error creating reply draft: Status {response.status_code}, Response: {response.text}"
    #                 )
    #                 return None

    #     except Exception as e:
    #         print(f"❌ Exception in _draft_reply: {e}")
    #         return None

    def reply_to_email(
        self, inbox="", email_id="", reply_body="", cc_recipients=[], bcc_recipients=[]
    ):
        if inbox == "":
            raise Exception("Inbox is required")

        email_id = email_id.split("_")[-1]

        reply_recipients = []
        reply_cc_recipients = []
        reply_bcc_recipients = []

        sender = self._find_email_sender(inbox, email_id)
        reply_recipients.append(sender)

        existing_recipients = self._find_email_recipients(inbox, email_id)
        existing_cc_recipients = self._find_email_cc_recipients(inbox, email_id)

        if existing_recipients is not None and len(existing_recipients) > 0:
            reply_recipients.extend(existing_recipients)

        if existing_cc_recipients is not None and len(existing_cc_recipients) > 0:
            reply_cc_recipients.extend(existing_cc_recipients)

        if cc_recipients is not None:
            reply_cc_recipients.extend(cc_recipients)

        if bcc_recipients is not None:
            reply_bcc_recipients.extend(bcc_recipients)

        reply_recipients_formatted = []
        reply_cc_recipients_formatted = []
        reply_bcc_recipients_formatted = []

        for reply_recipient in reply_recipients:
            reply_recipients_formatted.append(
                {"emailAddress": {"address": reply_recipient}}
            )
        for reply_cc_recipient in reply_cc_recipients:
            reply_cc_recipients_formatted.append(
                {"emailAddress": {"address": reply_cc_recipient}}
            )
        for reply_bcc_recipient in reply_bcc_recipients:
            reply_bcc_recipients_formatted.append(
                {"emailAddress": {"address": reply_bcc_recipient}}
            )

        data = {
            "message": {
                "toRecipients": reply_recipients_formatted,
                "ccRecipients": reply_cc_recipients_formatted,
                "bccRecipients": reply_bcc_recipients_formatted,
                "body": {"contentType": "HTML", "content": reply_body},
            }
        }

        url = (
            f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{email_id}/reply"
        )

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-type": "application/json",
        }

        try:
            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 202:
                return {
                    "status": "success",
                    "message": "Email reply sent successfully",
                    "recipients": reply_recipients_formatted,
                    "cc_recipients": reply_cc_recipients_formatted,
                    "bcc_recipients": reply_bcc_recipients_formatted,
                }
            else:
                error_message = "Failed to send email"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_message = error_data["error"].get(
                            "message", error_message
                        )
                except json.JSONDecodeError:
                    error_message = f"HTTP {response.status_code}: {response.reason}"

                return {
                    "status": "error",
                    "message": error_message,
                    "status_code": response.status_code,
                }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Request failed: {str(e)}"}

    def _find_email_sender(self, inbox, email_id):
        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{email_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()["from"]["emailAddress"]["address"]
        else:
            return None

    def _get_email_by_id(self, inbox, email_id):
        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{email_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def _find_email_recipients(self, inbox, email_id):
        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{email_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            recipients = []
            for recipient in response.json()["toRecipients"]:
                if recipient["emailAddress"]["address"] != inbox:
                    recipients.append(recipient["emailAddress"]["address"])
            return recipients
        else:
            return None

    def _find_email_cc_recipients(self, inbox, email_id):
        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{email_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            cc_recipients = []
            for cc_recipient in response.json()["ccRecipients"]:
                cc_recipients.append(cc_recipient["emailAddress"]["address"])
            return cc_recipients
        else:
            return None

    def _add_attachments_to_email(self, inbox, id, attachments):
        for attachment in attachments:
            if attachment.startswith("http"):
                file_content = self._get_file_from_url(attachment)
            else:
                file_content = self._get_file_from_local_file(attachment)

            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": file_content["filename"],
                "contentBytes": self._encode_file_into_base64(file_content["content"]),
            }
            url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{id}/attachments"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-type": "application/json",
            }

            response = requests.post(url, headers=headers, json=attachment)
            response.raise_for_status()
        return {
            "status": "success",
            "message": "Attachment added to email successfully",
            "id": response.json()["id"],
        }

    def _get_file_from_local_file(self, file_path):
        with open(file_path, "rb") as file:
            content = file.read()
            filename = os.path.basename(file_path)
            file_extension = os.path.splitext(filename)[1]

            return {
                "content": content,
                "filename": filename,
                "file_extension": file_extension,
                "size": len(content),
            }

    def _get_file_from_url(self, url):
        response = requests.get(url)
        response.raise_for_status()

        # Extract filename from URL
        parsed_url = urlparse(url)
        filename_from_url = os.path.basename(unquote(parsed_url.path))

        # Try to get filename from Content-Disposition header
        filename_from_header = None
        content_disposition = response.headers.get("Content-Disposition", "")
        if "filename=" in content_disposition:
            filename_from_header = content_disposition.split("filename=")[1].strip(
                "\"'"
            )

        # Determine final filename (prefer header over URL)
        filename = filename_from_header or filename_from_url or "downloaded_file"

        # Extract file extension
        file_extension = os.path.splitext(filename)[1] if filename else ""

        return {
            "content": response.content,
            "filename": filename,
            "file_extension": file_extension,
            "size": len(response.content),
        }

    def _encode_file_into_base64(self, file_content):
        return base64.b64encode(file_content).decode("utf-8")
