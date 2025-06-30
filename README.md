# You've Got Mail

Easily build AI Agents in MS Outlook.

![cover_image](public/cover_image.png)

Table of Contents
- [Introduction](#introduction)
- [Quickstart](#quickstart)
- [Getting MS credentials and setting up your inbox](#getting-ms-credentials-and-setting-up-your-inbox)
- [Structured Outputs from emails with OpenAI](#structured-outputs-from-emails-with-openai)
- [Roadmap & Planned functionalities](#roadmap--planned-functionalities)

## Introduction

MS Outlook is one of the most popular email clients among enterprises and business users.
In some roles - handling email is almost the entire job. People receive emails, extract data from them, pass that data to other systems, retrieve data from those systems and send it via email. And so it goes.

Hence, building AI solutions that can 

Furthermore, emails are a natural communication method that humans know and use daily.
Creating AI Agents that can live in an email environment offers a natural way of interacting with AI systems. For example an AI CC'd into a conversation could easily perform tasks that the parties of the email thread want handled.

Building integrations into MS Outlook is particularly painful. because (as all things Microsoft) the API has many rules that make it time-consuming to build anything.

This library is meant to facilitate that. At the same time it will offer 3 types of AI solutions:
- a set of AI helper functions meant to facilite the work with email retrieval and email sending (e.g. structured outputs from emails)
- an AI Agent that lives in your inbox and handles email work for you
- an AI agent that acts as a standalone inbox operatord can be used as an AI interface

## Quickstart: getting emails

You will first need to set-up MS email credentials for your inbox. See [Getting MS credentials and setting up your inbox](#getting-ms-credentials-and-setting-up-your-inbox) for instructions. If you have those credentials, you can run the code below.

```bash
pip install yougotmail
```

```python
import os
from yougotmail import YouGotMail

inbox = "yougotmail@outlook.com" # the email address of the inbox on which you will be operating

ygm = YouGotMail(
    client_id=os.environ.get("MS_CLIENT_ID"),
    client_secret=os.environ.get("MS_CLIENT_SECRET"),
    tenant_id=os.environ.get("MS_TENANT_ID")
)

emails = ygm.get_emails(
    inbox=[inbox], # list of inboxes from which you're retrieving emails
    range="last_30_minutes", # the time range 
    attachments=False # whether to include attachments in the emails or not
)

print(emails)

"""
Possible time ranges are
- previous_year (year before the the current year, e.g. 2024 if the current year is 2025)
- previous_month
- previous_week
- previous_day

- last_365_days (last 365 days until the current date)
- last_30_days
- last_7_days
- last_24_hours
- last_12_hours
- last_8_hours
- last_hour
- last_30_minutes
- last_hour
- last_30_minutes
"""
```

## Getting MS credentials and setting up your inbox

To connect yougotmail to your Outlook inbox we need to do 3 things:

1. Create a new "app" in Azure Entra  
2. Grant this app permissions to access the various email functionalities (read, draft, send)
3. Retrieve 3 unique ids that will be used to authenticate access to the inbox:
    - client_id
    - client_secret 
    - tenant_id

### Step 1: Login to your Microsoft Entra account at https://entra.microsoft.com/

You can use your normal MS login. Ideally you should be the admin user in your org. If not that's ok, we will need to ask the admin to authorize the specific conditions.

### Step 2: Go into Applications & Retrieve the Tenant Id

Once logged in, you can go into Applications. In the main Applications Dashboard you should see the tenant id for your org. You can copy it from here and store it.

![ms_setup_1.png](public/ms_setup_1.png)

### Step 3: Under Applications, go into App registrations

Click on "New registration" to create a new app.

![ms_setup_2.png](public/ms_setup_2.png)

You can select "Accounts in this organizational directory only (Your Organization Name only - Single tenant)"

![ms_setup_3.png](public/ms_setup_3.png)

### Step 4: Retrieve the client_id

Once created, you can grab the "Application (client) ID" from the application's dashboard. This is our "client_id".

Almost there - 2 down - 1 to go!

![ms_setup_4.png](public/ms_setup_4.png)

### Step 5: Create a new secret

In the sidebar of the application (not your Entra sidebar) you have "Certificates & secrets". In there you can click on "New client secret". You can leave the Description blank.A new secret will be created - you can copy the id in the "Value" columne (NOT one in the "Secret ID" - thanks Microsoft for this create UX!). You have now your "client_secret" that we will use to instatiate the YouGotEmail class. Success!

Note: the secret will expire after 6 months. The date is shown in the Expires column. Make a note of it and set-up some calendar reminders.

![ms_setup_5.png](public/ms_setup_5.png)

### Step 6: Grant your app permissions to the email API

The final thing we need to do is grant your app permissions to the email API. From the app's sidebar click on "API permissions". Then "Add a permission". Select MS Graph.

Select "Application permissions".


![ms_setup_6.png](public/ms_setup_6.png)

Chose "Application permissions".

![ms_setup_7.png](public/ms_setup_7.png)

From the list of API permissions select all related to email. You can type "Mail" in the search bar. Including MailboxFolder, MailboxItem, Mailbox Settings, Mail, User-Mail.

![ms_setup_8.png](public/ms_setup_8.png)

Finally, each permission requires Admin access. If you're the Admin you can click on the button at the top of the permissions table. If you're not, you need to send a request to your admin. Click on "Grant admin consent for <your org name>".

![ms_setup_10.png](public/ms_setup_10.png)

![ms_setup_9.png](public/ms_setup_9.png)

Step 7: Run Quickstart code

You can now run the Quickstart code by passing

## Quickstart: Structured Outputs from emails with OpenAI

You can pass your OpenAI API key to the YouGotMail class and call the `ai_get_emails_with_structured_output()` method to retrieve emails from MS Outlook and have OpenAI structured output from the email body. You will need to pass a schema of the info you want extracted from the email body.

```python
import os
from yougotmail import YouGotMail

inbox = "yougotmail@outlook.com" # the email address of the inbox on which you will be operating

ygm = YouGotMail(
            client_id=os.environ.get("MS_CLIENT_ID"),
            client_secret=os.environ.get("MS_CLIENT_SECRET"),
            tenant_id=os.environ.get("MS_TENANT_ID"),
            open_ai_api_key=os.environ.get("OPENAI_API_KEY")
            )


emails = ygm.ai_get_emails_with_structured_output(
    inbox=[inbox],
    range="last_8_hours",
    attachments=False,
    schema={
        "topic": {"type": "string", "description": "The topic of the email"},
        "sentiment": {"type": "string", "description": "what was the mood of the email"}
        }
        )

print(emails)
```

## Quickstart: Sending emails

```python
import os
from yougotmail import YouGotMail

inbox = "yougotmail@outlook.com" # the email address of the inbox from which you will be sending

ygm = YouGotMail(
    client_id=os.environ.get("MS_CLIENT_ID"),
    client_secret=os.environ.get("MS_CLIENT_SECRET"),
    tenant_id=os.environ.get("MS_TENANT_ID")
)

result = ygm.send_email(
    inbox=inbox,
    subject="Meeting Follow-up",
    importance="Normal", # "Low", "Normal", or "High" or empty
    email_body="<html><body><h1>Test Email</h1><p>This is a test email sent from YouGotMail.</p></body></html>", # Structure in HTML
    to_recipients=["colleague@company.com", "manager@company.com"], # list of email addresses
    cc_recipients=["team-lead@company.com"], # list of email addresses
    bcc_recipients=[], # list of email addresses
    attachments=["https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"] # list of file paths to attach
)

print(result)

# Returns:
# {
#     "status": "success",
#     "message": "Email sent successfully",
#     "recipients": {
#         "to": ["colleague@company.com", "manager@company.com"],
#         "cc": ["team-lead@company.com"],
#         "bcc": []
#     },
#     "subject": "Meeting Follow-up",
#     "body": "Hi team,..."
# }
```


## Roadmap & Planned functionalities

I will be releasing updates every few days after I complete the testing for the given methods.

Here are the planned capabilities:

1. Retrieve Emails
2. Retrieve conversations
3. Retrieve attachments
4. Send emails
5. Reply to emails
6. Storage in MongoDB and AWS
7. AI features for parsing emails
8. An AI agent that performs tasks in your inbox for you
9. A standalone AI agent that owns and runs a given inbox (and can perform specific actions - e.g. check database)
