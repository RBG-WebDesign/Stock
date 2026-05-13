# config/settings.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Define base paths dynamically so the script runs from anywhere
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

class Settings(BaseSettings):
    """Global configuration settings for the Techno-Quantamental Analyzer."""
    
    MODEL_LIST: list[str] = [
        "google/gemini-3-flash-preview",
        "google/gemini-2.5-flash",
        "qwen/qwen3.6-plus",
        "deepseek/deepseek-v4-flash",
        "deepseek/deepseek-v4-pro",
        "moonshotai/kimi-k2.5",
        "anthropic/claude-haiku-4.5",
        "anthropic/claude-opus-4.7",
    ]

    # --- API Keys ---
    FMP_API_KEY: str = Field(..., description="Financial Modeling Prep API Key")
    OPENROUTER_API_KEY: str = Field(..., description="OpenRouter API Key for sync testing")
    
    # FMP Subscription Plan (starter, premium)
    FMP_PLAN: str = Field(default="starter", description="FMP Subscription Plan")

    # Native keys for Phase 2 Batch API integration
    ANTHROPIC_API_KEY: str = Field(default="", description="Native Anthropic API Key")
    OPENAI_API_KEY: str = Field(default="", description="Native OpenAI API Key")
    
    # --- Pipeline Settings ---
    DEFAULT_MODEL: str = Field(
        default="moonshotai/kimi-k2.5", 
        description="The default model string to use for analysis"
    )

    DEFAULT_PROMPT_KEY: str = Field(
        default="master_analyst",
        description="The default prompt key from prompts.yaml to use for analysis"
    )
    
    MAX_CONCURRENT_LLM_REQUESTS: int = Field(
        default=10,
        description="Maximum number of concurrent LLM requests"
    )

    # --- Cache Settings ---
    CACHE_CLEANUP_DAYS: int = Field(
        default=365,
        description="Number of days to keep raw data in cache"
    )

    # --- LLM Payload Settings ---
    NEWS_SUMMARY_MAX_CHARS: int = Field(
        default=500,
        description="Maximum characters for news article summaries"
    )
    MAX_RECENT_ARTICLES: int = Field(
        default=10,
        description="Number of recent news articles to include in LLM payload"
    )

    # --- Directory Paths ---
    # These are used for our isolated file-based caching strategy
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    CHARTS_DIR: Path = DATA_DIR / "charts"
    PAYLOADS_DIR: Path = DATA_DIR / "payloads"
    REPORTS_DIR: Path = DATA_DIR / "reports"

    # Pydantic v2 Config to read from the .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignores other env vars not defined here
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Automatically create the required data directories on startup
        # to prevent FileNotFoundError during async I/O
        self.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.CHARTS_DIR.mkdir(parents=True, exist_ok=True)
        self.PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Instantiate a single global settings object to be imported across the project
# usage: from config.settings import settings
settings = Settings()