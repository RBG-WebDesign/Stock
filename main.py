# main.py
import asyncio
from datetime import datetime
from typing import List, Optional, Annotated

import typer
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, FloatPrompt, Prompt
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.status import Status

from tqa.utils.logger import logger
from config.settings import settings
from tqa.data_fetchers.fmp import FMPClient
from tqa.screener.universe import Screener
from tqa.charting.builder import ChartBuilder
from tqa.llm.orchestrator import AnalysisOrchestrator
from tqa.utils.session_logger import init_session
from tqa.utils.report_builder import generate_pdf_report

# Initialize Rich Console and Typer
console = Console()

# Update logger to use this console for synchronized output with progress bars
from tqa.utils.logger import setup_logger
setup_logger(console=console)

# Use a global progress instance to ensure tasks are managed in a single screen area
progress = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
    console=console,
    transient=True # This clears the progress bars after completion
)
app = typer.Typer(
    help="Techno-Quantamental Analyzer: AI-Powered Swing Trading Screener.",
    add_completion=False
)

def print_banner():
    art = (
        "   [bold cyan]████████╗ ██████╗  █████╗ [/bold cyan]\n"
        "   [bold cyan]   ██╔══╝██╔═══██╗██╔══██╗[/bold cyan]\n"
        "   [bold cyan]   ██║   ██║   ██║███████║[/bold cyan]\n"
        "   [bold cyan]   ██║   ██║▄▄ ██║██╔══██║[/bold cyan]\n"
        "   [bold cyan]   ██║    ╚██████╔╝██║  ██║[/bold cyan]\n"
        "   [dim cyan]   ╚═╝     ╚══▀▀═╝ ╚═╝  ╚═╝[/dim cyan]\n"
    )
    meta = (
        "   [bold white]TECHNO-QUANTAMENTAL ANALYZER[/bold white]     [dim cyan]v0.1[/dim cyan]\n"
        "   [dim]──────────────────────────────────────[/dim]\n"
        "   [dim]Provider:[/dim] [white]FMP[/white]  "
        "[dim]│[/dim]  [dim]Engine:[/dim] [white]Anthropic / OpenRouter[/white]  "
        "[dim]│[/dim]  [dim]Strategy:[/dim] [white]CAN SLIM · Minervini[/white]"
    )
    console.print(Panel(
        art + meta,
        subtitle="[dim italic]EOD Swing Trading Screener[/dim italic]",
        border_style="cyan",
        padding=(1, 2)
    ))
    
