# main.py
import asyncio
from datetime import datetime
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, FloatPrompt
from rich.table import Table

from tqa.utils.logger import logger
from config.settings import settings
from tqa.data_fetchers.fmp import FMPClient
from tqa.screener.universe import Screener
from tqa.charting.builder import ChartBuilder
from tqa.llm.orchestrator import AnalysisOrchestrator
from tqa.utils.session_logger import init_session

# Initialize Rich Console and Typer
console = Console()
app = typer.Typer(help="Techno-Quantamental Analyzer: AI-Powered Swing Trading Screener.")

def print_banner():
    """Displays a high-contrast terminal banner."""
    banner = """
    ████████  ██████   █████ 
       ██    ██    ██ ██   ██
       ██    ██    ██ ███████
       ██    ██ ▄▄ ██ ██   ██
       ██     ██████  ██   ██
    """
    console.print(Panel(banner, subtitle="AI-Agentic Quantamental Screener", style="bold green", border_style="cyan"))

async def run_pipeline(
    universe_limit: int,
    min_eps_growth: float,
    min_prev_eps: Optional[float] = None,
    min_latest_eps: Optional[float] = None,
    save_prompts: bool = False
):
    """
    The actual orchestration logic.
    """
    # 0. Initialize Session
    session = init_session()
    await session.log_config({
        "universe_limit": universe_limit,
        "min_eps_growth": min_eps_growth,
        "min_prev_eps": min_prev_eps,
        "min_latest_eps": min_latest_eps,
        "save_prompts": save_prompts,
        "model": settings.DEFAULT_MODEL,
        "timestamp": datetime.now().isoformat()
    })
    
    session.log_info(f"Starting scan: Limit={universe_limit}, Min EPS Growth={min_eps_growth}%")
    
    async with FMPClient() as client:
        # 1. Fetch Universe
        with console.status("[bold green]Fetching Universe data from FMP...") as status:
            universe = await client.fetch_universe()
            if not universe:
                console.print("[bold red]Error:[/bold red] Could not fetch universe from FMP.")
                return
            
            # Limit universe for testing if specified
            if universe_limit:
                universe = universe[:universe_limit]
            
            # Ensure all items have a symbol to avoid index misalignment in later stages
            universe = [item for item in universe if 'symbol' in item]
                
            console.print(f"[bold blue]✓[/bold blue] Found {len(universe)} tickers in target market cap range.")
            
            # 2. Staged Filtering (Waterfall: Fundamentals -> Technicals -> Full Data)
            status.update(f"[bold yellow]Phase 1: Checking fundamentals for {len(universe)} tickers...")
            
            # Fetch only income statements for initial screening (processed in chunks of 500)
            income_statements = []
            chunk_size = 500
            for i in range(0, len(universe), chunk_size):
                chunk = universe[i : i + chunk_size]
                is_tasks = [client.fetch_income_statement(item['symbol']) for item in chunk]
                chunk_results = await asyncio.gather(*is_tasks)
                income_statements.extend(chunk_results)
            
            # Apply Fundamental Filter
            screener = Screener(
                min_eps_growth=min_eps_growth,
                min_prev_eps=min_prev_eps,
                min_latest_eps=min_latest_eps
            )
            passed_fund = []
            for i, item in enumerate(universe):
                ticker = item['symbol']
                if screener.check_fundamentals(income_statements[i]):
                    passed_fund.append({
                        "ticker": ticker,
                        "income_statement": income_statements[i]
                    })
            
            console.print(f"[bold blue]✓[/bold blue] {len(passed_fund)} tickers passed fundamental filters.")
            
            if not passed_fund:
                console.print("[bold yellow]No tickers passed the fundamental filters.[/bold yellow]")
                return

            # Phase 2: Technical Filter (Trend Template)
            status.update(f"[bold yellow]Phase 2: Checking Trend Template for {len(passed_fund)} tickers...")
            hist_tasks = [client.fetch_historical_prices(d['ticker']) for d in passed_fund]
            historical_data = await asyncio.gather(*hist_tasks)
            
            passed_tech = []
            for i, d in enumerate(passed_fund):
                d['historical'] = historical_data[i]
                if screener.check_technicals(d['historical']):
                    passed_tech.append(d)
            
            console.print(f"[bold blue]✓[/bold blue] {len(passed_tech)} tickers passed technical filters.")
            
            if not passed_tech:
                console.print("[bold yellow]No tickers passed the technical filters.[/bold yellow]")
                return

            # Phase 3: Fetch Remaining Deep Metrics for survivors
            status.update(f"[bold yellow]Phase 3: Fetching deep metrics for {len(passed_tech)} survivors...")
            
            deep_tasks = []
            for d in passed_tech:
                ticker = d['ticker']
                deep_tasks.append(asyncio.gather(
                    client.fetch_key_metrics(ticker),
                    client.fetch_financial_ratios(ticker),
                    client.fetch_share_float(ticker),
                    client.fetch_stock_price_change(ticker),
                    client.fetch_earnings_surprises(ticker),
                    client.fetch_stock_grades(ticker),
                    client.fetch_historical_stock_grades(ticker),
                    client.fetch_historical_ratings(ticker),
                    client.fetch_financial_scores(ticker),
                    client.fetch_price_target_summary(ticker),
                    client.fetch_stock_news(ticker, limit=settings.MAX_RECENT_ARTICLES)
                ))
            
            deep_results = await asyncio.gather(*deep_tasks)
            
            passed_tickers = []
            for i, d in enumerate(passed_tech):
                res = deep_results[i]
                d.update({
                    "key_metrics": res[0],
                    "ratios": res[1],
                    "share_float": res[2],
                    "stock_price_change": res[3],
                    "earnings_surprises": res[4],
                    "stock_grades": res[5],
                    "historical_grades": res[6],
                    "historical_ratings": res[7],
                    "financial_scores": res[8],
                    "price_target_summary": res[9],
                    "news": res[10]
                })
                passed_tickers.append(d)
            
            console.print(f"[bold blue]✓[/bold blue] Full data fetch complete.")

            # 4. Generate Technical Charts
            status.update(f"[bold cyan]Generating charts for {len(passed_tickers)} tickers...")
            chart_builder = ChartBuilder()
            
            for ticker_data in passed_tickers:
                ticker = ticker_data['ticker']
                historical = ticker_data.get('historical', [])
                if historical:
                    chart_paths = chart_builder.build_all(ticker, historical)
                    ticker_data['chart_paths'] = chart_paths
            
            console.print(f"[bold blue]✓[/bold blue] Chart generation complete.")

            # 5. LLM Analysis via Orchestrator
            status.update(f"[bold magenta]Phase 4: Performing Parallel LLM Analysis for {len(passed_tickers)} tickers...")
            orchestrator = AnalysisOrchestrator()
            # Pass session to orchestrator for prompt logging
            passed_tickers = await orchestrator.analyze_multiple(passed_tickers, session=session if save_prompts else None)

            console.print(f"[bold blue]✓[/bold blue] LLM Analysis complete.")

    # 6. Display Summary Table
    table = Table(title=f"Screener Results ({datetime.now().strftime('%Y-%m-%d')})")
    table.add_column("Ticker", style="cyan")
    table.add_column("Price", justify="right")
    table.add_column("Confidence", justify="center", style="magenta")
    table.add_column("Pattern", justify="left")
    
    for data in passed_tickers:
        ticker = data['ticker']
        latest_price = "N/A"
        if data.get('historical'):
            latest_price = f"${data['historical'][0].get('close', 0):.2f}"
        
        analysis = data.get('analysis')
        conf = "N/A"
        pattern = "N/A"
        if analysis:
            if hasattr(analysis, 'confidence_score'):
                conf = str(analysis.confidence_score)
            if hasattr(analysis, 'primary_pattern'):
                pattern = analysis.primary_pattern

        table.add_row(ticker, latest_price, conf, pattern)
        
    console.print(table)
    console.print(f"\n[bold green]Success![/bold green] Session data saved to [yellow]{session.session_dir}[/yellow]")

