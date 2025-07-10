import requests
from yougotmail._utils._utils import Utils
from yougotmail.retrieve.retrieval_utils import RetrievalUtils
from yougotmail.retrieve.retrieve_conversations import RetrieveConversations


class MoveDelete:
    def __init__(self, client_id, client_secret, tenant_id):
        self.utils = Utils()
        self.retrieval_utils = RetrievalUtils(client_id, client_secret, tenant_id)
        self.retrieve_conversations = RetrieveConversations(
            client_id, client_secret, tenant_id
        )
        self.token = self.utils._generate_MS_graph_token(
            client_id, client_secret, tenant_id
        )

    def move_email_to_folder(self, inbox="", email_id="", folder_path=""):
        folder_id = self.retrieval_utils._resolve_folder_path(folder_path, inbox)
        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{email_id}/move"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"destinationId": folder_id}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code in [200, 201]:
            return {
                "status": "success", 
                "message": "Email moved to folder ✨",
                "email_id": email_id,
                "sender_name": response.json()["sender"]["emailAddress"]["name"],
                "subject": response.json()["subject"],
                "folder_path": folder_path
            }
        else:
            return {
                "status": "error",
                "message": "Failed to move email to folder ❌",
                "error": response.text
            }

    def delete_email(self, inbox="", email_id=""):
        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/messages/{email_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(url, headers=headers)
        if response.status_code in [200, 204]:
            return {
                "status": "success",
                "message": "Email deleted ✨",
                "email_id": email_id
            }
        else:
            return {
                "status": "error",
                "message": "Failed to delete email ❌",
                "error": response.text
            }

    def delete_conversation_by_id(self, inbox="", conversation_id=""):
        url = f"https://graph.microsoft.com/v1.0/users/{inbox}/conversations/{conversation_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(url, headers=headers)
        if response.status_code in [200, 204]:
            return {
                "status": "success",
                "message": "Conversation deleted ✨",
                "conversation_id": conversation_id
            }
        else:
            return {
                "status": "error",
                "message": "Failed to delete conversation ❌",
                "error": response.text
            }

    def delete_conversation(
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
        conversation = self.retrieve_conversations.get_conversation(
            inbox=inbox,
            conversation_id=conversation_id,
            range=range,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            subject=subject,
            sender_name=sender_name,
            sender_address=sender_address,
            read=read,
            attachments=attachments,
            storage=storage,
        )
        return self.delete_conversation_by_id(inbox, conversation["id"])
