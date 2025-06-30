import requests
import json
import os
from datetime import timedelta
from yougotmail._utils._utils import Utils

utils = Utils()


def create_microsoft_graph_webhook(inbox: str, api_url: str, client_state: str):
    """
    Creates a Microsoft Graph webhook subscription for inbox messages
    """

    # You'll need to get an access token for Microsoft Graph API
    # This typically requires OAuth2 flow or app registration
    access_token = utils._generate_MS_graph_token(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        tenant_id=os.getenv("TENANT_ID"),
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


def validate_webhook_endpoint(url: str):
    """
    Test if the webhook endpoint is accessible
    """

    try:
        response = requests.get(url, timeout=10)
        print(f"Webhook endpoint test - Status: {response.status_code}")
        return response.status_code < 400
    except requests.exceptions.RequestException as e:
        print(f"Webhook endpoint test failed: {e}")
        return False
