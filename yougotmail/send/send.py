import requests
import base64
from yougotmail._utils._utils import Utils
from yougotmail.storage.storage import Storage
import os
import json
from urllib.parse import urlparse, unquote


class Send:
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
        email_collection="emails",
        conversation_collection="conversations",
        attachment_collection="attachments",
    ):
        self.utils = Utils()
        self.token = self.utils._generate_MS_graph_token(
            client_id, client_secret, tenant_id
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

        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-type": "application/json",
        }

        if inbox == "":
            raise Exception("Inbox is required")

        # Fix: Don't overwrite the parameter arrays
        to_recipients_formatted = []
        for to_recipient in to_recipients:
            to_recipients_formatted.append({"emailAddress": {"address": to_recipient}})
        cc_recipients_formatted = []
        for cc_recipient in cc_recipients:
            cc_recipients_formatted.append({"emailAddress": {"address": cc_recipient}})
        bcc_recipients_formatted = []
        for bcc_recipient in bcc_recipients:
            bcc_recipients_formatted.append(
                {"emailAddress": {"address": bcc_recipient}}
            )

        data = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": email_body},
            "toRecipients": to_recipients_formatted,
            "ccRecipients": cc_recipients_formatted,
            "bccRecipients": bcc_recipients_formatted,
        }
        if importance != "":
            data["importance"] = importance

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        if attachments != []:
            self._add_attachments_to_email(inbox, response.json()["id"], attachments)

        return {
            "status": "success",
            "message": "Email drafted successfully",
            "id": response.json()["id"],
            "recipients": {
                "to": to_recipients,
                "cc": cc_recipients,
                "bcc": bcc_recipients,
            },
            "subject": subject,
        }

    def send_email_draft(self, inbox, id):
        if inbox == "":
            raise Exception("Inbox is required")
        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{id}/send"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-type": "application/json",
        }

        try:
            response = requests.post(url, headers=headers)

            if response.status_code == 202:
                return {"status": "success", "message": "Email sent successfully"}
            else:
                # Handle error cases gracefully
                error_message = "Failed to send email"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_message = error_data["error"].get(
                            "message", error_message
                        )
                except (json.JSONDecodeError, ValueError, KeyError):
                    error_message = f"HTTP {response.status_code}: {response.reason}"

                return {
                    "status": "error",
                    "message": error_message,
                    "status_code": response.status_code,
                }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Request failed: {str(e)}"}

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
        if inbox == "":
            raise Exception("Inbox is required")

        email_draft = self.draft_email(
            inbox,
            subject,
            importance,
            email_body,
            to_recipients,
            cc_recipients,
            bcc_recipients,
        )

        if attachments != []:
            self._add_attachments_to_email(inbox, email_draft["id"], attachments)

        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{email_draft['id']}/send"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-type": "application/json",
        }

        try:
            response = requests.post(url, headers=headers)

            if response.status_code == 202:
                print("Email sent successfully ✨")
                return {
                    "status": "success",
                    "message": "Email sent successfully",
                    "recipients": {
                        "to": to_recipients,
                        "cc": cc_recipients,
                        "bcc": bcc_recipients,
                    },
                    "subject": subject,
                    "body": email_body,
                }
            else:
                # Handle error cases gracefully
                error_message = "Failed to send email"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_message = error_data["error"].get(
                            "message", error_message
                        )
                except (json.JSONDecodeError, ValueError, KeyError):
                    error_message = f"HTTP {response.status_code}: {response.reason}"

                return {
                    "status": "error",
                    "message": error_message,
                    "status_code": response.status_code,
                }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Request failed: {str(e)}"}

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
