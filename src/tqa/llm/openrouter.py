# src/tqa/llm/openrouter.py
# Note: Rough draft 

from config.schemas import MasterAnalystOutput # Your Pydantic model
import json

payload = {
    "model": "openai/gpt-4o",
    "messages": [ ... ],
    # This forces the LLM to strictly adhere to your Pydantic schema
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "analyst_response",
            "schema": MasterAnalystOutput.model_json_schema(),
            "strict": True
        }
    }
}