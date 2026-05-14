import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from config.settings import settings

class PipelineConfig(BaseModel):
    universe_limit: Optional[int] = 50
    model: Optional[str] = settings.DEFAULT_MODEL
    prompt_mode: Optional[str] = settings.DEFAULT_PROMPT_KEY
    save_prompts: bool = False
    news_summary_max_chars: Optional[int] = settings.NEWS_SUMMARY_MAX_CHARS
    max_recent_articles: Optional[int] = settings.MAX_RECENT_ARTICLES

class MarketCapConfig(BaseModel):
    min_m: Optional[float] = settings.DEFAULT_MIN_MARKET_CAP / 1_000_000
    max_m: Optional[float] = settings.DEFAULT_MAX_MARKET_CAP / 1_000_000

class FundamentalFiltersConfig(BaseModel):
    min_eps_growth: float = settings.DEFAULT_MIN_EPS_GROWTH
    min_rev_growth: float = settings.DEFAULT_MIN_REV_GROWTH
    max_rev_growth: Optional[float] = None
    min_prev_eps: Optional[float] = None
    max_prev_eps: Optional[float] = None
    min_latest_eps: Optional[float] = None
    require_acceleration: bool = False

class FullConfig(BaseModel):
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    market_cap: MarketCapConfig = Field(default_factory=MarketCapConfig)
    fundamental_filters: FundamentalFiltersConfig = Field(default_factory=FundamentalFiltersConfig)
    technical_filters: List[str] = Field(default_factory=lambda: [
        "price > sma_100",
        "price > sma_200",
        "sma_100 > sma_200",
        "sma_200 > sma_200_22d",
        "sma_50 > sma_100",
        "sma_50 > sma_200",
        "price > sma_50",
        "price >= 1.30 * low_52w",
        "price >= 0.75 * high_52w"
    ])

def load_config_file(path: Path) -> FullConfig:
    """Loads and validates a JSON configuration file."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    with open(path, "r") as f:
        data = json.load(f)
    
    # Validate with Pydantic
    return FullConfig(**data)
