from yougotmail.ai._ai_handler import AIHandler
from typing import Any, Dict, List

class AI:
    def structured_output_from_email(self, *,
                                     email, 
                                     schema: Dict[str, Any]):
        schema = {
                "type": "json_schema",
                "json_schema": {
                    "name": "thread_questions_schema",
                    "description": "A schema for answering questions about the thread and its contents",
                    "schema": {
                        "type": "object",
                        "properties": {
                            **schema,
                        },
                        "required": list(schema.keys()),
                        "additionalProperties": False
                        }
                    }
                    }
        
        content_for_ai = f"""
            Here is the email: {email}
            """
        
        ai = AIHandler(
            prompt_name="EMAIL_EXTRACTION_PROMPT",
            schema=schema,
            content=content_for_ai
        )
        
        classification = ai.main()

        return classification

