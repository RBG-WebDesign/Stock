# main.py
# Rough draft of the main entry point for the TQA project.
import asyncio
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, FloatPrompt, Prompt
from rich.table import Table

from tqa.utils.logger import logger
from config.settings import settings

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

async def run_pipeline(universe_size: int, min_eps: float):
    """
    The actual orchestration logic.
    This will eventually call your screener, fetchers, and LLM modules.
    """
    logger.info(f"Starting scan: Universe={universe_size}, Min EPS={min_eps}%")
    
    with console.status("[bold green]Fetching Universe data from FMP...") as status:
        # TODO: Implement universe = await FMPClient().get_universe(limit=universe_size)
        await asyncio.sleep(1) # Simulate
        console.print(f"[bold blue]✓[/bold blue] Found {universe_size} tickers in target market cap range.")
        
        status.update("[bold yellow]Applying Deterministic Filters...")
        # TODO: Implement screened = await Screener().apply(universe, min_eps)
        await asyncio.sleep(1)
        console.print("[bold blue]✓[/bold blue] 42 Tickers survived math filters.")

        status.update("[bold magenta]Generating Technical Charts...")
        # TODO: Implement ChartBuilder().generate_batch(screened)
        await asyncio.sleep(1)
        
    # Example table output
    table = Table(title="Screener Results (Deterministic Phase)")
    table.add_column("Ticker", style="cyan")
    table.add_column("Price", justify="right")
    table.add_column("EPS Growth", justify="right", style="green")
    table.add_row("NVDA", "$900.10", "+450%")
    table.add_row("SMCI", "$850.50", "+320%")
    console.print(table)

@app.command()
def scan(
    universe_limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Max tickers to fetch from FMP."),
    min_eps_growth: Optional[float] = typer.Option(None, "--eps", "-e", help="Minimum YoY EPS growth %."),
):
    """Run the end-to-end Quantamental scan."""
    print_banner()

    # Interactive prompts if arguments are missing
    if universe_limit is None:
        universe_limit = IntPrompt.ask("[bold cyan]How many tickers should we pull from the FMP universe?[/bold cyan]", default=500)
    
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