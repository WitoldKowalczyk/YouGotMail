# Changelog

All notable changes to this project will be documented in this file.

## [0.0.1] - 2025-06-28
### Added
- `YouGotMail` class for retrieving emails from MS Outlook
- `get_emails()` method for retrieving emails from MS Outlook. For now, it was tested for retrieval with time ranges.

## [0.0.2] - 2025-06-28
### Added
- `ai_get_emails_with_structured_output()` method for retrieving emails from MS Outlook and extracting structured output from the email body.
- `ai_structured_output_from_email_body()` method for extracting structured output from the email body.

## [0.0.3] - 2025-06-30
### Added
- minor fixes

## [0.0.4] - 2025-06-30
### Added
- `send_email()` method for sending emails from MS Outlook.
- minor fixes
- updated docs

## [0.0.5] - 2025-07-05
### Added
- `create_microsoft_graph_webhook()` method for creating a Microsoft Graph webhook.
- `get_active_subscriptions_for_inbox()` method for getting active subscriptions for an inbox.
- `renew_subscriptions()` method for renewing subscriptions for an inbox.
- `delete_subscription()` method for deleting a subscription.
- `validate_webhook_endpoint()` method for validating a webhook endpoint.
### Changed
- updated docs and instructions
- modified installation & dependency handling - basic install comes without OpenAI, AWS or MongoDB dependencies. You can use `pip install yougotmail[openai]` to install the dependencies for OpenAI, `pip install yougotmail[boto3]` to install the dependencies for AWS, or `pip install yougotmail[pymongo]` to install the dependencies for MongoDB.

## [0.0.6] - 2025-07-06
### Changed
- minor fixes

## [0.0.7] - 2025-07-06
### Changed
- minor fixes

## [0.0.8] - 2025-07-06
### Changed
- minor fixes

## [0.0.9] - 2025-07-06
### Changed
- minor fixes

## [0.0.10] - 2025-07-06
### Changed
- minor fixes

## [0.0.11] - 2025-07-08
### Added
- `ai_agent_with_tools()` method for running an AI agent with tools.
- `test_ai_agent.py` file for testing the AI agent with tools.
- `test_ai_parsing.py` file for testing the AI parsing functionality.
- `test_ai_agent_with_tools.py` file for testing the AI agent with tools.

### Changed
- `storage` parameter to `get_emails()` method for storing emails and attachments in MongoDB.
- `conversation_2.json` file for testing the AI parsing functionality.
- `test_ai_agent_with_tools.py` file for testing the AI agent with tools.
- `test_ai_agent_with_tools.py` file for testing the AI agent with tools.
- `test_ai_agent_with_tools.py` file for testing the AI agent with tools.

## [0.0.12] - 2025-07-08
### Added
- minor fixes

## [0.0.13] - 2025-07-09
### Changed
- re-factored Ai structured outputs from email