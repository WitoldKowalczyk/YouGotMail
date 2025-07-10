from yougotmail import YouGotMail
import os
from dotenv import load_dotenv
import json

load_dotenv()

ygm = YouGotMail(
    client_id=os.environ.get("MS_CLIENT_ID"),
    client_secret=os.environ.get("MS_CLIENT_SECRET"),
    tenant_id=os.environ.get("MS_TENANT_ID"),
    open_ai_api_key=os.environ.get("OPENAI_API_KEY"),
)

def test_ai_agent_with_tools():
    try:
        prompt = input("Enter your prompt: ")
        response = ygm.ai_agent_with_tools(prompt=prompt)
        print(response)
    except Exception as e:
        print(f"Error: {e}")
