# You've Got Mail

Easily build AI Agents in MS Outlook.

![cover_image](public/cover_image.png)

## Quickstart

You will first need to set-up MS email credentials for your inbox. See [Getting MS credentials and setting up your inbox](#getting-ms-credentials-and-setting-up-your-inbox) for instructions. If you have those credentials, you can run the code below.

```bash
pip install yougotmail
```

```python
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

"""
Possible time ranges are:
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

TBD
