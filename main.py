# main.py
import asyncio
from datetime import datetime
from typing import List, Optional, Annotated
from pathlib import Path

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
from tqa.utils.config_loader import load_config_file, FullConfig
from tqa.utils.data_formatter import format_currency

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
        "   [bold cyan]████████╗ ██████╗    █████╗ [/bold cyan]\n"
        "   [bold cyan]   ██╔══╝██╔═══██╗  ██╔══██╗[/bold cyan]\n"
        "   [bold cyan]   ██║   ██║   ██║  ███████║[/bold cyan]\n"
        "   [bold cyan]   ██║   ██║▄▄ ██║  ██╔══██║[/bold cyan]\n"
        "   [bold cyan]   ██║     ╚████╔╝  ██║  ██║[/bold cyan]\n"
        "   [dim cyan]    ╚═╝      ╚═▀═╝   ╚═╝  ╚═╝[/dim cyan]\n"
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
    min_rev_growth: float = 20.0,
    max_rev_growth: Optional[float] = None,
    min_prev_eps: Optional[float] = None,
    max_prev_eps: Optional[float] = None,
    min_latest_eps: Optional[float] = None,
    min_market_cap: Optional[int] = None,
    max_market_cap: Optional[int] = None,
    news_summary_max_chars: int = settings.NEWS_SUMMARY_MAX_CHARS,
    max_recent_articles: int = settings.MAX_RECENT_ARTICLES,
    save_prompts: bool = False,
    exchanges: Optional[str] = settings.DEFAULT_EXCHANGES,
    prompt_mode: str = "master_analyst",
    model: str = settings.DEFAULT_MODEL,
    technical_filters: Optional[List[str]] = None
):
    """
    The actual orchestration logic.
    """
    # 0. Initialize Session
    session = init_session()
    await session.log_config({
        "universe_limit": universe_limit,
        "min_eps_growth": min_eps_growth,
        "min_rev_growth": min_rev_growth,
        "max_rev_growth": max_rev_growth,
        "min_prev_eps": min_prev_eps,
        "max_prev_eps": max_prev_eps,
        "min_latest_eps": min_latest_eps,
        "min_market_cap": min_market_cap,
        "max_market_cap": max_market_cap,
        "news_summary_max_chars": news_summary_max_chars,
        "max_recent_articles": max_recent_articles,
        "save_prompts": save_prompts,
        "exchanges": exchanges,
        "model": model,
        "prompt_mode": prompt_mode,
        "technical_filters": technical_filters,
        "timestamp": datetime.now().isoformat()
    })
    
    session.log_info(f"Starting scan: Limit={universe_limit}, Min EPS Growth={min_eps_growth}%")
    
    async with FMPClient() as client:
        # 1. Fetch Universe
        with console.status("[bold green]Fetching Universe data from FMP...") as status:
            # Use provided market cap or fallback to defaults in client
            fetch_kwargs = {
                "min_market_cap": min_market_cap if min_market_cap is not None else settings.DEFAULT_MIN_MARKET_CAP,
                "max_market_cap": max_market_cap if max_market_cap is not None else settings.DEFAULT_MAX_MARKET_CAP,
                "exchanges": exchanges
            }
                
            universe = await client.fetch_universe(**fetch_kwargs)
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
                    quarter_data = await client.fetch_income_statement_bulk(year, q, use_csv=True, exchanges=exchanges)
                    if quarter_data:
                        for statement in quarter_data:
                            symbol = statement.get('symbol')
                            if symbol and isinstance(symbol, str):
                                symbol = symbol.upper()
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
                min_rev_growth=min_rev_growth,
                max_rev_growth=max_rev_growth,
                min_prev_eps=min_prev_eps,
                max_prev_eps=max_prev_eps,
                min_latest_eps=min_latest_eps,
                technical_filters=technical_filters
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
            
            # Pre-fetch bulk data if premium to avoid thousands of individual calls
            bulk_profiles = {}
            bulk_ratings = {}
            bulk_scores = {}
            bulk_targets = {}
            bulk_consensus = {}
            
            if settings.FMP_PLAN == "premium":
                p3_bulk_task = progress.add_task("[yellow]Phase 3: Bulk Data Pre-fetch...", total=5)
                
                # Fetch bulk data concurrently
                profiles_res, ratings_res, scores_res, targets_res, consensus_res = await asyncio.gather(
                    client.fetch_profile_bulk(use_csv=True, exchanges=exchanges),
                    client.fetch_rating_bulk(use_csv=True, exchanges=exchanges),
                    client.fetch_scores_bulk(use_csv=True, exchanges=exchanges),
                    client.fetch_price_target_summary_bulk(use_csv=True, exchanges=exchanges),
                    client.fetch_upgrades_downgrades_consensus_bulk(use_csv=True, exchanges=exchanges)
                )
                
                # Build lookup maps
                def build_map(data):
                    m = {}
                    for item in (data or []):
                        sym = item.get('symbol')
                        if sym and isinstance(sym, str):
                            m[sym.upper()] = item
                    return m

                bulk_profiles = build_map(profiles_res)
                bulk_ratings = build_map(ratings_res)
                bulk_scores = build_map(scores_res)
                bulk_targets = build_map(targets_res)
                bulk_consensus = build_map(consensus_res)
                
                progress.advance(p3_bulk_task, 5)
                progress.remove_task(p3_bulk_task)

            async def fetch_deep(d, task_id):
                ticker = d['ticker'].upper()
                
                # Use bulk data if available, otherwise fallback to individual fetch
                # Note: Some metrics still need individual fetch as they are specific/historical
                tasks = {
                    "key_metrics": client.fetch_key_metrics(ticker),
                    "ratios": client.fetch_financial_ratios(ticker),
                    "share_float": client.fetch_share_float(ticker),
                    "stock_price_change": client.fetch_stock_price_change(ticker),
                    "earnings_surprises": client.fetch_earnings_surprises(ticker),
                    "stock_grades": client.fetch_stock_grades(ticker),
                    "historical_grades": client.fetch_historical_stock_grades(ticker),
                    "historical_ratings": client.fetch_historical_ratings(ticker),
                    "news": client.fetch_stock_news(ticker, limit=max_recent_articles)
                }
                
                # Conditional fetching for things we might have in bulk
                if ticker not in bulk_scores:
                    tasks["financial_scores"] = client.fetch_financial_scores(ticker)
                if ticker not in bulk_targets:
                    tasks["price_target_summary"] = client.fetch_price_target_summary(ticker)
                if ticker not in bulk_profiles:
                    tasks["profile"] = client.fetch_company_profile(ticker)
                
                keys = list(tasks.keys())
                res_values = await asyncio.gather(*tasks.values())
                res = dict(zip(keys, res_values))
                
                # Merge bulk data
                profile = (res.get("profile") or bulk_profiles.get(ticker) or {}).copy()
                scores = res.get("financial_scores") or bulk_scores.get(ticker) or {}
                targets = res.get("price_target_summary") or bulk_targets.get(ticker) or {}

                # Add consensus if available
                if ticker in bulk_consensus:
                    profile["analyst_consensus"] = bulk_consensus[ticker]

                # Add rating if available
                if ticker in bulk_ratings:
                    profile["bulk_rating"] = bulk_ratings[ticker]

                # Extract most recent revenue and earnings from income statement for report builder
                if d.get('income_statement'):
                    latest_is = d['income_statement'][0]
                    profile['recent_revenue'] = latest_is.get('revenue')
                    profile['recent_earnings'] = latest_is.get('netIncome')

                d.update({
                    "key_metrics": res.get("key_metrics"),
                    "ratios": res.get("ratios"),
                    "share_float": res.get("share_float"),
                    "stock_price_change": res.get("stock_price_change"),
                    "earnings_surprises": res.get("earnings_surprises"),
                    "stock_grades": res.get("stock_grades"),
                    "historical_grades": res.get("historical_grades"),
                    "historical_ratings": res.get("historical_ratings"),
                    "financial_scores": scores,
                    "price_target_summary": targets,
                    "news": res.get("news"),
                    "profile": profile
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
                prompt_mode=prompt_mode,
                summary_max_chars=news_summary_max_chars,
                max_articles=max_recent_articles
            )
            progress.remove_task(p4_task)
            session.update_funnel_stats(final_watchlist_count=len(passed_tickers))

    # Re-log config to persist final funnel stats
    await session.log_config({
        "universe_limit": universe_limit,
        "min_eps_growth": min_eps_growth,
        "min_rev_growth": min_rev_growth,
        "max_rev_growth": max_rev_growth,
        "min_prev_eps": min_prev_eps,
        "max_prev_eps": max_prev_eps,
        "min_latest_eps": min_latest_eps,
        "min_market_cap": min_market_cap,
        "max_market_cap": max_market_cap,
        "news_summary_max_chars": news_summary_max_chars,
        "max_recent_articles": max_recent_articles,
        "save_prompts": save_prompts,
        "model": model,
        "prompt_mode": prompt_mode,
        "technical_filters": technical_filters,
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
            currency = data.get('profile', {}).get('currency', 'USD')
            latest_price = format_currency(data['historical'][0].get('close', 0), currency)
        
        analysis = data.get('analysis')
        conf = "N/A"
        pattern = "N/A"
        if analysis:
            # Extract confidence score from any schema
            if hasattr(analysis, 'confidence_score'):
                conf = str(analysis.confidence_score)
            elif isinstance(analysis, dict):
                conf = str(analysis.get('confidence_score', 'N/A'))
            
            # Polymorphic pattern extraction
            pattern_attr_priority = [
                'primary_pattern',
                'base_classification',
                's_supply_demand',
                'institutional_trend_analysis'
            ]
            for attr in pattern_attr_priority:
                val = None
                if hasattr(analysis, attr):
                    val = getattr(analysis, attr)
                elif isinstance(analysis, dict):
                    val = analysis.get(attr)
                
                if val:
                    # Truncate long descriptions for the table
                    pattern = (val[:37] + "...") if len(val) > 40 else val
                    break

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
    min_rev_growth: Annotated[Optional[float], typer.Option("--min-rev-growth-pct", help="Minimum YoY Revenue growth %.")] = None,
    max_rev_growth: Annotated[Optional[float], typer.Option("--max-rev-growth-pct", help="Maximum YoY Revenue growth %.")] = None,
    min_prev_eps: Annotated[Optional[float], typer.Option("--min-prev-eps", help="Minimum absolute EPS for the previous quarter.")] = None,
    max_prev_eps: Annotated[Optional[float], typer.Option("--max-prev-eps", help="Maximum absolute EPS for the previous quarter.")] = None,
    min_latest_eps: Annotated[Optional[float], typer.Option("--min-latest-eps", help="Minimum absolute EPS for the most recent quarter.")] = None,
    min_market_cap_m: Annotated[Optional[float], typer.Option("--min-market-cap", help="Minimum market capitalization in Millions (e.g., 100 for $100M).")] = None,
    max_market_cap_m: Annotated[Optional[float], typer.Option("--max-market-cap", help="Maximum market capitalization in Millions (e.g., 1000 for $1B).")] = None,
    news_summary_max_chars: Annotated[Optional[int], typer.Option("--news-summary-max-chars", help="Maximum characters for news article summaries.")] = None,
    max_recent_articles: Annotated[Optional[int], typer.Option("--max-recent-articles", help="Number of recent news articles to include in LLM payload.")] = None,
    save_prompts: Annotated[bool, typer.Option("--save-prompts", "-s", help="Save all LLM prompts and responses for debugging.")] = False,
    exchanges: Annotated[Optional[str], typer.Option("--exchanges", "-X", help="Comma-separated list of stock exchanges to screen.")] = None,
    prompt_mode: Annotated[Optional[str], typer.Option("--prompt-mode", "-p", help="Prompt mode to use for analysis.")] = None,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="LLM model to use.")] = None,
    config_path: Annotated[Optional[Path], typer.Option("--config", "-c", help="Path to a JSON configuration file.")] = None
):
    """Run the end-to-end Quantamental scan."""
    # 1. Load config if provided
    config = FullConfig()
    if config_path:
        try:
            config = load_config_file(config_path)
            console.print(f"[bold green]✓[/bold green] Loaded configuration from [yellow]{config_path}[/yellow]")
        except Exception as e:
            console.print(f"[bold red]Error loading config:[/bold red] {e}")
            raise typer.Exit(1)


    # 2. Resolve Values with Priority: CLI -> Config -> Prompts/Defaults
    
    # Interactivity control: Skip prompts if config is provided or any explicit CLI args are provided
    cli_args_provided = any([
        universe_limit is not None,
        min_eps_growth is not None,
        min_rev_growth is not None,
        max_rev_growth is not None,
        min_prev_eps is not None,
        max_prev_eps is not None,
        min_latest_eps is not None,
        min_market_cap_m is not None,
        max_market_cap_m is not None,
        news_summary_max_chars is not None,
        max_recent_articles is not None,
        prompt_mode is not None,
        model is not None,
        exchanges is not None,
        save_prompts is True # Since default is False
    ])
    skip_prompts = config_path is not None or cli_args_provided

    # --- Pipeline Settings ---
    if universe_limit is None:
        universe_limit = config.pipeline.universe_limit
        if universe_limit is None and not skip_prompts:
            universe_limit = IntPrompt.ask("[bold cyan]How many tickers should we pull from the FMP universe?[/bold cyan]", default=50)
        elif universe_limit is None:
            universe_limit = 50

    if model is None:
        model = config.pipeline.model or settings.DEFAULT_MODEL
    
    if exchanges is None:
        # If not provided via CLI, use config (which defaults to settings.DEFAULT_EXCHANGES)
        exchanges = config.pipeline.exchanges

    if prompt_mode is None:
        prompt_mode = config.pipeline.prompt_mode or settings.DEFAULT_PROMPT_KEY

    if news_summary_max_chars is None:
        news_summary_max_chars = config.pipeline.news_summary_max_chars or settings.NEWS_SUMMARY_MAX_CHARS
    
    if max_recent_articles is None:
        max_recent_articles = config.pipeline.max_recent_articles or settings.MAX_RECENT_ARTICLES

    # Save Prompts: CLI flag takes precedence if True, otherwise check config
    if not save_prompts:
        save_prompts = config.pipeline.save_prompts

    # --- Fundamental & Market Cap Filters ---
    if min_eps_growth is None:
        min_eps_growth = config.fundamental_filters.min_eps_growth
        if min_eps_growth is None and not skip_prompts:
            min_eps_growth = FloatPrompt.ask("[bold cyan]Enter minimum EPS growth threshold (%) [/bold cyan]", default=settings.DEFAULT_MIN_EPS_GROWTH)
        elif min_eps_growth is None:
            min_eps_growth = settings.DEFAULT_MIN_EPS_GROWTH

    if min_rev_growth is None:
        min_rev_growth = config.fundamental_filters.min_rev_growth

    if max_rev_growth is None:
        max_rev_growth = config.fundamental_filters.max_rev_growth

    if min_prev_eps is None:
        min_prev_eps = config.fundamental_filters.min_prev_eps

    if max_prev_eps is None:
        max_prev_eps = config.fundamental_filters.max_prev_eps

    if min_latest_eps is None:
        min_latest_eps = config.fundamental_filters.min_latest_eps

    if min_market_cap_m is None:
        min_market_cap_m = config.market_cap.min_m

    if max_market_cap_m is None:
        max_market_cap_m = config.market_cap.max_m

    # 3. Interactive Advanced Mode (only if no config and not fully automated)
    # --- Technical Filters ---
    technical_filters = config.technical_filters

    if not skip_prompts:
        advanced = questionary.confirm("Enter advanced settings mode?", default=False).ask()
        if advanced:
            model = questionary.select("Select LLM Model", choices=settings.MODEL_LIST, default=model).ask()
            prompt_mode = questionary.select(
                "Select Prompt Mode",
                choices=["master_analyst", "institutional_accumulator", "can_slim_growth", "price_action_entry"],
                default=prompt_mode
            ).ask()
            save_prompts = questionary.confirm("Save raw prompts for debug?", default=save_prompts).ask()

            # News & Summary Settings
            console.print("\n[bold yellow]LLM Context Settings[/bold yellow]")
            news_summary_max_chars = IntPrompt.ask("News summary max characters", default=news_summary_max_chars)
            max_recent_articles = IntPrompt.ask("Max news articles to fetch", default=max_recent_articles)

            # New Fundamental & Market Cap Filters
            console.print("\n[bold yellow]Advanced Fundamental Filters[/bold yellow]")
            min_rev_growth = FloatPrompt.ask("Minimum YoY Revenue growth %", default=min_rev_growth)
            max_rev_growth_val = FloatPrompt.ask("Maximum YoY Revenue growth % (0 for None)", default=max_rev_growth or 0.0)
            max_rev_growth = float(max_rev_growth_val) if max_rev_growth_val != 0 else None

            max_prev_eps_val = FloatPrompt.ask("Maximum Prev Quarter EPS (e.g. 0 for turn profitable, 999 for None)", default=max_prev_eps or 999.0)
            max_prev_eps = float(max_prev_eps_val) if max_prev_eps_val != 999.0 else None

            console.print("\n[bold yellow]Universe Scale Filters[/bold yellow]")
            min_market_cap_m = FloatPrompt.ask("Minimum Market Cap ($ Millions)", default=min_market_cap_m)
            max_market_cap_m = FloatPrompt.ask("Maximum Market Cap ($ Millions)", default=max_market_cap_m)

    console.print(f"\n[bold green]▶ Launching Pipeline...[/bold green]")
    console.print(f"Settings: [yellow]Model={model}[/yellow] | [yellow]Prompt Mode={prompt_mode}[/yellow] | [yellow]Date={datetime.now().strftime('%Y-%m-%d')}[/yellow]\n")

    try:
        # Convert market cap from Millions to absolute dollars
        min_market_cap = int(min_market_cap_m * 1_000_000) if min_market_cap_m is not None else None
        max_market_cap = int(max_market_cap_m * 1_000_000) if max_market_cap_m is not None else None
        
        session_id = asyncio.run(run_pipeline(
            universe_limit,
            min_eps_growth,
            min_rev_growth=min_rev_growth,
            max_rev_growth=max_rev_growth,
            min_prev_eps=min_prev_eps,
            max_prev_eps=max_prev_eps,
            min_latest_eps=min_latest_eps,
            min_market_cap=min_market_cap,
            max_market_cap=max_market_cap,
            news_summary_max_chars=news_summary_max_chars,
            max_recent_articles=max_recent_articles,
            save_prompts=save_prompts,
            exchanges=exchanges,
            prompt_mode=prompt_mode,
            model=model,
            technical_filters=technical_filters
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
