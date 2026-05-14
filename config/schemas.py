from pydantic import BaseModel, Field
from typing import Literal

class MasterAnalystOutput(BaseModel):
    """Schema for the comprehensive Quantamental Master Analyst prompt."""
    ticker: str = Field(..., description="The ticker symbol of the evaluated stock.")
    primary_pattern: str = Field(..., description="The primary technical pattern identified (e.g., Cup and Handle, High Tight Flag, VCP).")
    fundamental_catalyst: str = Field(..., description="A 1-3 sentence summary of the strongest fundamental driver (e.g., EPS growth, margins).")
    suggested_entry_pivot: float = Field(..., description="The exact dollar amount for the optimal breakout entry point.")
    suggested_stop_loss: float = Field(..., description="The exact dollar amount for the invalidation point or stop loss.")
    confidence_score: int = Field(..., ge=1, le=10, description="A score from 1 to 10 evaluating the alignment of fundamentals and technicals. 10 is perfect.")
    bull_case: str = Field(..., description="Thesis (1-3 sentences) for why this trade will succeed.")
    bear_case_risks: str = Field(..., description="Thesis (1-3 sentences) for the biggest risks or why this trade might fail.")

class CanSlimOutput(BaseModel):
    """Schema for the pure CAN SLIM growth prompt."""
    ticker: str = Field(..., description="The ticker symbol of the evaluated stock.")
    c_current_earnings: str = Field(..., description="Evaluation of recent quarterly earnings growth.")
    a_annual_earnings: str = Field(..., description="Evaluation of annual earnings growth.")
    n_new_catalyst: str = Field(..., description="Identification of new products, management, or price highs.")
    s_supply_demand: str = Field(..., description="Analysis of volume footprints and institutional accumulation.")
    l_leader_laggard: str = Field(..., description="Assessment of relative strength within its sector.")
    i_institutional_sponsorship: str = Field(..., description="Evaluation of big money backing or fund ownership.")
    m_market_direction: str = Field(..., description="Assessment of the broader market environment.")
    suggested_entry_pivot: float = Field(..., description="The exact dollar amount for the optimal breakout entry point.")
    suggested_stop_loss: float = Field(..., description="The exact dollar amount for the invalidation point or stop loss.")
    is_breakout_safe: bool = Field(..., description="True if the current environment and setup support a safe breakout, False otherwise.")
    confidence_score: int = Field(..., ge=1, le=10, description="Overall CAN SLIM grade from 1 to 10.")

class PriceActionEntryOutput(BaseModel):
    """Schema for the purely technical Price Action prompt."""
    ticker: str = Field(..., description="The ticker symbol of the evaluated stock.")
    market_structure: str = Field(..., description="Description of the trend, higher highs/lows, or Change of Character (CHoCH).")
    point_of_control: str = Field(..., description="The price zone with the heaviest volume consolidation.")
    base_classification: str = Field(..., description="The specific name of the consolidation base.")
    suggested_entry_pivot: float = Field(..., description="The optimal breakout entry price.")
    suggested_stop_loss: float = Field(..., description="The exact price where the technical setup is broken.")