@app.command()
def scan(
    universe_limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Max tickers to fetch from FMP."),
    min_eps_growth: Optional[float] = typer.Option(None, "--min-eps-growth-pct", "-e", help="Minimum YoY EPS growth %."),
    min_prev_eps: Optional[float] = typer.Option(None, "--min-prev-eps", help="Minimum absolute EPS for the previous quarter to avoid low-base distortions."),
    min_latest_eps: Optional[float] = typer.Option(None, "--min-latest-eps", help="Minimum absolute EPS for the most recent quarter."),
    save_prompts: bool = typer.Option(False, "--save-prompts", "-s", help="Save all LLM prompts and responses for debugging."),
):
    """Run the end-to-end Quantamental scan."""
    print_banner()

    # Interactive prompts if arguments are missing
    if universe_limit is None:
        universe_limit = IntPrompt.ask("[bold cyan]How many tickers should we pull from the FMP universe?[/bold cyan]", default=50)
    
    if min_eps_growth is None:
        min_eps_growth = FloatPrompt.ask("[bold cyan]Enter minimum EPS growth threshold (%) [/bold cyan]", default=20.0)

    console.print(f"\n[bold green]▶ Launching Pipeline...[/bold green]")
    console.print(f"Settings: [yellow]Model={settings.DEFAULT_MODEL}[/yellow] | [yellow]Date={datetime.now().strftime('%Y-%m-%d')}[/yellow]\n")

    try:
        asyncio.run(run_pipeline(
            universe_limit,
            min_eps_growth,
            min_prev_eps=min_prev_eps,
            min_latest_eps=min_latest_eps,
            save_prompts=save_prompts
        ))
    except KeyboardInterrupt:
        console.print("\n[bold red]Aborted by user.[/bold red]")
    except Exception as e:
        logger.critical(f"Pipeline Failed: {e}", exc_info=True)
        console.print(f"\n[bold red]CRITICAL ERROR:[/bold red] {e}")

@app.command()
def report(session_id: str = typer.Argument(..., help="The session ID to generate a report for.")):
    """Parse a completed session and generate the Markdown summary."""
    console.print(f"[bold green]Generating report for session {session_id}...[/bold green]")
    # TODO: Implement generate_report logic here

if __name__ == "__main__":
    app()
