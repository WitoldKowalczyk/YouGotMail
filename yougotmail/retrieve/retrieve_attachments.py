import requests
import base64
from yougotmail._utils._utils import Utils
from yougotmail.storage.storage import Storage
from yougotmail.retrieve.retrieval_utils import RetrievalUtils


class RetrieveAttachments:
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
        self.retrieval_utils = RetrievalUtils(
            client_id,
            client_secret,
            tenant_id,
            mongo_url,
            mongo_db_name,
            aws_access_key_id,
            aws_secret_access_key,
            region_name,
        )

    def get_attachments(
        self,
        inbox,
        range,
        start_date,  # can be date: YYYY-MM-DD or datetime YYYY-MM-DDT00:00:00Z
        start_time,
        end_date,  # can be date: YYYY-MM-DD or datetime YYYY-MM-DDT00:00:00Z
        end_time,
        subject,
        sender_name,
        sender_address,
        recipients,
        cc,
        bcc,
        folder_path,
        drafts,
        archived,
        deleted,
        sent,
        read,
        storage,
    ):
        try:
            attachments_list = []
            if inbox == []:
                raise Exception("Inbox is required")
            if range != "" and (
                start_date != "" or end_date != "" or start_time != "" or end_time != ""
            ):
                raise Exception(
                    "Start date and end date are not allowed when range is provided"
                )

            for inbox in inbox:
                attachments_from_one_inbox = self._get_attachments_for_one_inbox(
                    inbox,
                    range,
                    start_date,
                    start_time,
                    end_date,
                    end_time,
                    subject,
                    sender_name,
                    sender_address,
                    recipients,
                    cc,
                    bcc,
                    folder_path,
                    drafts,
                    archived,
                    deleted,
                    sent,
                    read,
                )
                if attachments_from_one_inbox is not None:
                    attachments_list.append(attachments_from_one_inbox)
                else:
                    return None

            if storage and len(attachments_list) > 0:
                self.storage.store_attachments(attachments_list)
                attachments_list = self.utils._convert_datetimes(
                    self.utils._remove_objectid_from_list(attachments_list)
                )

            return attachments_list

        except Exception as e:
            print(f"Error in get_attachments: {e}")
            return None

    def _get_attachments_for_one_inbox(
        self,
        inbox,
        range,
        start_date,  # can be date: YYYY-MM-DD or datetime YYYY-MM-DDT00:00:00Z
        start_time,
        end_date,  # can be date: YYYY-MM-DD or datetime YYYY-MM-DDT00:00:00Z
        end_time,
        subject,
        sender_name,
        sender_address,
        recipients,
        cc,
        bcc,
        folder_path,
        drafts,
        archived,
        deleted,
        sent,
        read,
    ):
        try:
            url_filter = self.retrieval_utils._create_filter_url(
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
                read=read,
            )

            url = (
                f"https://graph.microsoft.com/v1.0/users/{inbox}/messages?{url_filter}"
            )

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
                "Prefer": 'outlook.body-content-type="text"',
            }

            try:
                output_attachments_list = []
                page_count = 0
                while url and page_count < 100000:
                    page_count += 1
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    emails = data["value"]
                    next_page_link = data.get("@odata.nextLink")

                    for email in emails:
                        attachment_list = self._get_attachments_from_one_email(
                            inbox, email
                        )
                        re_structured_email = self._re_structure_email_for_attachments(
                            email, inbox, attachment_list
                        )
                        filtered_email = self.retrieval_utils._filter_email_outputs(
                            re_structured_email, archived, deleted, sent
                        )
                        if filtered_email is not None:
                            attachments = filtered_email.get("attachments")
                            output_attachments_list.extend(attachments)
                    url = next_page_link

            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
                return None

            if len(output_attachments_list) == 0:
                return None

            return {
                "inbox": inbox,
                "number_of_attachments_found": len(output_attachments_list),
                "attachments": output_attachments_list,
            }
        except Exception as e:
            print(f"Error in _get_attachments_for_one_inbox: {e}")
            return None

    def _get_attachments_from_one_email(self, inbox, email):
        try:
            attachments = []
            if email is not None:
                email_id = email["id"]
                has_attachments = email.get("hasAttachments", False)
                if not has_attachments:
                    return []

            url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{email_id}/attachments"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            values = data["value"]

            for value in values:
                attachment_id = value.get("id", "")
                attachment_url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{email_id}/attachments/{attachment_id}/$value"
                attachment_response = requests.get(attachment_url, headers=headers)
                attachment_response.raise_for_status()

                attachment = {
                    "attachment_id": "attachment_" + attachment_id,
                    "file_name": value["name"],
                    "date": value["lastModifiedDateTime"],
                    "contentType": value["contentType"],
                    "contentBytes": base64.b64encode(
                        attachment_response.content
                    ).decode("utf-8"),
                }
                attachments.append(attachment)

            return attachments

        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None

    def _re_structure_email_for_attachments(self, email, inbox, attachment_list):
        unique_body = email.get("uniqueBody", {}).get("content", "")
        if unique_body == "":
            body = email.get("body", {}).get("content", "")
        else:
            body = unique_body
        body = self.retrieval_utils._trim_reply_section(body)

        from_field = email.get("from", {}).get("emailAddress", {})
        sender_address = from_field.get("address", "")
        new_attachment_list = []
        for attachment in attachment_list:
            attachment_object = {
                "inbox": inbox,
                "sender_address": sender_address,
                "file_name": attachment["file_name"],
                "date": attachment["date"],
                "contentType": attachment["contentType"],
                "contentBytes": attachment["contentBytes"],
            }
            new_attachment_list.append(attachment_object)
        return {
            "folder_name": self.retrieval_utils._get_folder_name(
                email["parentFolderId"], inbox
            ),
            "attachments": new_attachment_list,
        }
