from datetime import timezone, datetime
import requests
from bson import ObjectId


class Utils:
    def __init__(self):
        pass

    def _generate_MS_graph_token(self, client_id, client_secret, tenant_id):
        access_token_url = (
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        )
        scope = "https://graph.microsoft.com/.default"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }
        try:
            response = requests.post(access_token_url, data=token_data)
            response.raise_for_status()
            return response.json()["access_token"]
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None

    def _return_result(self, status: str, message: str, content: dict = None):
        return {"status": status, "message": message, "content": content}

    def _format_date(self, date):
        if not date:
            return None

        if isinstance(date, str):
            try:
                date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                try:

                    date = datetime.strptime(date.split("+")[0], "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    try:

                        date = datetime.strptime(date.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")
                    except ValueError:

                        date = datetime.strptime(
                            date.rstrip("Z"), "%Y-%m-%dT%H:%M:%S.%f"
                        )
        return date.replace(tzinfo=timezone.utc)

    def _now_utc(self):
        return datetime.now(timezone.utc)

    def _remove_objectid(self, doc):
        """Helper to remove the _id field from a document and convert ObjectIds to strings."""
        if not doc:
            return doc

        if isinstance(doc, ObjectId):
            return str(doc)
        elif isinstance(doc, dict):
            doc = dict(doc)  # Make a copy to avoid mutating the original
            # Remove _id field if present
            if "_id" in doc:
                del doc["_id"]
            # Recursively process all values
            for key, value in doc.items():
                doc[key] = self._remove_objectid(value)
            return doc
        elif isinstance(doc, list):
            return [self._remove_objectid(item) for item in doc]
        else:
            return doc

    def _remove_objectid_from_list(self, data_list):
        """Helper to remove the _id field and convert ObjectIds from a list of documents."""
        if not data_list:
            return data_list

        # Process each item in the list
        for i, item in enumerate(data_list):
            data_list[i] = self._remove_objectid(item)

        return data_list

    def _convert_datetimes(self, obj):
        """Recursively convert datetime objects to ISO strings in dicts/lists."""
        if isinstance(obj, dict):
            return {k: self._convert_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_datetimes(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    def _display_query_details(
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
        storage,
    ) -> str:
        """
        Display human-readable query details based on user inputs
        """
        message_lines = ["📧 You've Got Mail Query Details:", "=" * 40]

        # Inbox information
        message_lines.append(f"📮 Target Inbox(es): {', '.join(inbox)}")

        # Date range information
        if range:
            date_now = self._now_utc().strftime("%Y-%m-%d %H:%M:%S")
            this_year = datetime.now().year
            this_month = datetime.now().month
            this_day = datetime.now().day
            previous_year = this_year - 1
            previous_month = this_month - 1
            previous_day = this_day - 1

            range_descriptions = {
                "previous_year": f"Previous calendar year (Jan 1 {previous_year} - Dec 31 {previous_year}), UTC",
                "previous_month": f"Previous calendar month ({previous_month}), UTC",
                "previous_week": f"Previous calendar week (Monday-Sunday) prior to {date_now}, UTC",
                "previous_day": f"Previous calendar day ({this_year}-{this_month}-{previous_day}), UTC",
                "last_365_days": f"Last 365 days prior to {date_now}, UTC",
                "last_30_days": f"Last 30 days prior to {date_now}, UTC",
                "last_7_days": f"Last 7 days prior to {date_now}, UTC",
                "last_24_hours": f"Last 24 hours prior to {date_now}, UTC",
                "last_12_hours": f"Last 12 hours prior to {date_now}, UTC",
                "last_8_hours": f"Last 8 hours prior to {date_now}, UTC",
                "last_hour": f"Last hour prior to {date_now}, UTC",
            }
            description = range_descriptions.get(range, f"Custom range: {range}")
            message_lines.append(f"📅 Date Range: {description}")
        elif start_date or end_date:
            message_lines.append("📅 Custom Date Range:")
            if start_date:
                start_display = f"{start_date}"
                if start_time:
                    start_display += f" {start_time}"
                message_lines.append(f"   From: {start_display}")
            if end_date:
                end_display = f"{end_date}"
                if end_time:
                    end_display += f" {end_time}"
                message_lines.append(f"   To: {end_display}")
        else:
            message_lines.append("📅 Date Range: Default (last 7 days)")

        # Email type filters
        type_filters = []
        if drafts:
            type_filters.append("Drafts only")
        elif not drafts:
            type_filters.append("Excluding drafts")

        if read:
            type_filters.append("Read emails only")
        elif not read:
            type_filters.append("Unread emails only")

        if archived:
            type_filters.append("Archived emails only")
        elif not archived:
            type_filters.append("Excluding archived")

        if deleted:
            type_filters.append("Deleted emails only")
        elif not deleted:
            type_filters.append("Excluding deleted")

        if sent:
            type_filters.append("Sent emails only")
        elif not sent:
            type_filters.append("Excluding sent emails")

        if type_filters:
            message_lines.append(f"📝 Email Types: {', '.join(type_filters)}")
        elif not type_filters:
            message_lines.append("📝 Email Types: All email types")

        # Sender filters
        if sender_address:
            message_lines.append("👤 Sender Email Filter:")
            for addr in sender_address:
                message_lines.append(f"   - {addr}")

        if sender_name:
            message_lines.append("👤 Sender Name Filter:")
            for name in sender_name:
                message_lines.append(f"   - {name}")

        # Recipient filters
        if recipients:
            message_lines.append("📨 Recipient Filter:")
            for recipient in recipients:
                message_lines.append(f"   - {recipient}")

        if cc:
            message_lines.append("📋 CC Filter:")
            for cc_addr in cc:
                message_lines.append(f"   - {cc_addr}")

        if bcc:
            message_lines.append("📄 BCC Filter:")
            for bcc_addr in bcc:
                message_lines.append(f"   - {bcc_addr}")

        # Subject filter
        if subject:
            message_lines.append("🏷️  Subject Filter:")
            for subj in subject:
                message_lines.append(f"   - Contains: '{subj}'")

        # Folder filter
        if folder_path:
            folder_display = " > ".join(folder_path)
            message_lines.append(f"📁 Folder Filter: {folder_display}")

        # Attachments
        if attachments:
            message_lines.append("📎 Attachments: retrieving attachments")
        elif not attachments:
            message_lines.append("📎 Attachments: not retrieving attachments")

        # Storage option
        if storage == "emails":
            message_lines.append("💾 Storage: Saving emails to database")
        elif storage == "emails_and_attachments":
            message_lines.append(
                "💾 Storage: Saving emails and attachments to database"
            )
        else:
            message_lines.append("💾 Storage: Not saving to database")

        message_lines.append("=" * 40)

        return "\n".join(message_lines)
