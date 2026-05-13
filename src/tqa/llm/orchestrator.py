# src/tqa/llm/orchestrator.py
import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from config.settings import settings
from tqa.utils.data_formatter import format_fundamentals_for_llm
from config.schemas import MasterAnalystOutput
from tqa.llm.openrouter import OpenRouterClient
from tqa.utils.logger import logger

class AnalysisOrchestrator:
    """
    Orchestrates parallel LLM analysis for multiple tickers.
    """

    def __init__(self, semaphore_limit: int = settings.MAX_CONCURRENT_LLM_REQUESTS):
        self.semaphore = asyncio.Semaphore(semaphore_limit)

    async def analyze_multiple(self, tickers_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Runs analysis for multiple tickers in parallel with concurrency control.
        """
        logger.info(f"Starting parallel analysis for {len(tickers_data)} tickers...")
        
        async with OpenRouterClient() as client:
            tasks = [self._process_ticker(client, data) for data in tickers_data]
            results = await asyncio.gather(*tasks)
            
        logger.info(f"Parallel analysis complete. Processed {len(results)} tickers.")
        return results

    async def _process_ticker(self, client: OpenRouterClient, ticker_data: Dict[str, Any]) -> Dict[str, Any]:
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
                formatted_fundamentals = format_fundamentals_for_llm(ticker_data)
                
                analysis = await client.analyze_ticker(
                    ticker=ticker,
                    fundamentals=formatted_fundamentals,
                    chart_paths=chart_paths,
                    prompt_key=settings.DEFAULT_PROMPT_KEY
                )

                if analysis:
                    ticker_data['analysis'] = analysis
                    await self._save_report(ticker, analysis)
                else:
                    logger.error(f"Analysis failed for {ticker}")

            except Exception as e:
                logger.error(f"Error during processing of {ticker}: {e}")

        return ticker_data

    async def _save_report(self, ticker: str, analysis: Any):
        """
        Saves the analysis result to a JSON file in the reports directory.
        """
        try:
            report_date = datetime.now().strftime('%Y-%m-%d')
            report_path = settings.REPORTS_DIR / f"{ticker}_{report_date}.json"
            
            # Using a thread pool for file I/O to avoid blocking the event loop
            def save_file():
                settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
                with open(report_path, "w") as f:
                    # Check if analysis is a Pydantic model
                    if hasattr(analysis, "model_dump_json"):
                        f.write(analysis.model_dump_json(indent=2))
                    else:
                        json.dump(analysis, f, indent=2)
            
            await asyncio.to_thread(save_file)
            logger.info(f"Analysis report saved for {ticker}: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save report for {ticker}: {e}")
