# src/tqa/utils/session_logger.py
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import settings

class SessionLogger:
    """
    Handles structured logging for a specific pipeline run (session).
    Saves prompts, responses, and configurations to a dedicated directory.
    """
    def __init__(self, session_id: Optional[str] = None):
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.session_id = session_id
        self.session_dir = settings.REPORTS_DIR / "runs" / session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.prompts_log_path = self.session_dir / "prompts_debug.jsonl"
        self.config_log_path = self.session_dir / "run_config.json"
        
        # Setup session-specific file logger
        self.logger = logging.getLogger(f"session.{session_id}")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.session_dir / "pipeline.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    async def log_config(self, config: Dict[str, Any]):
        """Saves the run configuration and settings."""
        def write_config():
            with open(self.config_log_path, "w") as f:
                json.dump(config, f, indent=2)
        
        await asyncio.to_thread(write_config)
        self.logger.info(f"Configuration saved to {self.config_log_path}")

    def _serialize_response(self, response: Any) -> Any:
        """Safely serializes various response types."""
        if response is None:
            return None
        
        # Handle Pydantic models (v2 model_dump, v1 dict)
        if hasattr(response, "model_dump"):
            try:
                return response.model_dump()
            except Exception as e:
                self.logger.warning(f"Failed to call model_dump: {e}")
        
        if hasattr(response, "dict") and callable(getattr(response, "dict")):
            try:
                return response.dict()
            except Exception as e:
                self.logger.warning(f"Failed to call dict(): {e}")

        # If it's already a basic type that json.dumps handles, return it
        if isinstance(response, (str, int, float, bool, list, dict)):
            return response

        # Fallback to string representation
        try:
            return str(response)
        except Exception:
            return "[Unserializable Response]"

    async def log_prompt(self, ticker: str, prompt: str, response: Any, model: str):
        """Logs a single LLM interaction with robust serialization and error handling."""
        try:
            # Validate required fields
            if not ticker or not model:
                self.logger.warning(f"Missing required fields for logging: ticker={ticker}, model={model}")
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "ticker": ticker or "UNKNOWN",
                "model": model or "UNKNOWN",
                "prompt": prompt or "",
                "response": self._serialize_response(response)
            }
            
            def append_log():
                with open(self.prompts_log_path, "a") as f:
                    f.write(json.dumps(entry) + "\n")
            
            await asyncio.to_thread(append_log)
            self.logger.debug(f"Logged LLM interaction for {ticker}")
        except Exception as e:
            # Prevent logging failures from crashing the pipeline
            self.logger.error(f"Failed to log prompt for {ticker}: {str(e)}")

    def log_info(self, message: str):
        self.logger.info(message)

    def log_error(self, message: str):
        self.logger.error(message)

# Global session instance (optional, can be initialized in main.py)
session: Optional[SessionLogger] = None

def init_session(session_id: Optional[str] = None) -> SessionLogger:
    global session
    session = SessionLogger(session_id)
    return session
