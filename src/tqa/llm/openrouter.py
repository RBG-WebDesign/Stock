# src/tqa/llm/openrouter.py
import asyncio
import base64
import json
from datetime import datetime
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import aiohttp
from pydantic import ValidationError

from config.schemas import MasterAnalystOutput, CanSlimOutput, PriceActionEntryOutput
from config.settings import settings, BASE_DIR
from tqa.utils.logger import logger


async def encode_image_base64(image_path: str) -> str:
    """Encodes an image to a base64 string asynchronously."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found at {image_path}")
    
    def read_and_encode():
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    return await asyncio.to_thread(read_and_encode)


class OpenRouterClient:
    """
    Asynchronous client for OpenRouter API with Vision and JSON Schema support.
    """

    def __init__(self, api_key: str = settings.OPENROUTER_API_KEY, model: str = settings.DEFAULT_MODEL):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/vincerot/techno-quantamental-analyzer", # Optional but good practice for OpenRouter
            "X-Title": "Techno-Quantamental Analyzer",
        }
        self.prompts_config = self._load_prompts()
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    def _load_prompts(self) -> Dict[str, Any]:
        """Loads prompt templates from config/prompts.yaml."""
        prompt_path = BASE_DIR / "config" / "prompts.yaml"
        try:
            with open(prompt_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load prompts from {prompt_path}: {e}")
            return {}

    async def analyze_ticker(
        self,
        ticker: str,
        fundamentals: Dict[str, Any],
        chart_paths: Dict[str, str],
        prompt_key: str = "master_analyst"
    ) -> Tuple[Optional[Any], str]:
        """
        Sends fundamental data and charts to OpenRouter for comprehensive analysis.
        Returns a tuple of (analysis_result, prompt_string).
        """
        logger.info(f"Initiating OpenRouter analysis for {ticker} using {self.model} via {prompt_key}...")

        # 1. Prepare Prompts
        system_prompt = self.prompts_config.get("system_prompts", {}).get("swing_trader", "")
        user_template = self.prompts_config.get("user_prompts", {}).get(prompt_key, "")

        if not system_prompt or not user_template:
            logger.error(f"Missing prompt configuration for system_prompt or {prompt_key}")
            return None, ""

        # 2. Select Schema based on prompt_key
        schema_map = {
            "master_analyst": MasterAnalystOutput,
            "institutional_accumulator": MasterAnalystOutput,
            "can_slim_growth": CanSlimOutput,
            "price_action_entry": PriceActionEntryOutput
        }
        output_schema = schema_map.get(prompt_key, MasterAnalystOutput)

        # Format user prompt with ticker and fundamental JSON
        formatted_user_prompt = user_template.format(
            ticker=ticker,
            fundamentals=json.dumps(fundamentals, indent=2)
        )

        # 3. Encode Charts
        try:
            daily_b64 = await encode_image_base64(chart_paths.get("daily", ""))
            weekly_b64 = await encode_image_base64(chart_paths.get("weekly", ""))
        except Exception as e:
            logger.error(f"Error encoding charts for {ticker}: {e}")
            return None, formatted_user_prompt

        # 4. Construct Payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": formatted_user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{daily_b64}"}
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{weekly_b64}"}
                        }
                    ]
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "analyst_response",
                    "schema": output_schema.model_json_schema(),
                    "strict": True
                }
            }
        }

        # Save payload for debugging before sending
        await self._save_payload(ticker, payload)

        # 5. Execute Request
        try:
            if self._session:
                async with self._session.post(self.base_url, headers=self.headers, json=payload) as response:
                    analysis = await self._handle_response(response, ticker, output_schema)
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.base_url, headers=self.headers, json=payload) as response:
                        analysis = await self._handle_response(response, ticker, output_schema)
            
            return analysis, formatted_user_prompt

        except Exception as e:
            logger.error(f"Exception during OpenRouter analysis for {ticker}: {e}")
            return None, formatted_user_prompt

    async def _handle_response(self, response: aiohttp.ClientResponse, ticker: str, schema: Any) -> Optional[Any]:
        """Handles the API response, including error checking and parsing."""
        if response.status != 200:
            error_text = await response.text()
            logger.error(f"OpenRouter API error {response.status}: {error_text}")
            return None

        result = await response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        if not content:
            logger.error(f"Empty response from OpenRouter for {ticker}")
            return None

        return self._parse_and_validate(content, ticker, schema)

    def _parse_and_validate(self, content: str, ticker: str, schema: Any) -> Optional[Any]:
        """Robustly parses and validates the LLM output against the provided schema."""
        try:
            # 1. Cleaning: Remove potential markdown code blocks
            cleaned_content = content.strip()
            if cleaned_content.startswith("```"):
                # Remove starting ```json or ```
                cleaned_content = cleaned_content.split("\n", 1)[-1]
                # Remove ending ```
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content.rsplit("```", 1)[0]
            
            cleaned_content = cleaned_content.strip()

            # 2. JSON Decoding
            data = json.loads(cleaned_content)

            # 3. Schema Validation
            output = schema.model_validate(data)
            logger.info(f"Successfully received and validated analysis for {ticker} using {schema.__name__}")
            return output

        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding failed for {ticker}: {e}")
            logger.debug(f"Raw content: {content}")
        except ValidationError as e:
            logger.error(f"Pydantic validation failed for {ticker}: {e}")
            logger.debug(f"Decoded data: {data}")
        except Exception as e:
            logger.error(f"Unexpected error parsing response for {ticker}: {e}")
        
        return None

    async def _save_payload(self, ticker: str, payload: Dict[str, Any]):
        """Saves the raw JSON request payload to the payloads directory for debugging."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{ticker}_{timestamp}.json"
            filepath = settings.PAYLOADS_DIR / filename

            def write_json():
                with open(filepath, "w") as f:
                    json.dump(payload, f, indent=2)

            await asyncio.to_thread(write_json)
            logger.debug(f"Saved request payload to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save request payload for {ticker}: {e}")

        return None
