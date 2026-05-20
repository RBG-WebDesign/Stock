# src/tqa/utils/data_formatter.py
import math
from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd

def format_fundamentals_for_llm(
    ticker_data: Dict[str, Any],
    news_summary_max_chars: Optional[int] = None,
    max_recent_articles: Optional[int] = None,
    settings_override: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Takes raw ticker data and returns a structured dictionary with pre-calculated
    growth metrics to assist the LLM in its analysis.
    """
    # Use provided overrides, then settings_override, then fallback to defaults
    news_max_chars = news_summary_max_chars
    if news_max_chars is None and settings_override:
        news_max_chars = getattr(settings_override, 'NEWS_SUMMARY_MAX_CHARS', 2000)
    
    articles_limit = max_recent_articles
    if articles_limit is None and settings_override:
        articles_limit = getattr(settings_override, 'MAX_RECENT_ARTICLES', 10)

    ticker = ticker_data.get("ticker", "UNKNOWN")
    profile = ticker_data.get("profile", {})
    income_statements = ticker_data.get("income_statement", [])
    key_metrics = ticker_data.get("key_metrics", [])
    ratios = ticker_data.get("ratios", [])
    share_float = ticker_data.get("share_float", {})
    price_change = ticker_data.get("stock_price_change", {})
    surprises = ticker_data.get("earnings_surprises", [])
    estimates = ticker_data.get("analyst_estimates", [])
    news = ticker_data.get("news", [])
    historical = ticker_data.get("historical", [])
    
    # New nodes
    stock_grades = ticker_data.get("stock_grades", [])
    hist_grades = ticker_data.get("historical_grades", [])
    hist_ratings = ticker_data.get("historical_ratings", [])
    fin_scores = ticker_data.get("financial_scores", {})
    target_summary = ticker_data.get("price_target_summary", {})

    # Filter surprises for past dates only and calculate surprise % manually
    today = datetime.now().strftime("%Y-%m-%d")
    processed_surprises = []
    for s in surprises:
        date = s.get("date", "9999-12-31")
        if date > today:
            continue
            
        actual = s.get("epsActual")
        est = s.get("epsEstimated")
        
        # Calculate surprise percentage manually: ((Actual - Estimated) / abs(Estimated)) * 100
        surprise_pct = None
        if actual is not None and est is not None and est != 0:
            surprise_pct = round(((actual - est) / abs(est)) * 100, 2)
            
        processed_surprises.append({
            "date": date,
            "epsActual": actual,
            "epsEstimated": est,
            "revenueActual": format_large_number(s.get("revenueActual")),
            "revenueEstimated": format_large_number(s.get("revenueEstimated")),
            "surprise_pct": surprise_pct
        })
    
    # Calculate technical indicators from historical if available
    technical_stats = _calculate_technical_stats(historical)

    formatted = {
        "ticker": ticker,
        "profile": {
            "name": profile.get("companyName"),
            "industry": profile.get("industry"),
            "sector": profile.get("sector"),
            "description": profile.get("description"),
            "analyst_consensus": profile.get("analyst_consensus"),
            "bulk_rating": profile.get("bulk_rating"),
        },
        "price_performance": {
            "1D_pct": price_change.get("1D"),
            "5D_pct": price_change.get("5D"),
            "1M_pct": price_change.get("1M"),
            "3M_pct": price_change.get("3M"),
            "6M_pct": price_change.get("6M"),
            "1Y_pct": price_change.get("1Y"),
            "ytd_pct": price_change.get("ytd"),
            "52_week_high": technical_stats.get("52_week_high"),
            "52_week_low": technical_stats.get("52_week_low"),
            "current_price": historical[0].get("close") if historical else None,
            "sma_20": technical_stats.get("sma_20"),
            "sma_50": technical_stats.get("sma_50"),
            "sma_100": technical_stats.get("sma_100"),
            "sma_200": technical_stats.get("sma_200"),
        },
        "recent_performance": _calculate_growth_metrics(income_statements),
        "margins_and_returns": _get_latest_ratios(ratios, key_metrics),
        "supply_demand": {
            "float": format_large_number(share_float.get("floatShares")),
            "outstanding": format_large_number(share_float.get("outstandingShares")),
            "free_float_pct": f"{share_float.get('freeFloat', 0):.2f}%" if share_float.get('freeFloat') else None
        },
        "earnings_integrity": {
            "last_4_surprises": processed_surprises[:4],
            "average_surprise_pct": _calculate_avg_surprise(processed_surprises[:4])
        },
        "analyst_sentiment": {
            "latest_grades": [
                {
                    "date": g.get("date"),
                    "company": g.get("gradingCompany"),
                    "newGrade": g.get("newGrade"),
                    "action": g.get("action")
                }
                for g in stock_grades[:3]
            ],
            "rating_trend": hist_grades[0] if hist_grades else {},
            "price_targets": {
                "avg_target": target_summary.get("lastYearAvgPriceTarget"),
                "analyst_count": target_summary.get("lastYearCount")
            }
        },
        "financial_health": {
            "altman_z_score": round(fin_scores.get("altmanZScore", 0), 2) if fin_scores.get("altmanZScore") else None,
            "piotroski_score": fin_scores.get("piotroskiScore"),
            "historical_rating": hist_ratings[0].get("rating") if hist_ratings else None,
            "historical_scores": {
                "roe_score": hist_ratings[0].get("returnOnEquityScore") if hist_ratings else None,
                "dcf_score": hist_ratings[0].get("discountedCashFlowScore") if hist_ratings else None
            }
        },
        "recent_news": [
            {
                "title": n.get("title"), 
                "date": n.get("publishedDate"), 
                "summary": n.get("text")[:news_max_chars] + "..." if n.get("text") else ""
            }
            for n in news[:articles_limit]
        ]
    }
    
    # Add optional premium data if it exists in payload
    if "institutional_positions" in ticker_data:
        inst = ticker_data["institutional_positions"]
        formatted["supply_demand"]["institutional_ownership_percent"] = inst[0].get("ownershipPercent") if inst else None
        formatted["supply_demand"]["institutional_trend"] = "Increasing" if _is_institutional_increasing(inst) else "Decreasing/Flat"
        
    if estimates:
        formatted["future_outlook"] = {
            "next_quarter_eps_est": estimates[0].get("epsAvg"),
            "next_quarter_revenue_est": format_large_number(estimates[0].get("revenueAvg"))
        }
    
    return formatted

def format_currency(val: Any, currency: Optional[str] = "USD") -> str:
    """Formats a number as currency using the correct symbol."""
    if val is None or not isinstance(val, (int, float)):
        return "N/A"
    
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CNY": "¥",
        "CAD": "C$",
        "AUD": "A$",
        "HKD": "HK$",
        "INR": "₹",
        "KRW": "₩"
    }
    
    symbol = symbols.get(currency.upper() if currency else "USD", currency if currency else "$")
    return f"{symbol}{val:,.2f}"

def format_large_number(val: Any) -> Any:
    """Converts large numbers to human readable M/B suffixes."""
    if val is None or not isinstance(val, (int, float)):
        return val
    
    abs_val = abs(val)
    if abs_val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.2f}B"
    elif abs_val >= 1_000_000:
        return f"{val / 1_000_000:.2f}M"
    return val

def _calculate_growth_metrics(income_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not income_statements:
        return {"error": "No income statements available"}
    
    # FMP: Newest to Oldest
    latest = income_statements[0]
    metrics = {}
    
    # Q/Q Growth (compare latest with previous available entry, usually 1 quarter ago)
    if len(income_statements) >= 2:
        prev_q = income_statements[1]
        if latest.get("eps") is not None and prev_q.get("eps") is not None and prev_q["eps"] != 0:
            metrics["eps_growth_qq_pct"] = round(((latest["eps"] - prev_q["eps"]) / abs(prev_q["eps"])) * 100, 2)
        
        if latest.get("revenue") and prev_q.get("revenue") and prev_q["revenue"] != 0:
            metrics["revenue_growth_qq_pct"] = round(((latest["revenue"] - prev_q["revenue"]) / prev_q["revenue"]) * 100, 2)
    
    # Y/Y Growth (specifically look for quarter with same period but previous year)
    latest_period = latest.get("period")
    latest_year = latest.get("fiscalYear")
    
    if latest_period and latest_year:
        year_ago_q = next((s for s in income_statements if s.get("period") == latest_period and s.get("fiscalYear") == latest_year - 1), None)
        
        if year_ago_q:
            if latest.get("eps") is not None and year_ago_q.get("eps") is not None and year_ago_q["eps"] != 0:
                metrics["eps_growth_yy_pct"] = round(((latest["eps"] - year_ago_q["eps"]) / abs(year_ago_q["eps"])) * 100, 2)
            
            if latest.get("revenue") and year_ago_q.get("revenue") and year_ago_q["revenue"] != 0:
                metrics["revenue_growth_yy_pct"] = round(((latest["revenue"] - year_ago_q["revenue"]) / year_ago_q["revenue"]) * 100, 2)
                
    if not metrics:
        return {"error": "Insufficient data for growth calculation"}
            
    return metrics

def _get_latest_ratios(ratios: List[Dict[str, Any]], key_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    res = {}
    if ratios:
        latest = ratios[0]
        # Format as rounded percentages
        if latest.get("grossProfitMargin"):
            res["gross_profit_margin"] = f"{latest['grossProfitMargin'] * 100:.2f}%"
        if latest.get("operatingProfitMargin"):
            res["operating_profit_margin"] = f"{latest['operatingProfitMargin'] * 100:.2f}%"
        if latest.get("netProfitMargin"):
            res["net_profit_margin"] = f"{latest['netProfitMargin'] * 100:.2f}%"
    
    if key_metrics:
        latest_km = key_metrics[0]
        if latest_km.get("roe"):
            res["return_on_equity"] = f"{latest_km['roe'] * 100:.2f}%"
            
    return res

def _calculate_technical_stats(historical: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not historical:
        return {}
    
    df = pd.DataFrame(historical)
    if df.empty or "date" not in df.columns:
        return {}
        
    # Ensure chronological order for rolling calculations
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    
    stats = {}
    if "close" in df.columns:
        last_252 = df.tail(252)
        stats["52_week_high"] = round(last_252["high"].max(), 2) if "high" in last_252.columns else None
        stats["52_week_low"] = round(last_252["low"].min(), 2) if "low" in last_252.columns else None
        
        stats["sma_20"] = round(df["close"].rolling(20).mean().iloc[-1], 2) if len(df) >= 20 else None
        stats["sma_50"] = round(df["close"].rolling(50).mean().iloc[-1], 2) if len(df) >= 50 else None
        stats["sma_100"] = round(df["close"].rolling(100).mean().iloc[-1], 2) if len(df) >= 100 else None
        stats["sma_200"] = round(df["close"].rolling(200).mean().iloc[-1], 2) if len(df) >= 200 else None
        
    return stats

def _is_institutional_increasing(institutional: List[Dict[str, Any]]) -> bool:
    if not isinstance(institutional, list) or len(institutional) < 2:
        return False
    
    current = institutional[0].get("ownershipPercent")
    previous = institutional[1].get("ownershipPercent")
    
    if current is None or previous is None:
        return False
        
    return current > previous

def _calculate_avg_surprise(processed_surprises: List[Dict[str, Any]]) -> float:
    if not processed_surprises:
        return 0.0
    valid_surprises = [s["surprise_pct"] for s in processed_surprises if s.get("surprise_pct") is not None]
    if not valid_surprises:
        return 0.0
    return round(sum(valid_surprises) / len(valid_surprises), 2)
