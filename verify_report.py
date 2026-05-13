# verify_report.py
import os
import json
from pathlib import Path
from src.tqa.utils.report_builder import generate_pdf_report
from config.settings import settings

def create_mock_data():
    session_id = "test_session_123"
    session_dir = settings.REPORTS_DIR / "runs" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock run_config.json
    config = {
        "model": "gpt-4o",
        "min_eps_growth": 20,
        "prompt_mode": "master_analyst",
        "funnel_stats": {
            "universe_count": 1000,
            "fundamental_passed_count": 50,
            "technical_passed_count": 10,
            "final_watchlist_count": 5
        }
    }
    with open(session_dir / "run_config.json", "w") as f:
        json.dump(config, f)
        
    # Mock prompts_debug.jsonl
    mgtx_res = {
        "ticker": "MGTX",
        "primary_pattern": "Volatility Contraction Pattern (VCP) Breakout Continuation",
        "fundamental_catalyst": "Phase I Gene Therapy Data & Revenue Inflection",
        "suggested_entry_pivot": 10.25,
        "suggested_stop_loss": 8.75,
        "confidence_score": 6,
        "bull_case": "Institutional accumulation post-breakout with accelerating EPS growth (130%+) and massive revenue recognition from partnerships. Analyst consensus upgraded aggressively with avg target 114% above current price.",
        "bear_case_risks": "Pre-profitability biotech with negative Altman-Z (-3.56) and low Piotroski (4) indicating financial distress risk. Deeply negative operating margins (-130%) create dependency on capital markets. VCP shows above-average volatility for the pattern type."
    }
    
    with open(session_dir / "prompts_debug.jsonl", "w") as f:
        f.write(json.dumps({"ticker": "MGTX", "response": mgtx_res}) + "\n")
        
    return session_id

if __name__ == "__main__":
    session_id = create_mock_data()
    print(f"Created mock data for session {session_id}")
    try:
        report_path = generate_pdf_report(session_id)
        print(f"Success! Report generated at: {report_path}")
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
