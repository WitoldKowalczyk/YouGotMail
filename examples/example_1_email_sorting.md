## Intro

In this example, we will be using the `yougotmail` library to sort emails into folders based on their topic.

We want every email that lands in our inbox to be sorted into a folder based on its topic.

## Step 1: Install yougotmail and the yougotmail with OpenAI dependency

You need to install both yougotmail and the yougotmail with OpenAI dependency since we will need it to extract structured outputs from emails.

```bash
pip install yougotmail
pip install "yougotmail[openai]"
```

## Step 2: Initialize the YouGotMail class with the MS credentials + the OpenAI key since we'll be using structured outputs

```python
from yougotmail import YouGotMail
import os

ygm = YouGotMail(
    client_id=os.environ.get("MS_CLIENT_ID"),
    client_secret=os.environ.get("MS_CLIENT_SECRET"),
    tenant_id=os.environ.get("MS_TENANT_ID"),
    open_ai_api_key=os.environ.get("OPENAI_API_KEY")
)
```

## Step 3: Get the emails from the inbox with the `ai_get_emails_with_structured_output()` method

This method allows us to retrieve emails from the inbox and directly extract structured outputs from them.

Users can pass the properties of the schema they want extracted from the emails as well as instructions for the AI to follow.
We'll use the instructions to tell the AI how to classify specific emails into the categories we want. Those can be custom defined and adjusted to our needs. For example - you can narrow it down to specific words or language (ie. all emails containing "Acme NYC" should be classified as "acme_project").

Note: you don't need to pass a full JSON schema, just individual properties you need.

In this example we specify the time range to be the last hour. We assume this could be a cron job that runs every hour and performs the sorting. for all emails from the last hour.

```python

INBOX="user@example.com"

emails = ygm.ai_get_emails_with_structured_output(
    inbox=[INBOX],
    range="last_hour",
    schema={
        "email_topic": {
            "type": "string",
            "description": "The topic of the email and what it is about",
            "enum": ["marketing", "acme_project", "front_end_product_roadmap", "back_end_product_roadmap", "other"]
        },
    },
    instructions=f"""
    Emails are about marketing if they contain mentions of marketing.
    Emails are about acme_project if they contain mentions of acme project.
    Emails are about front_end_product_roadmap if they contain mentions of front end product roadmap.
    Emails are about back_end_product_roadmap if they contain mentions of back end product roadmap.
    Emails are about other if they contain mentions of other.
    """
)
```
## Step 4: Move the emails to the appropriate folders

The emails are returned as a list of inboxes with a list of emails retrieved for each inbox.

```json
[
    {
        "inbox": "user_1@example.com",
        "emails": []
    },
    {
        "inbox": "user_2@example.com",
        "emails": []
    }
]
```

If you're retrieving emails from only 1 inbox, you can grab emails from the first inbox.


```python
emails = emails[0]["emails"]
```

Then for each email we retrieve the `structured_output` and the `email_topic` from it. Based on the topic selected we assign the email to the appropriate folder.

```python
for email in emails:
    email_id = email["email_id"]
    email_topic = email["structured_output"]["email_topic"]
    if email_topic == "front_end_product_roadmap":
        response = ygm.move_email_to_folder(
            inbox=INBOX, 
            email_id=email_id, 
            folder_path="Roadmaps/Front-end" # no need to mention inbox, just use the sub-folder path that comes after it (the assumption is all your folder are sub-folders of the Inbox)
            )
        print(response)
    elif email_topic == "back_end_product_roadmap":
        response = ygm.move_email_to_folder(inbox=INBOX, email_id=email_id, folder_path="Roadmaps/Back-end")
        print(response)
    elif email_topic == "marketing":
        response = ygm.move_email_to_folder(inbox=INBOX, email_id=email_id, folder_path="Marketing")
        print(response)
    elif email_topic == "acme_project":
        response = ygm.move_email_to_folder(inbox=INBOX, email_id=email_id, folder_path="Acme Project")
        print(response)
    elif email_topic == "other":
        response = ygm.move_email_to_folder(inbox=INBOX, email_id=email_id, folder_path="Other")
        print(response)
    else:
        print(f"Email {email_id} is not about front_end_product_roadmap, back_end_product_roadmap, marketing, acme_project or other")
```

## Step 5: Run the script

```bash
python example_1_email_sorting.py
```
