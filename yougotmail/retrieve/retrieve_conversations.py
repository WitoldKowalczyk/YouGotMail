import requests
import datetime
from dateutil.parser import parse as parse_date
from yougotmail._utils._utils import Utils
from yougotmail.storage.storage import Storage
from yougotmail.retrieve.retrieve_emails import RetrieveEmails
from yougotmail.retrieve.retrieve_attachments import RetrieveAttachments
from yougotmail.retrieve.retrieval_utils import RetrievalUtils


class RetrieveConversations:
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
        self.retrieve_emails = RetrieveEmails(
            client_id,
            client_secret,
            tenant_id,
            mongo_url,
            mongo_db_name,
            aws_access_key_id,
            aws_secret_access_key,
            region_name,
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
        )
        self.mongo_db_storage = Storage(
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
        storage=None,
    ):
        try:
            if inbox == "":
                raise Exception("Inbox is required")
            if conversation_id != "":
                return self._get_conversation_by_conversation_id(
                    inbox, conversation_id, attachments, storage
                )

            # get all messages fitting criteria
            emails_matching_conversation_filters = (
                self.retrieve_emails._get_emails_from_one_inbox(
                    inbox=inbox,
                    range=range,
                    start_date=start_date,
                    start_time=start_time,
                    end_date=end_date,
                    end_time=end_time,
                    subject=[subject],
                    sender_name=[sender_name],
                    sender_address=[sender_address],
                    recipients=[],
                    cc=[],
                    bcc=[],
                    folder_path=[],
                    drafts=False,
                    archived=False,
                    deleted=False,
                    sent="all",
                    read=read,
                    attachments=attachments,
                )
            )

            if emails_matching_conversation_filters is None:
                print(f"No conversation found in inbox {inbox} for the given filters")
                return None
            emails_matching_conversation_filters = (
                emails_matching_conversation_filters.get("emails")
            )
            conversation_ids = set(
                [
                    email.get("conversation_id")
                    for email in emails_matching_conversation_filters
                ]
            )

            if len(conversation_ids) == 1:
                return self._get_conversation_by_conversation_id(
                    inbox, list(conversation_ids)[0], attachments, storage
                )
            elif len(conversation_ids) > 1:
                # Create a mapping of conversation IDs to their details
                conversation_details = []
                for email in emails_matching_conversation_filters:
                    conversation_details.append(
                        {
                            "conversation_id": email.get("conversation_id"),
                            "subject": email.get("subject"),
                            "sender": email.get("sender_address"),
                        }
                    )
                # Remove duplicates by converting to dictionary and back to list
                unique_conversations = list(
                    {v["conversation_id"]: v for v in conversation_details}.values()
                )
                number_of_conversations = len(unique_conversations)
                print(
                    f"More than one conversation found in inbox {inbox} for the given filters."
                )
                conversations_found_info = {
                    "number_of_conversations": number_of_conversations,
                    "conversations": unique_conversations,
                }
                print(conversations_found_info)
                return None
            else:
                print(f"No conversation found in inbox {inbox} for the given filters")
                return None
        except Exception as e:
            print(f"Error in get_conversation: {e}")
            return None

    def _re_structure_email_for_conversation(self, email, inbox, attachment_list):
        unique_body = email.get("uniqueBody", {}).get("content", "")
        if unique_body == "":
            body = email.get("body", {}).get("content", "")
        else:
            body = unique_body
        body = self.retrieval_utils._trim_reply_section(body)

        from_field = email.get("from", {}).get("emailAddress", {})
        sender_name = from_field.get("name", "")
        sender_address = from_field.get("address", "")

        return {
            "received_date": email["receivedDateTime"],
            "folder_name": self.retrieval_utils._get_folder_name(
                email["parentFolderId"], inbox
            ),
            "sender_name": sender_name,
            "sender_address": sender_address,
            "recipients": [
                {
                    "recipient_name": recipient["emailAddress"]["name"],
                    "recipient_address": recipient["emailAddress"]["address"],
                }
                for recipient in email["toRecipients"]
            ],
            "cc": [
                {
                    "cc_recipient_name": cc_recipient["emailAddress"]["name"],
                    "cc_recipient_address": cc_recipient["emailAddress"]["address"],
                }
                for cc_recipient in email["ccRecipients"]
            ],
            "bcc": [
                {
                    "bcc_recipient_name": bcc_recipient["emailAddress"]["name"],
                    "bcc_recipient_address": bcc_recipient["emailAddress"]["address"],
                }
                for bcc_recipient in email["bccRecipients"]
            ],
            "subject": email["subject"],
            "body": body,
            "attachments": attachment_list,
        }

    def _get_conversation_by_conversation_id(
        self, inbox, conversation_id, attachments, storage
    ):
        try:
            conversation_id_without_prefix = conversation_id.split("_")[1]
            url_filter = (
                f"$filter=conversationId eq '{conversation_id_without_prefix}'&"
                f"isDraft eq false&"
                f"$select=from,conversationId,hasAttachments,receivedDateTime,subject,toRecipients,ccRecipients,bccRecipients,uniqueBody,body,parentFolderId"
            )
            print(f"\033[1;35m{url_filter}\033[0m")
            url = (
                f"https://graph.microsoft.com/v1.0/users/{inbox}/messages?{url_filter}"
            )
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
                "Prefer": 'outlook.body-content-type="text"',
            }
            try:
                emails_list = []
                page_count = 0
                email_count = 0
                while url and page_count < 100000:
                    page_count += 1
                    # print(f"Getting page - {page_count}")
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    # print(data)
                    emails = data["value"]
                    next_page_link = data.get("@odata.nextLink")

                    for email in emails:
                        if not attachments:
                            attachment_list = []
                        elif attachments:
                            attachment_list = self.retrieve_attachments._get_attachments_from_one_email(
                                inbox, email
                            )
                        re_structured_email = self._re_structure_email_for_conversation(
                            email, inbox, attachment_list
                        )
                        filtered_email = self.retrieval_utils._filter_email_outputs(
                            re_structured_email,
                            archived=False,
                            deleted=False,
                            sent="all",
                        )
                        if filtered_email is not None:
                            email_count += 1
                            print_result = {
                                "count": email_count,
                                "inbox": inbox,
                                "sender": filtered_email.get("sender_address"),
                                "subject": filtered_email.get("subject"),
                                "datetime": filtered_email.get("received_date"),
                                "folder": filtered_email.get("folder_name"),
                            }
                            print(print_result)
                            emails_list.append(filtered_email)
                    url = next_page_link

            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
                return None

            if len(emails_list) == 0:
                print(f"No emails found in inbox {inbox} for the given filters")
                return None

            # Sort emails by received_date, most recent first
            def safe_parse_date(email):
                try:
                    received_date = email.get("received_date")
                    if received_date:
                        return parse_date(received_date)
                    else:
                        return (
                            datetime.datetime.min
                        )  # Put emails with no date at the end
                except Exception:
                    return datetime.datetime.min  # Put unparseable dates at the end

            emails_list.sort(key=safe_parse_date, reverse=True)

            conversation_object = {
                "inbox": inbox,
                "conversation_id": conversation_id,
                "number_of_emails_found": len(emails_list),
                "emails": emails_list,
            }

            if storage == "emails":
                self.mongo_db_storage.store_conversation(conversation_object)
                conversation_object = self.utils._convert_datetimes(
                    self.utils._remove_objectid_from_list(conversation_object)
                )
            elif storage == "emails_and_attachments":
                self.mongo_db_storage.store_conversation_and_attachments(
                    conversation_object
                )
                conversation_object = self.utils._convert_datetimes(
                    self.utils._remove_objectid_from_list(conversation_object)
                )

            return conversation_object
        except Exception as e:
            print(f"Error in get_conversation_by_conversation_id: {e}")
            return None