async def run_pipeline(
    universe_limit: int,
    min_eps_growth: float,
    min_prev_eps: Optional[float] = None,
    min_latest_eps: Optional[float] = None,
    save_prompts: bool = False,
    prompt_mode: str = "master_analyst",
    model: str = settings.DEFAULT_MODEL
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
        "model": model,
        "prompt_mode": prompt_mode,
        "timestamp": datetime.now().isoformat()
    })
    
    session.log_info(f"Starting scan: Limit={universe_limit}, Min EPS Growth={min_eps_growth}%")
    
    async with FMPClient() as client:
        # 1. Fetch Universe
        with console.status("[bold green]Fetching Universe data from FMP...") as status:
            universe = await client.fetch_universe()
            if not universe:
                console.print("[bold red]Error:[/bold red] Could not fetch universe from FMP.")
                return None
            
            # Limit universe for testing if specified
            if universe_limit:
                universe = universe[:universe_limit]
            
            # Ensure all items have a symbol to avoid index misalignment in later stages
            universe = [item for item in universe if 'symbol' in item]
            
            session.update_funnel_stats(universe_count=len(universe))
            console.print(f"[bold blue]✓[/bold blue] Found {len(universe)} tickers in target market cap range.")

        # Staged Filtering & Processing
        with progress:
            # 2. Phase 1: Fundamental Filtering
            ticker_statements = {}
            if settings.FMP_PLAN == "premium":
                # Bulk fetching logic (Premium only)
                p1_bulk_task = progress.add_task("[yellow]Phase 1: Bulk Fundamental Fetch...", total=4)
                
                def get_recent_quarters(n=4):
                    now = datetime.now()
                    results = []
                    curr_year = now.year
                    curr_q = (now.month - 1) // 3 + 1
                    for _ in range(n):
                        curr_q -= 1
                        if curr_q <= 0:
                            curr_q = 4
                            curr_year -= 1
                        results.append((curr_year, f"Q{curr_q}"))
                    return results

                quarters = get_recent_quarters(4)
                for year, q in quarters:
                    quarter_data = await client.fetch_income_statement_bulk(year, q)
                    if quarter_data:
                        for statement in quarter_data:
                            symbol = statement.get('symbol', '').upper()
                            if symbol:
                                if symbol not in ticker_statements:
                                    ticker_statements[symbol] = []
                                ticker_statements[symbol].append(statement)
                    progress.advance(p1_bulk_task)
                
                # Sort statements by date
                for symbol in ticker_statements:
                    ticker_statements[symbol].sort(key=lambda x: x.get('date', ''), reverse=True)

            # Apply Fundamental Filter loop
            p1_task = progress.add_task("[yellow]Phase 1: Fundamental Screening...", total=len(universe))
            screener = Screener(
                min_eps_growth=min_eps_growth,
                min_prev_eps=min_prev_eps,
                min_latest_eps=min_latest_eps
            )
            passed_fund = []
            
            for item in universe:
                ticker = item['symbol'].upper()
                statements = ticker_statements.get(ticker, [])
                
                # If bulk data missing for this ticker, fallback to individual fetch
                if not statements:
                    statements = await client.fetch_income_statement(ticker)
                
                if len(statements) >= 2:
                    if screener.check_fundamentals(statements):
                        passed_fund.append({
                            "ticker": ticker,
                            "income_statement": statements
                        })
                progress.advance(p1_task)
            
            progress.remove_task(p1_task)
            if 'p1_bulk_task' in locals():
                progress.remove_task(p1_bulk_task)

            session.update_funnel_stats(fundamental_passed_count=len(passed_fund))
            if not passed_fund:
                console.print("[bold yellow]No tickers passed the fundamental filters.[/bold yellow]")
                return session.session_id

            # 3. Phase 2: Technical Filtering
            p2_task = progress.add_task("[yellow]Phase 2: Technical Data & Filtering...", total=len(passed_fund))
            chart_builder = ChartBuilder()
            
            async def process_tech(data, task_id):
                ticker = data['ticker']
                # Check for existing charts first
                existing_charts = chart_builder.check_existing_charts(ticker)
                if existing_charts:
                    data['chart_paths'] = existing_charts
                
                # Fetch historical data
                historical = await client.fetch_historical_prices(ticker)
                data['historical'] = historical
                
                passed = False
                if data.get('chart_paths'):
                    passed = True # Assume technicals passed if charts exist from today
                elif screener.check_technicals(historical):
                    passed = True
                
                progress.advance(task_id)
                return data if passed else None

            tech_tasks = [process_tech(d, p2_task) for d in passed_fund]
            tech_results = await asyncio.gather(*tech_tasks)
            passed_tech = [r for r in tech_results if r is not None]
            
            progress.remove_task(p2_task)

            session.update_funnel_stats(technical_passed_count=len(passed_tech))
            if not passed_tech:
                console.print("[bold yellow]No tickers passed the technical filters.[/bold yellow]")
                return session.session_id

            # 4. Phase 3: Deep Metrics Fetch
            p3_task = progress.add_task("[yellow]Phase 3: Deep Metrics Fetch...", total=len(passed_tech))
            
            async def fetch_deep(d, task_id):
                ticker = d['ticker']
                res = await asyncio.gather(
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
                )
                d.update({
                    "key_metrics": res[0], "ratios": res[1], "share_float": res[2],
                    "stock_price_change": res[3], "earnings_surprises": res[4],
                    "stock_grades": res[5], "historical_grades": res[6],
                    "historical_ratings": res[7], "financial_scores": res[8],
                    "price_target_summary": res[9], "news": res[10]
                })
                progress.advance(task_id)
                return d

            deep_tasks = [fetch_deep(d, p3_task) for d in passed_tech]
            passed_tickers = await asyncio.gather(*deep_tasks)
            
            progress.remove_task(p3_task)

            # 5. Chart Generation
            p_chart_task = progress.add_task("[cyan]Generating Charts...", total=len(passed_tickers))
            for ticker_data in passed_tickers:
                if not ticker_data.get('chart_paths'):
                    ticker = ticker_data['ticker']
                    historical = ticker_data.get('historical', [])
                    if historical:
                        ticker_data['chart_paths'] = chart_builder.build_all(ticker, historical)
                progress.advance(p_chart_task)
            
            progress.remove_task(p_chart_task)

            # 6. LLM Analysis
            p4_task = progress.add_task("[magenta]Phase 4: LLM Analysis...", total=len(passed_tickers))
            orchestrator = AnalysisOrchestrator()
            
            # We wrap the orchestrator's _process_ticker to advance our progress bar
            # Or just let it run. For better UI, we'll wrap it.
            original_process = orchestrator._process_ticker
            async def wrapped_process(*args, **kwargs):
                res = await original_process(*args, **kwargs)
                progress.advance(p4_task)
                return res
            
            orchestrator._process_ticker = wrapped_process
            
            # Use the already passed_tickers from phase 3/charting
            passed_tickers = await orchestrator.analyze_multiple(
                passed_tickers, 
                session=session, 
                save_prompts=save_prompts,
                model=model,
                prompt_mode=prompt_mode
            )
            progress.remove_task(p4_task)
            session.update_funnel_stats(final_watchlist_count=len(passed_tickers))

    # Re-log config to persist final funnel stats
    await session.log_config({
        "universe_limit": universe_limit,
        "min_eps_growth": min_eps_growth,
        "min_prev_eps": min_prev_eps,
        "min_latest_eps": min_latest_eps,
        "save_prompts": save_prompts,
        "model": model,
        "prompt_mode": prompt_mode,
        "timestamp": datetime.now().isoformat()
    })

    # 7. Display Summary Table
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
            elif isinstance(analysis, dict):
                conf = str(analysis.get('confidence_score', 'N/A'))
            
            if hasattr(analysis, 'primary_pattern'):
                pattern = analysis.primary_pattern
            elif isinstance(analysis, dict):
                pattern = analysis.get('primary_pattern', 'N/A')

        table.add_row(ticker, latest_price, conf, pattern)
        
    console.print(table)
    console.print(f"\n[bold green]Success![/bold green] Session data saved to [yellow]{session.session_dir}[/yellow]")
    return session.session_id

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Techno-Quantamental Analyzer: AI-Powered Swing Trading Screener.
    """
    print_banner()
    if ctx.invoked_subcommand is None:
        choice = questionary.select(
            "What would you like to do?",
            choices=["scan", "report", "exit"],
            default="scan"
        ).ask()
        
        if choice == "scan":
            ctx.invoke(scan)
        elif choice == "report":
            ctx.invoke(report)
        else:
            raise typer.Exit()

@app.command()
def scan(
    universe_limit: Annotated[Optional[int], typer.Option("--limit", "-l", help="Max tickers to fetch from FMP.")] = None,
    min_eps_growth: Annotated[Optional[float], typer.Option("--min-eps-growth-pct", "-e", help="Minimum YoY EPS growth %.")] = None,
    min_prev_eps: Annotated[Optional[float], typer.Option("--min-prev-eps", help="Minimum absolute EPS for the previous quarter to avoid low-base distortions.")] = None,
    min_latest_eps: Annotated[Optional[float], typer.Option("--min-latest-eps", help="Minimum absolute EPS for the most recent quarter.")] = None,
    save_prompts: Annotated[bool, typer.Option("--save-prompts", "-s", help="Save all LLM prompts and responses for debugging.")] = False,
    prompt_mode: Annotated[str, typer.Option("--prompt-mode", "-p", help="Prompt mode to use for analysis.")] = settings.DEFAULT_PROMPT_KEY,
    model: Annotated[str, typer.Option("--model", "-m", help="LLM model to use.")] = settings.DEFAULT_MODEL
):
    """Run the end-to-end Quantamental scan."""
    # Interactive prompts if arguments are missing
    if universe_limit is None:
        universe_limit = IntPrompt.ask("[bold cyan]How many tickers should we pull from the FMP universe?[/bold cyan]", default=50)
    
    if min_eps_growth is None:
        min_eps_growth = FloatPrompt.ask("[bold cyan]Enter minimum EPS growth threshold (%) [/bold cyan]", default=20.0)

    # Advanced Mode toggle
    advanced = questionary.confirm("Enter advanced settings mode?", default=False).ask()
    if advanced:
        model = questionary.select(
            "Select LLM Model",
            choices=settings.MODEL_LIST,
            default=model
        ).ask()
        
        prompt_mode = questionary.select(
            "Select Prompt Mode",
            choices=["master_analyst", "institutional_accumulator", "can_slim_growth", "price_action_entry"],
            default=prompt_mode
        ).ask()
        
        save_prompts = questionary.confirm("Save raw prompts for debug?", default=save_prompts).ask()

    console.print(f"\n[bold green]▶ Launching Pipeline...[/bold green]")
    console.print(f"Settings: [yellow]Model={model}[/yellow] | [yellow]Prompt Mode={prompt_mode}[/yellow] | [yellow]Date={datetime.now().strftime('%Y-%m-%d')}[/yellow]\n")

    try:
        session_id = asyncio.run(run_pipeline(
            universe_limit,
            min_eps_growth,
            min_prev_eps=min_prev_eps,
            min_latest_eps=min_latest_eps,
            save_prompts=save_prompts,
            prompt_mode=prompt_mode,
            model=model
        ))

        if session_id:
            console.print(f"\n[bold green]Scan complete. Triggering automatic report generation...[/bold green]")
            report(session_id=session_id, interactive=False)

    except KeyboardInterrupt:
        console.print("\n[bold red]Aborted by user.[/bold red]")
    except Exception as e:
        logger.critical(f"Pipeline Failed: {e}", exc_info=True)
        console.print(f"\n[bold red]CRITICAL ERROR:[/bold red] {e}")

@app.command()
def report(
    session_id: Annotated[Optional[str], typer.Argument(help="The session ID to generate a report for.")] = None,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="The LLM model used for the session.")] = None,
    min_confidence: Annotated[float, typer.Option("--min-confidence", "-c", help="Minimum confidence score for inclusive in the report.")] = 0.0,
    interactive: Annotated[bool, typer.Option("--interactive/--no-interactive", help="Enable/disable interactive mode.")] = True
):
    """Parse a completed session and generate the PDF summary."""
    if interactive and not session_id:
        runs_dir = settings.REPORTS_DIR / "runs"
        if not runs_dir.exists():
            console.print("[bold red]Error:[/bold red] No sessions found.")
            return
        
        sessions = sorted([d.name for d in runs_dir.iterdir() if d.is_dir()], reverse=True)[:5]
        if not sessions:
            console.print("[bold red]Error:[/bold red] No sessions found.")
            return

        console.print("\n[bold cyan]Recent Sessions:[/bold cyan]")
        for i, s in enumerate(sessions):
            console.print(f"[{i}] {s}")
        
        idx = IntPrompt.ask("Select session index", default=0)
        if 0 <= idx < len(sessions):
            session_id = sessions[idx]
        else:
            console.print("[bold red]Invalid selection.[/bold red]")
            return

    if not session_id:
        console.print("[bold red]Error:[/bold red] Session ID is required.")
        return

    console.print(f"[bold green]Generating report for session {session_id}...[/bold green]")
    try:
        report_path = generate_pdf_report(session_id, min_confidence=min_confidence)
        console.print(f"[bold blue]✓[/bold blue] Report generated: [yellow]{report_path}[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Failed to generate report:[/bold red] {e}")
        logger.error(f"Report generation failed: {e}", exc_info=True)

if __name__ == "__main__":
    app()
