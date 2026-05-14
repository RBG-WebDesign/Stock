# src/tqa/llm/orchestrator.py
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.settings import settings
from tqa.utils.data_formatter import format_fundamentals_for_llm
from config.schemas import MasterAnalystOutput
from tqa.llm.openrouter import OpenRouterClient
from tqa.utils.logger import logger
from tqa.utils.session_logger import SessionLogger

class AnalysisOrchestrator:
    """
    Orchestrates parallel LLM analysis for multiple tickers.
    """

    def __init__(self, semaphore_limit: int = settings.MAX_CONCURRENT_LLM_REQUESTS):
        self.semaphore = asyncio.Semaphore(semaphore_limit)

    async def analyze_multiple(
        self,
        tickers_data: List[Dict[str, Any]],
        session: Optional[SessionLogger] = None,
        save_prompts: bool = False,
        model: str = settings.DEFAULT_MODEL,
        prompt_mode: str = settings.DEFAULT_PROMPT_KEY,
        summary_max_chars: Optional[int] = None,
        max_articles: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Runs analysis for multiple tickers in parallel with concurrency control.
        """
        logger.info(f"Starting parallel analysis for {len(tickers_data)} tickers using {model}...")
        
        async with OpenRouterClient(model=model) as client:
            tasks = [
                self._process_ticker(
                    client, data, session, save_prompts, 
                    prompt_mode=prompt_mode, 
                    summary_max_chars=summary_max_chars,
                    max_articles=max_articles
                ) for data in tickers_data
            ]
            results = await asyncio.gather(*tasks)
            
        logger.info(f"Parallel analysis complete. Processed {len(results)} tickers.")
        return results

    async def _process_ticker(
        self,
        client: OpenRouterClient,
        ticker_data: Dict[str, Any],
        session: Optional[SessionLogger] = None,
        save_prompts: bool = False,
        prompt_mode: str = settings.DEFAULT_PROMPT_KEY,
        summary_max_chars: Optional[int] = None,
        max_articles: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Processes a single ticker: analysis and saving report.
        """
        ticker = ticker_data.get('ticker', 'UNKNOWN')
        chart_paths = ticker_data.get('chart_paths', {})

        if not chart_paths:
            logger.warning(f"Skipping analysis for {ticker}: No charts found.")
            return ticker_data

        async with self.semaphore:
            try:
                # Format fundamentals to include pre-calculated metrics for better LLM performance
                formatted_fundamentals = format_fundamentals_for_llm(
                    ticker_data,
                    news_summary_max_chars=summary_max_chars,
                    max_recent_articles=max_articles,
                    settings_override=settings
                )
                
                analysis, actual_prompt = await client.analyze_ticker(
                    ticker=ticker,
                    fundamentals=formatted_fundamentals,
                    chart_paths=chart_paths,
                    prompt_key=prompt_mode,
                    session_dir=session.session_dir if session else None
                )

                if analysis:
                    ticker_data['analysis'] = analysis
                    # Save report to session directory if available, otherwise global reports dir
                    report_dir = session.session_dir if session else settings.REPORTS_DIR
                    await self._save_report(ticker, analysis, report_dir)
                    
                    # Log to session if provided
                    if session:
                        await session.log_prompt(
                            ticker,
                            actual_prompt,
                            analysis,
                            client.model,
                            include_prompt=save_prompts,
                            profile=ticker_data.get("profile")
                        )
                else:
                    logger.error(f"Analysis failed for {ticker}")

            except Exception as e:
                logger.error(f"Error during processing of {ticker}: {e}")

        return ticker_data

    async def _save_report(self, ticker: str, analysis: Any, report_dir: Path):
        """
        Saves the analysis result to a JSON file in the specified directory.
        """
        try:
            report_date = datetime.now().strftime('%Y-%m-%d')
            report_path = report_dir / f"{ticker}_{report_date}.json"
            
            # Using a thread pool for file I/O to avoid blocking the event loop
            def save_file():
                report_dir.mkdir(parents=True, exist_ok=True)
                with open(report_path, "w") as f:
                    # Check if analysis is a Pydantic model
                    if hasattr(analysis, "model_dump_json"):
                        f.write(analysis.model_dump_json(indent=2))
                    else:
                        json.dump(analysis, f, indent=2)
            
            await asyncio.to_thread(save_file)
            logger.debug(f"Analysis report saved for {ticker}: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save report for {ticker}: {e}")
