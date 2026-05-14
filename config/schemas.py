from pydantic import BaseModel, Field
from typing import Optional

class BaseAnalysisOutput(BaseModel):
    """Base schema for all LLM analysis outputs to ensure pipeline compatibility."""
    ticker: str = Field(..., description="The ticker symbol of the evaluated stock.")
    suggested_entry_pivot: float = Field(..., description="The exact dollar amount for the optimal breakout entry point.")
    suggested_stop_loss: float = Field(..., description="The exact dollar amount for the invalidation point or stop loss.")
    confidence_score: int = Field(..., ge=1, le=10, description="A score from 1 to 10 evaluating the setup. 10 is perfect.")

class MasterAnalystOutput(BaseAnalysisOutput):
    """Schema for the comprehensive Quantamental Master Analyst prompt."""
    primary_pattern: str = Field(..., description="The primary technical pattern identified (e.g., Cup and Handle, High Tight Flag, VCP).")
    fundamental_catalyst: str = Field(..., description="A 1-3 sentence summary of the strongest fundamental driver (e.g., EPS growth, margins).")
    bull_case: str = Field(..., description="Thesis (1-3 sentences) for why this trade will succeed.")
    bear_case_risks: str = Field(..., description="Thesis (1-3 sentences) for the biggest risks or why this trade might fail.")

class CanSlimOutput(BaseAnalysisOutput):
    """Schema for the pure CAN SLIM growth prompt."""
    c_current_earnings: str = Field(..., description="Evaluation of recent quarterly earnings growth.")
    a_annual_earnings: str = Field(..., description="Evaluation of annual earnings growth.")
    n_new_catalyst: str = Field(..., description="Identification of new products, management, or price highs.")
    s_supply_demand: str = Field(..., description="Analysis of volume footprints and institutional accumulation.")
    l_leader_laggard: str = Field(..., description="Assessment of relative strength within its sector.")
    i_institutional_sponsorship: str = Field(..., description="Evaluation of big money backing or fund ownership.")
    m_market_direction: str = Field(..., description="Assessment of the broader market environment.")
    is_breakout_safe: bool = Field(..., description="True if the current environment and setup support a safe breakout, False otherwise.")

class PriceActionEntryOutput(BaseAnalysisOutput):
    """Schema for the purely technical Price Action prompt."""
    market_structure: str = Field(..., description="Description of the trend, higher highs/lows, or Change of Character (CHoCH).")
    point_of_control: str = Field(..., description="The price zone with the heaviest volume consolidation.")
    base_classification: str = Field(..., description="The specific name of the consolidation base.")

class InstitutionalAccumulatorOutput(BaseAnalysisOutput):
    """Schema for the Institutional Accumulation focused prompt."""
    institutional_trend_analysis: str = Field(..., description="Deep dive into supply_demand.institutional_trend and ownership %.")
    pocket_pivots_identified: str = Field(..., description="Analysis of volume spikes within the base coming from moving averages.")
    analyst_sentiment_summary: str = Field(..., description="Summary of reputable analyst firm ratings and price targets.")
    price_volume_footprint: str = Field(..., description="Comparison of wide-range up days vs down days on high volume.")
    base_tightness_grading: str = Field(..., description="Grading of how tight the price action is on the right side of the base.")
