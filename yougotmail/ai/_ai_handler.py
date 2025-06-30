from openai import OpenAI
import json
import yougotmail.ai._ai_prompts as prompts
import yougotmail.ai._ai_schemas as schemas
from textwrap import dedent


class AIHandler:
    def __init__(
        self,
        open_ai_api_key="",
        prompt="",
        prompt_name="",
        schema_name="",
        schema="",
        content="",
        model="gpt-4.1",
        reasoning_effort="",
    ):
        self.client = OpenAI(api_key=open_ai_api_key)
        self.prompt = prompt
        self.prompt_name = prompt_name
        self.schema_name = schema_name
        self.schema = schema
        self.prompts = prompts
        self.schemas = schemas
        self.content = content
        self.model = model
        self.reasoning_effort = reasoning_effort

    def main(self):
        if self.schema == "":
            schema = getattr(self.schemas, self.schema_name)
        else:
            schema = self.schema

        if self.prompt == "":
            prompt = getattr(self.prompts, self.prompt_name)
        else:
            prompt = self.prompt

        if isinstance(self.content, dict):
            self.content = json.dumps(self.content)

        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": dedent(prompt)},
                    {"role": "user", "content": self.content},
                ],
                response_format=schema,
            )

            response_content = json.loads(completion.choices[0].message.content)

            return response_content

        except Exception as e:
            print(
                f"\033[1;35mError in 3A4BE42D-4C6F-46A2-A2B7-6478A00FF9A2: {str(e)}\033[0m"
            )

    def completions(self):
        prompt = getattr(self.prompts, self.prompt_name)

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": dedent(prompt)},
                {"role": "user", "content": self.content},
            ],
            max_tokens=100,
        )
        response_content = completion.choices[0].message.content.strip()
        print(response_content)
        return response_content

    def reasoning(self):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                reasoning_effort=self.reasoning_effort,
                messages=[{"role": "user", "content": self.content}],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {e}")
