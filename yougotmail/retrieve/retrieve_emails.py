import requests
import datetime
from dateutil.parser import parse as parse_date
from yougotmail._utils._utils import Utils
from yougotmail.retrieve.retrieve_attachments import RetrieveAttachments
from yougotmail.retrieve.retrieval_utils import RetrievalUtils


class RetrieveEmails:
    def __init__(
        self,
        client_id,
        client_secret,
        tenant_id,
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
        self.utils = Utils()
        self.token = self.utils._generate_MS_graph_token(
            client_id, client_secret, tenant_id
        )

        # Store storage configuration but don't initialize yet
        self._storage_config = {
            "mongo_url": mongo_url,
            "mongo_db_name": mongo_db_name,
            "email_collection": email_collection,
            "conversation_collection": conversation_collection,
            "attachment_collection": attachment_collection,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "region_name": region_name,
            "bucket_name": bucket_name,
        }
        self._db_storage = None

        self.retrieve_attachments = RetrieveAttachments(
            client_id, client_secret, tenant_id, **self._storage_config
        )
        self.retrieval_utils = RetrievalUtils(client_id, client_secret, tenant_id)

    def _ensure_storage(self):
        """Lazy initialization of storage"""
        if self._db_storage is None:
            from yougotmail.storage.storage import Storage

            self._db_storage = Storage(**self._storage_config)
        return self._db_storage

    @property
    def db_storage(self):
        """Property to access storage only when needed"""
        return self._ensure_storage()

    def get_emails(
        self,
        *,
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
        attachments,
        storage,
    ):
        try:
            inboxes_list = []

            print(
                self.utils._display_query_details(
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
                    attachments,
                    storage,
                )
            )

            for inbox in inbox:
                print(f"\nSearching for emails in inbox {inbox} ")
                emails_from_one_inbox = self._get_emails_from_one_inbox(
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
                    attachments,
                )
                if emails_from_one_inbox is not None:
                    inboxes_list.append(emails_from_one_inbox)
                else:
                    return None

            if storage in ["emails", "emails_and_attachments"]:
                storage_instance = self._ensure_storage()
                if storage == "emails":
                    storage_instance.store_emails(inboxes_list)
                else:
                    storage_instance.store_emails_and_attachments(inboxes_list)
                inboxes_list = self.utils._convert_datetimes(
                    self.utils._remove_objectid_from_list(inboxes_list)
                )

            return inboxes_list

        except Exception as e:
            print(f"Error in get_emails: {e}")
            return None

    def _get_emails_from_one_inbox(
        self,
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
        attachments,
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
                emails_list = []
                page_count = 0
                email_count = 0
                while url and page_count < 100000:
                    page_count += 1
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    emails = data["value"]
                    next_page_link = data.get("@odata.nextLink")

                    for email in emails:
                        if not attachments:
                            attachment_list = []
                        elif attachments:
                            attachment_list = self.retrieve_attachments._get_attachments_from_one_email(
                                inbox, email
                            )
                        re_structured_email = self.retrieval_utils._re_structure_email(
                            email, inbox, attachment_list
                        )
                        filtered_email = self.retrieval_utils._filter_email_outputs(
                            re_structured_email, archived, deleted, sent
                        )
                        if filtered_email is not None:
                            email_count += 1
                            print(f"\nEmail {email_count} in {inbox}:")
                            print(f"  Inbox:     {inbox}")
                            print(
                                f"  From:      {filtered_email.get('sender_address')}"
                            )
                            print(f"  Subject:   {filtered_email.get('subject')}")
                            print(f"  Date:      {filtered_email.get('received_date')}")
                            print(f"  Folder:    {filtered_email.get('folder_name')}")
                            print(
                                f"  Attachments: {len(filtered_email.get('attachments', []))}"
                            )
                            emails_list.append(filtered_email)
                    url = next_page_link

            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
                return None

            if len(emails_list) == 0:
                result = {"inbox": inbox, "number_of_emails_found": 0, "emails": []}
                print(f"No emails found in inbox {inbox} for the given filters")
                return result

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

            return {
                "inbox": inbox,
                "number_of_emails_found": len(emails_list),
                "emails": emails_list,
            }
        except Exception as e:
            print(f"Error in _get_emails_from_one_inbox: {e}")
            return None

    def _get_emails_from_one_inbox_without_print(
        self,
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
        attachments,
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
                emails_list = []
                page_count = 0
                email_count = 0
                while url and page_count < 100000:
                    page_count += 1
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    emails = data["value"]
                    next_page_link = data.get("@odata.nextLink")

                    for email in emails:
                        if not attachments:
                            attachment_list = []
                        elif attachments:
                            attachment_list = self.retrieve_attachments._get_attachments_from_one_email(
                                inbox, email
                            )
                        re_structured_email = self.retrieval_utils._re_structure_email(
                            email, inbox, attachment_list
                        )
                        filtered_email = self.retrieval_utils._filter_email_outputs(
                            re_structured_email, archived, deleted, sent
                        )
                        if filtered_email is not None:
                            emails_list.append(filtered_email)
                    url = next_page_link

            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
                return None

            if len(emails_list) == 0:
                result = {"inbox": inbox, "number_of_emails_found": 0, "emails": []}
                return result

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

            return {
                "inbox": inbox,
                "number_of_emails_found": len(emails_list),
                "emails": emails_list,
            }
        except Exception as e:
            print(f"Error in _get_emails_from_one_inbox: {e}")
            return None
