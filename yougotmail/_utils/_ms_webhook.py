import requests
import json
from datetime import timedelta
from yougotmail._utils._utils import Utils
from datetime import datetime, timezone

utils = Utils()


class MSWebhook:
    def __init__(self, client_id, client_secret, tenant_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.utils = Utils()

    def create_microsoft_graph_webhook(
        self, inbox: str, api_url: str, client_state: str
    ):
        """
        Creates a Microsoft Graph webhook subscription for inbox messages
        """

        access_token = self.utils._generate_MS_graph_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
        )

        if not access_token:
            print("Error: MICROSOFT_GRAPH_ACCESS_TOKEN environment variable not set")
            return None

        url = "https://graph.microsoft.com/v1.0/subscriptions"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Calculate expiration datetime (max 3 days for mail resources)
        expiration_time = utils._now_utc() + timedelta(
            days=2, hours=23
        )  # Just under 3 days
        expiration_iso = expiration_time.strftime("%Y-%m-%dT%H:%M:%S.0000000Z")

        payload = {
            "changeType": "created",
            "notificationUrl": api_url,
            "resource": f"/users/{inbox}/mailfolders('inbox')/messages",
            "expirationDateTime": expiration_iso,
            "clientState": client_state,
        }

        try:
            print(f"Making POST request to: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")

            response = requests.post(url, headers=headers, json=payload)

            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")

            if response.status_code in [200, 201]:
                subscription_data = response.json()
                print("Webhook subscription created successfully!")
                print(f"Subscription ID: {subscription_data.get('id')}")
                print(f"Response: {json.dumps(subscription_data, indent=2)}")
                return subscription_data
            else:
                print("Error creating webhook subscription:")
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {response.text}")
            return None

    def get_active_subscriptions_for_inbox(self, inbox):
        token = self.utils._generate_MS_graph_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
        )

        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(
            "https://graph.microsoft.com/v1.0/subscriptions", headers=headers
        )
        response.raise_for_status()

        subscriptions = response.json().get("value", [])

        matching_subs = [
            sub
            for sub in subscriptions
            if f"/users/{inbox.lower()}/mailfolders('inbox')/messages"
            in sub["resource"].lower()
        ]

        result = {
            "total_subscriptions": len(matching_subs),
            "inbox": inbox,
            "subscriptions": [
                {
                    "id": sub["id"],
                    "expiration_date_time": sub["expirationDateTime"],
                    "notification_url": sub["notificationUrl"],
                }
                for sub in matching_subs
            ],
        }

        return result

    def renew_subscriptions(self, target_inbox):
        token = self.utils._generate_MS_graph_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Get current subscriptions
        r = requests.get(
            "https://graph.microsoft.com/v1.0/subscriptions", headers=headers
        )
        r.raise_for_status()
        subscriptions = r.json().get("value", [])

        renewals = 0

        for sub in subscriptions:
            sub_id = sub["id"]
            extracted_inbox = (
                sub["resource"]
                .split("/users/")[1]
                .split("/mailfolders('inbox')/messages")[0]
            )
            if extracted_inbox.lower() != target_inbox.lower():
                continue

            expiration = datetime.fromisoformat(
                sub["expirationDateTime"].replace("Z", "+00:00")
            )

            # Renew if expiring within 36h
            if expiration - datetime.now(timezone.utc) < timedelta(hours=36):
                # Format the expiration time exactly as Microsoft expects it
                new_expiration = (
                    datetime.now(timezone.utc) + timedelta(days=2, hours=23)
                ).strftime("%Y-%m-%dT%H:%M:%S.0000000Z")
                print(f"🔁 Renewing subscription {sub_id} (expires at {expiration})")

                patch_body = {"expirationDateTime": new_expiration}
                patch = requests.patch(
                    f"https://graph.microsoft.com/v1.0/subscriptions/{sub_id}",
                    headers=headers,
                    json=patch_body,
                )
                print(f"🔧 Renewal response: {patch.status_code} - {patch.text}")
                if patch.status_code == 200:
                    renewals += 1

        return {
            "status": "done",
            "subscriptions_checked": len(subscriptions),
            "inbox": target_inbox,
            "message": (
                f"renewed {renewals} subscriptions"
                if renewals > 0
                else "no subscriptions renewed"
            ),
        }

    def delete_subscription(self, subscription_id):
        url = f"https://graph.microsoft.com/v1.0/subscriptions/{subscription_id}"
        headers = {
            "Authorization": f"Bearer {self.utils._generate_MS_graph_token(self.client_id, self.client_secret, self.tenant_id)}",
            "Content-Type": "application/json",
        }
        response = requests.delete(url, headers=headers)
        return response.json()
