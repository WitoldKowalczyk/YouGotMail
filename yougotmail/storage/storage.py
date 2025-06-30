from pymongo import MongoClient
import base64
import boto3
from yougotmail._utils._utils import Utils


class Storage:
    def __init__(
        self,
        mongo_url="",
        mongo_db_name="",
        aws_access_key_id="",
        aws_secret_access_key="",
        region_name="",
        bucket_name="",
        email_collection="",
        conversation_collection="",
        attachment_collection="",
    ):

        # Only initialize if all required parameters are provided
        if all(
            [
                mongo_url,
                mongo_db_name,
                aws_access_key_id,
                aws_secret_access_key,
                region_name,
                bucket_name,
            ]
        ):
            self.client = MongoClient(mongo_url)
            self.db = self.client.get_database(mongo_db_name)
            self.utils = Utils()

            # Default database collections
            self.emails_collection = self.db.get_collection(email_collection)
            self.conversations_collection = self.db.get_collection(
                conversation_collection
            )
            self.attachments_collection = self.db.get_collection(attachment_collection)

            # S3 client and bucket name
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name,
            )
            self.attachments_bucket_name = bucket_name
            self.enabled = True
        else:
            # Storage is disabled - set all to None
            self.client = None
            self.db = None
            self.utils = None
            self.emails_collection = None
            self.conversations_collection = None
            self.attachments_collection = None
            self.s3_client = None
            self.attachments_bucket_name = None
            self.enabled = False

    def store_emails(self, inbox_list):
        if not self.enabled:
            print("Storage is not configured - skipping email storage")
            return
        try:
            for inbox in inbox_list:
                for email in inbox["emails"]:
                    if self._check_if_email_exists(email["email_id"]):
                        print(
                            f"Email document already exists in mongo: {email['email_id']}"
                        )
                        continue
                    email["received_date"] = self.utils._format_date(
                        email["received_date"]
                    )
                    attachments = email["attachments"]
                    new_attachment_list = []
                    for attachment in attachments:
                        new_attachment = {
                            "attachment_id": attachment["attachment_id"],
                            "file_name": attachment["file_name"],
                            "date": self.utils._format_date(attachment["date"]),
                            "contentType": attachment["contentType"],
                        }
                        new_attachment_list.append(new_attachment)
                    email["attachments"] = new_attachment_list
                    self.emails_collection.insert_one(email)
                    print(f"Email document saved in mongo: {email['email_id']}")
        except Exception as e:
            print(f"Error in store_emails: {e}")
            return None

    def store_emails_and_attachments(self, inbox_list):
        if not self.enabled:
            print("Storage is not configured - skipping email storage")
            return
        try:
            for inbox in inbox_list:
                inbox_name = inbox["inbox"]
                emails = inbox["emails"]
                for email in emails:
                    if self._check_if_email_exists(email["email_id"]):
                        print(
                            f"Email document already exists in mongo: {email['email_id']}"
                        )
                        continue
                    email["received_date"] = self.utils._format_date(
                        email["received_date"]
                    )
                    attachments = email["attachments"]
                    if attachments:
                        new_attachment_list = []
                        for attachment in attachments:
                            file_metadata = self._store_attachments_in_s3(
                                inbox_name, email["email_id"], attachment
                            )
                            new_attachment = {
                                "attachment_id": attachment["attachment_id"],
                                "file_name": attachment["file_name"],
                                "date": self.utils._format_date(attachment["date"]),
                                "contentType": attachment["contentType"],
                                "url": file_metadata["url"],
                            }
                            new_attachment_list.append(new_attachment)
                        email["attachments"] = new_attachment_list
                    self.emails_collection.insert_one(email)
                    print(f"Email document saved in mongo: {email['email_id']}")
        except Exception as e:
            print(f"Error in store_emails: {e}")
            return None

    def store_attachments(self, attachments_list):
        if not self.enabled:
            print("Storage is not configured - skipping attachment storage")
            return
        for inbox in attachments_list:
            for attachment in inbox["attachments"]:
                if self._check_if_attachment_exists(attachment["attachment_id"]):
                    print(
                        f"Attachment document already exists in mongo: {attachment['attachment_id']}"
                    )
                    continue
                file_metadata = self._store_attachments_in_s3(
                    inbox["inbox"], attachment
                )
                new_attachment = {
                    "attachment_id": attachment["attachment_id"],
                    "file_name": attachment["file_name"],
                    "date": self.utils._format_date(attachment["date"]),
                    "contentType": attachment["contentType"],
                    "url": file_metadata["url"],
                }
                self.attachments_collection.insert_one(new_attachment)
                print(
                    f"Attachment document saved in mongo: {attachment['attachment_id']}"
                )

    def _check_if_email_exists(self, email_id):
        if not self.enabled:
            return False
        existing_email = self.emails_collection.find_one({"email_id": email_id})
        if existing_email:
            return True
        else:
            return False

    def _check_if_attachment_exists(self, attachment_id):
        if not self.enabled:
            return False
        existing_attachment = self.attachments_collection.find_one(
            {"attachment_id": attachment_id}
        )
        if existing_attachment:
            return True
        else:
            return False

    def _check_if_conversation_exists(self, conversation_id):
        if not self.enabled:
            return False
        existing_conversation = self.conversations_collection.find_one(
            {"conversation_id": conversation_id}
        )
        if existing_conversation:
            return True
        else:
            return False

    def _store_attachments_in_s3(self, inbox_name, email_id, attachment):
        if not self.enabled:
            return None
        try:
            attachment_id = attachment["attachment_id"]
            file_name = attachment["file_name"]
            file_extension = file_name.split(".")[-1]
            file_date = attachment["date"]
            file_name_with_underscores = attachment["file_name"].replace(" ", "_")
            contentType = ""
            body = ""

            if file_extension == "pdf":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "application/pdf"
            elif file_extension == "xlsx":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            elif file_extension == "docx":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif file_extension == "pptx":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            elif file_extension == "doc":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif file_extension == "txt":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "text/plain"
            elif file_extension == "csv":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "text/csv"
            elif file_extension == "xls":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            elif file_extension == "rtf":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "application/rtf"
            elif file_extension == "png":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "image/png"
            elif file_extension == "jpg":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "image/jpeg"
            elif file_extension == "jpeg":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "image/jpeg"
            elif file_extension == "gif":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "image/gif"
            elif file_extension == "bmp":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "image/bmp"
            elif file_extension == "ico":
                body = base64.b64decode(attachment["contentBytes"])
                contentType = "image/vnd.microsoft.icon"

            s3_metadata = {
                "inbox": inbox_name,
                "email_id": email_id,
                "attachment_id": attachment_id,
                "file_name": file_name,
                "date": file_date,
                "contentType": contentType,
                "url": f"https://{self.attachments_bucket_name}.s3.amazonaws.com/{file_date}_{file_name_with_underscores}",
            }

            self.s3_client.put_object(
                Bucket=self.attachments_bucket_name,
                Key=file_name,
                Body=body,
                ContentType=contentType,
                Metadata=s3_metadata,
            )

            return s3_metadata
        except Exception as e:
            print(f"Error in _store_attachments_in_s3: {e}")
            return None

    def store_conversation(self, conversation_object):
        if not self.enabled:
            print("Storage is not configured - skipping conversation storage")
            return
        emails = conversation_object["emails"]
        new_attachments = []
        for email in emails:
            attachments = email["attachments"]
            for attachment in attachments:
                new_attachment = {
                    "attachment_id": attachment["attachment_id"],
                    "file_name": attachment["file_name"],
                    "date": self.utils._format_date(attachment["date"]),
                    "contentType": attachment["contentType"],
                }
                new_attachments.append(new_attachment)
            email["attachments"] = new_attachments
        conversation_object["emails"] = emails
        if self._check_if_conversation_exists(conversation_object["conversation_id"]):
            self.conversations_collection.update_one(
                {"conversation_id": conversation_object["conversation_id"]},
                {"$set": conversation_object},
            )
            print(
                f"Updated conversation document saved in mongo: {conversation_object['conversation_id']}"
            )
        else:
            self.conversations_collection.insert_one(conversation_object)
            print(
                f"New conversation document saved in mongo: {conversation_object['conversation_id']}"
            )

    def store_conversation_and_attachments(self, conversation_object):
        if not self.enabled:
            print("Storage is not configured - skipping conversation storage")
            return
        if self._check_if_conversation_exists(conversation_object["conversation_id"]):
            print(
                f"Conversation document already exists in mongo: {conversation_object['conversation_id']}"
            )
            return
        emails = conversation_object["emails"]
        new_attachments = []
        for email in emails:
            attachments = email["attachments"]
            for attachment in attachments:
                file_metadata = self._store_attachments_in_s3(
                    conversation_object["inbox"], email["email_id"], attachment
                )
                new_attachment = {
                    "attachment_id": attachment["attachment_id"],
                    "file_name": attachment["file_name"],
                    "date": self.utils._format_date(attachment["date"]),
                    "contentType": attachment["contentType"],
                    "url": file_metadata["url"],
                }
                new_attachments.append(new_attachment)
            email["attachments"] = new_attachments
        conversation_object["emails"] = emails
        if self._check_if_conversation_exists(conversation_object["conversation_id"]):
            self.conversations_collection.update_one(
                {"conversation_id": conversation_object["conversation_id"]},
                {"$set": conversation_object},
            )
            print(
                f"Updated conversation document saved in mongo: {conversation_object['conversation_id']}"
            )
        else:
            self.conversations_collection.insert_one(conversation_object)
            print(
                f"New conversation document saved in mongo: {conversation_object['conversation_id']}"
            )
