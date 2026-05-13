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

async def run_pipeline(universe_limit: int, min_eps: float):
    """
    The actual orchestration logic.
    """
    logger.info(f"Starting scan: Limit={universe_limit}, Min EPS={min_eps}%")
    
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
                
            console.print(f"[bold blue]✓[/bold blue] Found {len(universe)} tickers in target market cap range.")
            
            # 2. Staged Filtering (Efficiency: Fundamentals -> Technicals -> Full Data)
            status.update(f"[bold yellow]Phase 1: Checking EPS growth for {len(universe)} tickers...")
            
            # Fetch only income statements for initial screening
            is_tasks = [client.fetch_income_statement(item['symbol']) for item in universe if 'symbol' in item]
            income_statements = await asyncio.gather(*is_tasks)
            
            # Match income statements back to tickers
            initial_data = []
            for i, item in enumerate(universe):
                if 'symbol' in item:
                    initial_data.append({
                        "ticker": item['symbol'],
                        "income_statement": income_statements[i]
                    })
            
            # Apply EPS Filter
            screener = Screener(min_eps_growth=min_eps)
            passed_eps = [d for d in initial_data if screener._check_eps_growth(d['income_statement'])]
            console.print(f"[bold blue]✓[/bold blue] {len(passed_eps)} tickers passed EPS growth filter.")
            
            if not passed_eps:
                console.print("[bold yellow]No tickers passed the EPS filter.[/bold yellow]")
                return

            # Phase 2: Technical Filter
            status.update(f"[bold yellow]Phase 2: Checking technicals for {len(passed_eps)} tickers...")
            hist_tasks = [client.fetch_historical_prices(d['ticker']) for d in passed_eps]
            historical_data = await asyncio.gather(*hist_tasks)
            
            passed_tech = []
            for i, d in enumerate(passed_eps):
                d['historical'] = historical_data[i]
                if screener._check_technical(d['historical']):
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
                    client.fetch_share_float(ticker)
                ))
            
            deep_results = await asyncio.gather(*deep_tasks)
            
            passed_tickers = []
            for i, d in enumerate(passed_tech):
                metrics, ratios, float_data = deep_results[i]
                d.update({
                    "key_metrics": metrics,
                    "ratios": ratios,
                    "share_float": float_data
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
                    chart_builder.build_all(ticker, historical)
            
            console.print(f"[bold blue]✓[/bold blue] Chart generation complete.")

    # 5. Display Summary Table
    table = Table(title=f"Screener Results ({datetime.now().strftime('%Y-%m-%d')})")
    table.add_column("Ticker", style="cyan")
    table.add_column("Price", justify="right")
    table.add_column("EPS Growth (Q)", justify="right", style="green")
    
    for data in passed_tickers:
        ticker = data['ticker']
        # Extract latest price from historical or screening data
        latest_price = "N/A"
        if data.get('historical'):
            latest_price = f"${data['historical'][0].get('close', 0):.2f}"
        
        # Calculate EPS growth for display
        eps_growth = "N/A"
        if data.get('income_statement') and len(data['income_statement']) >= 2:
            latest_eps = data['income_statement'][0].get('eps', 0)
            prev_eps = data['income_statement'][1].get('eps', 0)
            if prev_eps and prev_eps != 0:
                growth = ((latest_eps - prev_eps) / abs(prev_eps)) * 100
                eps_growth = f"{growth:+.1f}%"

        table.add_row(ticker, latest_price, eps_growth)
        
    console.print(table)
    console.print(f"\n[bold green]Success![/bold green] Charts saved to [yellow]data/charts/[/yellow]")

@app.command()
def scan(
    universe_limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Max tickers to fetch from FMP."),
    min_eps_growth: Optional[float] = typer.Option(None, "--eps", "-e", help="Minimum YoY EPS growth %."),
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
        asyncio.run(run_pipeline(universe_limit, min_eps_growth))
    except KeyboardInterrupt:
        console.print("\n[bold red]Aborted by user.[/bold red]")
    except Exception as e:
        logger.critical(f"Pipeline Failed: {e}", exc_info=True)
        console.print(f"\n[bold red]CRITICAL ERROR:[/bold red] {e}")

@app.command()
def report(date: str = typer.Argument(datetime.now().strftime("%Y-%m-%d"), help="The date of the batch to report on.")):
    """Parse a completed LLM batch and generate the Markdown report."""
    console.print(f"[bold green]Generating report for {date}...[/bold green]")
    # TODO: Implement generate_report logic here

if __name__ == "__main__":
    app()
