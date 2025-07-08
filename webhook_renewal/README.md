# Webhook Renewal Cron Job in AWS Lambda

This folder contains the code for the AWS Lambda function that renews the webhooks for an inbox. This is a cron job that runs daily at 00:00 UTC to renew the webhooks for an inbox.

## Setup

### 1. Create a new AWS Lambda function.

Create a new AWS Lambda function and name it for e.g. "webhook_renewal".

Use Python 3.10 and x86_64 for the runtime.

### 2. Add the following environment variables in configuration:

- INBOX: The inbox to renew the webhooks for.
- MS_CLIENT_ID: The client ID of the app.
- MS_CLIENT_SECRET: The client secret of the app.
- MS_TENANT_ID: The tenant ID of the app.

### 2. Install the dependencies:

Create a new project:

```bash
mkdir webhook_renewal
cd webhook_renewal
```

Create a new folder called "dependencies" in the root of the project.

```bash
mkdir dependencies
```

Install the yougotmail library into dependencies:

```bash
pip install --target ./dependencies yougotmail
```

### 3. Create a new file called "lambda_function.py" in the root of the project.

```bash
touch lambda_function.py
```

### 4. Add the following code to the lambda function:

```python
import os
from yougotmail import YouGotMail

INBOX = os.environ.get("INBOX")
MS_CLIENT_ID = os.environ.get("MS_CLIENT_ID")
MS_CLIENT_SECRET = os.environ.get("MS_CLIENT_SECRET")
MS_TENANT_ID = os.environ.get("MS_TENANT_ID")

def lambda_handler(event, context):

    ygm = YouGotMail(
        client_id=MS_CLIENT_ID,
        client_secret=MS_CLIENT_SECRET,
        tenant_id=MS_TENANT_ID
    )

    renew_subscriptions = ygm.renew_subscriptions(
        inbox=INBOX)
    
    print(renew_subscriptions)

    return {}
```

### 5. Zip the dependencies and the lambda function:

```bash
cd dependencies
zip -r ../deployment.zip *
cd ..

zip -r deployment.zip lambda_function.py
```

### 6. Update the lambda function code with the zip file:

```bash
aws lambda update-function-code --function-name webhook_renewal --zip-file fileb://deployment.zip
```

Note: you should have your AWS CLI configured with the correct permissions to update the lambda function code.

### 7. Set up a cron job in AWS

- Go into Scheduler in AWS Lambda and create a new rule. Name it for e.g. "webhook_renewal".
- Set the schedule to "rate" and set the value to "rate(1 day)".
- Set the target to the lambda function you created.
- Click on "Create rule".