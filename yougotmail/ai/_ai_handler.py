import json
from yougotmail.ai._ai_tools import AI_TOOLS
from textwrap import dedent


class AIHandler:
    def __init__(self, open_ai_api_key):
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=open_ai_api_key)
        except ImportError:
            raise ImportError(
                "OpenAI package is not installed. Install it with 'pip install yougotmail[openai]'"
            )

    def _content(self, content):
        if isinstance(content, dict):
            content = json.dumps(content)
        return content

    def text_generation(self, instructions="", prompt="", model="gpt-4.1"):
        try:
            response = self.client.responses.create(
                model=model, instructions=dedent(instructions), input=prompt
            )
            return response.output_text
        except Exception as e:
            print(f"An error occurred in text_generation: {str(e)}")

    def structured_outputs(self, prompt="", schema="", content="", model="gpt-4.1"):
        try:
            completion = self.client.beta.chat.completions.parse(
                model=model,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": dedent(prompt)},
                    {"role": "user", "content": self._content(content)},
                ],
                response_format=schema,
            )
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            print(f"An error occurred in structured_outputs: {str(e)}")

    def reasoning(self, prompt="", reasoning_effort="medium", model="o4-mini"):
        try:
            response = self.client.responses.create(
                model=model,
                reasoning={"effort": f"{reasoning_effort}"},
                input=[{"role": "user", "content": prompt}],
            )

            return response.output_text
        except Exception as e:
            print(f"An error occurred: {e}")

    def process_image(self, prompt="", image_url="", model="gpt-4.1"):
        try:
            response = self.client.responses.create(
                model=model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {
                                "type": "input_image",
                                "image_url": image_url,
                            },
                        ],
                    }
                ],
            )
            return response.output_text
        except Exception as e:
            print(f"An error occurred in process_image: {str(e)}")

    def function_calling(
        self, instructions="", prompt="", model="gpt-4.1", tools=[], ai_tools=""
    ):
        try:
            # Initialize conversation history
            conversation_history = [
                {"role": "developer", "content": dedent(instructions)},
                {"role": "user", "content": prompt},
            ]

            while True:
                response = self.client.responses.create(
                    model=model, 
                    input=conversation_history, 
                    tools=tools, 
                    tool_choice="auto"
                )
                tool_call = response.output[0]

                if tool_call.type == "function_call":
                    args = json.loads(tool_call.arguments)
                    result = ai_tools._ai_function_router(tool_call.name, args)

                    conversation_history.append(tool_call)
                    conversation_history.append(
                        {
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": str(result),
                        }
                    )
                else:
                    # Add assistant's response to conversation history
                    conversation_history.append({
                        "role": "assistant",
                        "content": response.output_text
                    })
                    
                    # Display assistant's response to user
                    print("\nAssistant:", response.output_text)
                    
                    # Get user input for continuation
                    print("\nUser (type 'exit' to end conversation):", end=" ")
                    user_input = input()
                    
                    # Check if user wants to exit
                    if user_input.lower() == 'exit':
                        return response.output_text
                    
                    # Add user's input to conversation history
                    conversation_history.append({
                        "role": "user",
                        "content": user_input
                    })

        except Exception as e:
            print(f"An error occurred in function_calling: {e}")
            raise
