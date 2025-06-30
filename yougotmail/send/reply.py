import requests
import base64
from yougotmail._utils._utils import Utils
import os
from urllib.parse import urlparse, unquote
import json


class Reply:
    def __init__(self, client_id, client_secret, tenant_id):
        self.utils = Utils()
        self.token = self.utils._generate_MS_graph_token(
            client_id, client_secret, tenant_id
        )

    def reply_to_email(
        self, inbox="", email_id="", email_body="", cc_recipients=[], bcc_recipients=[]
    ):
        if inbox == "":
            raise Exception("Inbox is required")

        email_id = email_id.split("_")[-1]

        cc_recipients_formatted = []
        for cc_recipient in cc_recipients:
            cc_recipients_formatted.append({"emailAddress": {"address": cc_recipient}})
        bcc_recipients_formatted = []
        for bcc_recipient in bcc_recipients:
            bcc_recipients_formatted.append(
                {"emailAddress": {"address": bcc_recipient}}
            )

        data = {
            "message": {
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": self._find_email_sender(inbox, email_id)
                        }
                    }
                ],
                "ccRecipients": cc_recipients_formatted,
                "body": {"contentType": "HTML", "content": email_body},
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
