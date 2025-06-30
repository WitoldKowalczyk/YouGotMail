import requests
import datetime
import re
from yougotmail._utils._utils import Utils
from yougotmail.storage.storage import Storage


class RetrievalUtils:
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

    def _refine_dates_for_range(
        self, range, start_date, end_date, start_time, end_time
    ):
        # Use UTC consistently for all calculations
        now_utc = datetime.datetime.now(datetime.timezone.utc)

        if range == "previous_year":
            # Previous calendar year (Jan 1st to Dec 31st of previous year)
            current_year = now_utc.year
            previous_year = current_year - 1

            # Start: January 1st of previous year at 00:00:00
            start_dt = datetime.datetime(
                previous_year, 1, 1, 0, 0, 0, 0, datetime.timezone.utc
            )

            # End: December 31st of previous year at 23:59:59
            end_dt = datetime.datetime(
                previous_year, 12, 31, 23, 59, 59, 999999, datetime.timezone.utc
            )
        elif range == "previous_month":
            # Previous calendar month
            # Get first day of current month
            first_day_current_month = now_utc.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

            # Get last day of previous month
            end_dt = first_day_current_month - datetime.timedelta(microseconds=1)

            # Get first day of previous month
            start_dt = end_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # Set end to last second of previous month
            end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif range == "previous_week":
            # Previous Monday-Sunday week
            # Get current weekday (Monday=0, Sunday=6)
            current_weekday = now_utc.weekday()

            # Calculate days to previous Monday (start of previous week)
            days_to_prev_monday = current_weekday + 7  # Go back to previous Monday

            # Set start to previous Monday at 00:00:00
            start_dt = (now_utc - datetime.timedelta(days=days_to_prev_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            # Set end to previous Sunday at 23:59:59
            end_dt = (start_dt + datetime.timedelta(days=6)).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        elif range == "previous_day":
            yesterday = now_utc - datetime.timedelta(days=1)
            start_dt = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = yesterday.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        elif range == "last_365_days":
            start_dt = now_utc - datetime.timedelta(days=365)
            end_dt = now_utc
        elif range == "last_30_days":
            start_dt = now_utc - datetime.timedelta(days=30)
            end_dt = now_utc
        elif range == "last_7_days":
            start_dt = now_utc - datetime.timedelta(days=7)
            end_dt = now_utc
        elif range == "last_24_hours":
            start_dt = now_utc - datetime.timedelta(hours=24)
            end_dt = now_utc
        elif range == "last_12_hours":
            start_dt = now_utc - datetime.timedelta(hours=12)
            end_dt = now_utc
        elif range == "last_8_hours":
            start_dt = now_utc - datetime.timedelta(hours=8)
            end_dt = now_utc
        elif range == "last_hour":
            start_dt = now_utc - datetime.timedelta(hours=1)
            end_dt = now_utc
        elif range == "last_30_minutes":
            start_dt = now_utc - datetime.timedelta(minutes=30)
            end_dt = now_utc
        else:
            if not start_date:
                start_dt = now_utc - datetime.timedelta(days=7)
            else:
                start_dt = datetime.datetime.strptime(
                    f"{start_date} {start_time or '00:00:00'}", "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=datetime.timezone.utc)

            if not end_date:
                end_dt = now_utc
            else:
                end_dt = datetime.datetime.strptime(
                    f"{end_date} {end_time or '23:59:59'}", "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=datetime.timezone.utc)

        start_date_filter = (
            f"receivedDateTime ge {start_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        )
        end_date_filter = f"receivedDateTime le {end_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}"

        return start_date_filter, end_date_filter

    def _trim_reply_section(self, body: str) -> str:
        """
        Trim an email body to remove quoted replies based on common patterns like:
        - 'On 15 Jun 2025, at 12:27'
        - 'On Wed, Jun 11, 2025 at 5:57 AM, John Doe <...>'

        Parameters
        ----------
        body : str
            The full text of the email (plain text or simplified markdown).

        Returns
        -------
        str
            The trimmed message, excluding any quoted reply section.
        """
        # Common quoted-reply intro formats (loosely defined for real-world variability)
        patterns = [
            r"\nOn \d{1,2} \w{3,9} \d{4}, at \d{1,2}:\d{2}",  # e.g. On 15 Jun 2025, at 12:27
            r"\nOn (?:\w{3},?\s)?\w{3,9} \d{1,2}, \d{4} at \d{1,2}:\d{2}(?: [APMapm]{2})?, .+?<",  # On Wed, Jun 11, 2025 at 5:57 AM, John <
        ]

        for pattern in patterns:
            match = re.search(pattern, body)
            if match:
                return body[: match.start()].rstrip()

        return body.strip()

    def _re_structure_email(self, email, inbox, attachment_list):
        unique_body = email.get("uniqueBody", {}).get("content", "")
        if unique_body == "":
            body = email.get("body", {}).get("content", "")
        else:
            body = unique_body
        body = self._trim_reply_section(body)

        from_field = email.get("from", {}).get("emailAddress", {})
        sender_name = from_field.get("name", "")
        sender_address = from_field.get("address", "")

        return {
            "email_id": "email_" + email["id"],
            "received_date": email["receivedDateTime"],
            "folder_name": self._get_folder_name(email["parentFolderId"], inbox),
            "sender_name": sender_name,
            "sender_address": sender_address,
            "conversation_id": "conversation_" + email["conversationId"],
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

    def _get_child_folder_id(self, parent_id: str, name: str, inbox: str) -> str:
        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/mailFolders/{parent_id}/childFolders"
        headers = {"Authorization": f"Bearer {self.token}"}
        while url:
            resp = requests.get(url, headers=headers).json()
            for folder in resp.get("value", []):
                if folder.get("displayName") == name:
                    return folder.get("id")
            url = resp.get("@odata.nextLink")  # Follow pagination if present
        raise Exception(f"Folder '{name}' not found in {parent_id}")

    def _resolve_folder_path(self, path: list[str], inbox: str) -> str:
        folder_id = "inbox"
        print(path)
        for part in path:
            print(f"\033[1;31mSearching for folder {part} in {folder_id}\033[0m")
            folder_id = self._get_child_folder_id(
                parent_id=folder_id, name=part, inbox=inbox
            )
        return folder_id

    def _get_folder_name(self, folder_id: str, inbox: str) -> str:
        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/mailFolders/{folder_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.get(url, headers=headers).json()
        return resp.get("displayName")

    def _create_filter_url(
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
        read,
    ):
        filter_list = []

        start_date_filter, end_date_filter = self._refine_dates_for_range(
            range, start_date, end_date, start_time, end_time
        )
        filter_list.append(start_date_filter)
        filter_list.append(end_date_filter)

        if subject != []:
            subject_filter = " or ".join(
                [f"contains(subject,'{subject_part}')" for subject_part in subject]
            )
            subject_filter = f"({subject_filter})"
            filter_list.append(subject_filter)

        if sender_name != []:
            sender_name_filter = " or ".join(
                [
                    f"contains(from/emailAddress/name,'{sender_name_part}')"
                    for sender_name_part in sender_name
                ]
            )
            sender_name_filter = f"({sender_name_filter})"
            filter_list.append(sender_name_filter)

        if sender_address != []:
            sender_address_filter = " or ".join(
                [
                    f"contains(from/emailAddress/address,'{sender_address_part}')"
                    for sender_address_part in sender_address
                ]
            )
            sender_address_filter = f"({sender_address_filter})"
            filter_list.append(sender_address_filter)

        if recipients != []:
            recipients_filter = " or ".join(
                [
                    f"toRecipients/any(r:contains(r/emailAddress/address,'{recipient_part}'))"
                    for recipient_part in recipients
                ]
            )
            recipients_filter = f"({recipients_filter})"
            filter_list.append(recipients_filter)

        if cc != []:
            cc_filter = " or ".join(
                [
                    f"ccRecipients/any(c:contains(c/emailAddress/address,'{cc_part}'))"
                    for cc_part in cc
                ]
            )
            cc_filter = f"({cc_filter})"
            filter_list.append(cc_filter)

        if bcc != []:
            bcc_filter = " or ".join(
                [
                    f"bccRecipients/any(b:contains(b/emailAddress/address,'{bcc_part}'))"
                    for bcc_part in bcc
                ]
            )
            bcc_filter = f"({bcc_filter})"
            filter_list.append(bcc_filter)

        if folder_path != []:
            folder_id = self._resolve_folder_path(folder_path, inbox)
            folder_filter = f"parentFolderId eq '{folder_id}'"
            folder_filter = f"({folder_filter})"
            filter_list.append(folder_filter)

        if drafts == "all":
            pass
        elif drafts:
            filter_list.append("isDraft eq true")
        else:
            filter_list.append("isDraft eq false")

        if read == "all":
            pass
        elif read:
            filter_list.append("isRead eq true")
        else:
            filter_list.append("isRead eq false")

        filter_string = " and ".join(filter_list)

        url_filter = (
            f"$filter=({filter_string})&"
            f"$select=from,conversationId,hasAttachments,receivedDateTime,subject,toRecipients,ccRecipients,bccRecipients,uniqueBody,body,parentFolderId"
        )

        return url_filter

    def _filter_email_outputs(self, email, archived=False, deleted=False, sent=False):
        email_folder_name = email.get("folder_name")

        if archived == "all":
            pass
        elif not archived:
            if email_folder_name == "Archive":
                return None
        else:
            if email_folder_name != "Archive":
                return None
        
        if deleted == "all":
            pass
        elif not deleted:
            if email_folder_name == "Deleted Items":
                return None
        else:
            if email_folder_name != "Deleted Items":
                return None

        # Logic for returning sent or not sent or both emails
        if sent == "all":
            pass
        elif not sent:
            if email_folder_name == "Sent Items":
                return None
        else:
            if email_folder_name != "Sent Items":
                return None

        return email
