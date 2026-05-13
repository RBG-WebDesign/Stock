# config/settings.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Define base paths dynamically so the script runs from anywhere
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

MODEL_LIST = [
    "moonshotai/kimi-k2.5", # Input: $0.40 per 1M tokens, Output: $1.90 per 1M tokens
    "anthropic/claude-haiku-4.5", # Input: $1.0 per 1M tokens, Output: $5 per 1M tokens
    "anthropic/claude-opus-4.7", # Input: $5.0 per 1M tokens, Output: $25 per 1M tokens
    "google/gemini-2.5-flash", # Input: $0.30 per 1M tokens, Output: $2.50 per 1M tokens
    "google/gemini-3-flash-preview", # Input: $0.50 per 1M tokens, Output: $3.00 per 1M tokens
    "deepseek/deepseek-v4-pro", # Input: $0.435 per 1M tokens, Output: $0.87 per 1M tokens
    "deepseek/deepseek-v4-flash", # Input: $0.126 per 1M tokens, Output: $0.252 per 1M tokens
    "qwen/qwen3.6-plus", # Input: $0.325 per 1M tokens, Output: $1.95 per 1M tokens
]

class Settings(BaseSettings):
    """Global configuration settings for the Techno-Quantamental Analyzer."""
    
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