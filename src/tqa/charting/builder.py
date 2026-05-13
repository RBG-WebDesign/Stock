# src/tqa/charting/builder.py
import os
from typing import Any, Dict, List, Optional

import matplotlib.patches as patches
import matplotlib.ticker as mticker
import mplfinance as mpf
import pandas as pd
from tqa.utils.logger import logger


class ChartBuilder:
    """
    Generates high-contrast technical charts for Vision LLM analysis.
    Supports both Daily (1-Year) and Weekly (3-Year) timeframes.
    """

    def __init__(self, output_dir: str = "data/charts"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Define high-contrast TradingView-like style
        self.style = mpf.make_mpf_style(
            base_mpf_style='charles',
            facecolor='white',
            edgecolor='black',
            figcolor='white',
            rc={
                'font.size': 10,
                'font.family': 'Arial',
                'axes.labelsize': 10,
                'xtick.labelsize': 8,
                'ytick.labelsize': 8
            }
        )

    def _prepare_dataframe(self, historical_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Converts raw FMP historical JSON data into a clean Pandas DataFrame.
        Expected keys in each dict: 'date', 'open', 'high', 'low', 'close', 'volume'
        """
        if not historical_data:
            raise ValueError("No historical data provided.")

        df = pd.DataFrame(historical_data)

        df = df.rename(columns={
            "date": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        })

        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        # FMP data is often newest to oldest; mplfinance needs oldest to newest
        df.sort_index(ascending=True, inplace=True)

        return df

    def _attach_pct_axis(self, ax_price, ylim, base_price):
        """
        Attaches a % change Y-axis to the LEFT of ax_price using
        secondary_yaxis with forward/inverse transforms.

        This avoids twinx() entirely, which fights with mplfinance's
        internal axis layout and causes both axes to land on the same side.
        """
        def price_to_pct(x):
            return (x / base_price - 1) * 100

        def pct_to_price(x):
            return (x / 100 + 1) * base_price

        ax_pct = ax_price.secondary_yaxis('left', functions=(price_to_pct, pct_to_price))
        ax_pct.set_ylabel('% Change', fontsize=8, fontweight='bold', labelpad=4)
        ax_pct.tick_params(axis='y', labelsize=8, pad=2)
        ax_pct.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))
        ax_pct.grid(False)

        return ax_pct

    def generate_daily_chart(self, ticker: str, df: pd.DataFrame, days: int = 252) -> Optional[str]:
        """
        Generates a daily candlestick chart with SMA 20, 50, 100, 200.
        Includes volume with 50-day volume SMA.
        Price axis on the RIGHT. % Change axis on the LEFT.
        """
        try:
            ticker = ticker.upper()
            logger.debug(f"Generating daily chart for {ticker}...")

            if len(df) < 200:
                logger.warning(f"Not enough data for {ticker} daily chart (need 200+ days).")

            # Calculate SMAs on the FULL dataframe to avoid cutoff at start of plot window
            df = df.copy()
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['SMA50'] = df['Close'].rolling(window=50).mean()
            df['SMA100'] = df['Close'].rolling(window=100).mean()
            df['SMA200'] = df['Close'].rolling(window=200).mean()
            df['VolSMA50'] = df['Volume'].rolling(window=50).mean()

            # Slice the last N days for plotting
            plot_df = df.tail(days).copy()
            last_date = plot_df.index[-1].strftime('%Y-%m-%d')

            latest_prices = {
                'Price': plot_df['Close'].iloc[-1],
                'SMA20': plot_df['SMA20'].iloc[-1],
                'SMA50': plot_df['SMA50'].iloc[-1],
                'SMA100': plot_df['SMA100'].iloc[-1],
                'SMA200': plot_df['SMA200'].iloc[-1]
            }

            apds = []
            if not plot_df['SMA20'].isnull().all():
                apds.append(mpf.make_addplot(plot_df['SMA20'], color='green', width=1.0))
            if not plot_df['SMA50'].isnull().all():
                apds.append(mpf.make_addplot(plot_df['SMA50'], color='blue', width=1.2))
            if not plot_df['SMA100'].isnull().all():
                apds.append(mpf.make_addplot(plot_df['SMA100'], color='orange', width=1.2))
            if not plot_df['SMA200'].isnull().all():
                apds.append(mpf.make_addplot(plot_df['SMA200'], color='red', width=1.5))
            if not plot_df['VolSMA50'].isnull().all():
                apds.append(mpf.make_addplot(plot_df['VolSMA50'], color='blue', width=0.8, panel=1))

            # Y-axis padding: +/- 10% of price range
            ymin = plot_df['Low'].min()
            ymax = plot_df['High'].max()
            price_range = ymax - ymin
            padding = price_range * 0.10
            ylim = (ymin - padding, ymax + padding)

            output_path = os.path.join(self.output_dir, f"{ticker}_daily.png")

            fig, axes = mpf.plot(
                plot_df,
                type='candle',
                style=self.style,
                ylabel='',
                volume=True,
                ylabel_lower='Volume',
                addplot=apds,
                tight_layout=True,
                panel_ratios=(4, 1),
                returnfig=True,
                ylim=ylim
            )

            ax_price = axes[0]

            # Set z-order: SMAs beneath candles
            for line in ax_price.get_lines():
                line.set_zorder(2)

            # Price axis: RIGHT side
            ax_price.yaxis.tick_right()
            ax_price.yaxis.set_label_position("right")

            # Add x-axis padding
            left, right = ax_price.get_xlim()
            padding = (right - left) * 0.05
            ax_price.set_xlim(left - padding, right + padding)

            # "USD" label above the right (price) axis
            ax_price.text(1.025, 1.00, "USD", transform=ax_price.transAxes,
                          fontsize=9, fontweight='bold', ha='center', va='bottom')

            # % Change axis: LEFT side via secondary_yaxis (no twinx)
            base_price = plot_df['Close'].iloc[0]
            self._attach_pct_axis(ax_price, ylim, base_price)

            # SMA legend — upper left, drawn last so it sits above the pct axis spine
            x_pos, y_start, y_step = 0.02, 0.95, 0.04

            rect = patches.Rectangle(
                (0.01, 0.75), 0.18, 0.22,
                transform=ax_price.transAxes,
                facecolor='white', alpha=0.7, edgecolor='gray', zorder=4
            )
            ax_price.add_patch(rect)

            ax_price.text(
                x_pos, y_start, f"Price: {latest_prices['Price']:.2f}",
                transform=ax_price.transAxes, color='black', fontsize=8,
                verticalalignment='top', fontweight='bold', zorder=5
            )

            for i, (label, color) in enumerate([
                ('SMA20', 'green'), ('SMA50', 'blue'), ('SMA100', 'orange'), ('SMA200', 'red')
            ]):
                ax_price.text(
                    x_pos, y_start - (i + 1) * y_step,
                    f"{label}: {latest_prices[label]:.2f}",
                    transform=ax_price.transAxes, color=color, fontsize=8,
                    verticalalignment='top', fontweight='bold', zorder=5
                )

            fig.suptitle(f"{ticker} - Daily (1-Year) - {last_date}",
                         fontsize=12, fontweight='bold', y=1.01)
            fig.savefig(output_path, dpi=150, bbox_inches='tight')

            logger.info(f"Successfully saved daily chart: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate daily chart for {ticker}: {e}")
            return None

    def generate_weekly_chart(self, ticker: str, df: pd.DataFrame) -> Optional[str]:
        """
        Generates a weekly candlestick chart with 10, 30, and 40 week SMA.
        Price axis on the RIGHT. % Change axis on the LEFT.
        """
        try:
            ticker = ticker.upper()
            logger.debug(f"Generating weekly chart for {ticker}...")

            # Resample to Weekly (ending Friday)
            logic = {
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }
            weekly_df = df.resample('W-FRI').apply(logic).dropna()

            # Calculate SMAs on the FULL weekly dataframe
            weekly_df = weekly_df.copy()
            weekly_df['SMA10'] = weekly_df['Close'].rolling(window=10).mean()
            weekly_df['SMA20'] = weekly_df['Close'].rolling(window=20).mean()
            weekly_df['SMA40'] = weekly_df['Close'].rolling(window=40).mean()
            weekly_df['VolSMA10'] = weekly_df['Volume'].rolling(window=10).mean()

            # Slice last 3 years (approx 156 weeks)
            plot_df = weekly_df.tail(156).copy()
            last_date = plot_df.index[-1].strftime('%Y-%m-%d')

            if len(plot_df) < 10:
                logger.warning(f"Not enough data for {ticker} weekly chart.")
                return None

            latest_prices = {
                'Price': plot_df['Close'].iloc[-1],
                'SMA10': plot_df['SMA10'].iloc[-1],
                'SMA20': plot_df['SMA20'].iloc[-1],
                'SMA40': plot_df['SMA40'].iloc[-1]
            }

            apds = []
            if not plot_df['SMA10'].isnull().all():
                apds.append(mpf.make_addplot(plot_df['SMA10'], color='blue', width=1.2))
            if not plot_df['SMA20'].isnull().all():
                apds.append(mpf.make_addplot(plot_df['SMA20'], color='orange', width=1.2))
            if not plot_df['SMA40'].isnull().all():
                apds.append(mpf.make_addplot(plot_df['SMA40'], color='red', width=1.5))
            if not plot_df['VolSMA10'].isnull().all():
                apds.append(mpf.make_addplot(plot_df['VolSMA10'], color='blue', width=0.8, panel=1))

            # Y-axis padding: +/- 10% of price range
            ymin = plot_df['Low'].min()
            ymax = plot_df['High'].max()
            price_range = ymax - ymin
            padding = price_range * 0.10
            ylim = (ymin - padding, ymax + padding)

            output_path = os.path.join(self.output_dir, f"{ticker}_weekly.png")

            fig, axes = mpf.plot(
                plot_df,
                type='candle',
                style=self.style,
                ylabel='',
                volume=True,
                ylabel_lower='Volume',
                addplot=apds,
                tight_layout=True,
                panel_ratios=(4, 1),
                returnfig=True,
                ylim=ylim
            )

            ax_price = axes[0]

            # Set z-order: SMAs beneath candles
            for line in ax_price.get_lines():
                line.set_zorder(2)

            # Price axis: RIGHT side
            ax_price.yaxis.tick_right()
            ax_price.yaxis.set_label_position("right")

            # Add x-axis padding
            left, right = ax_price.get_xlim()
            padding = (right - left) * 0.05
            ax_price.set_xlim(left - padding, right + padding)

            # "USD" label above the right (price) axis
            ax_price.text(1.025, 1.00, "USD", transform=ax_price.transAxes,
                          fontsize=9, fontweight='bold', ha='center', va='bottom')

            # % Change axis: LEFT side via secondary_yaxis (no twinx)
            base_price = plot_df['Close'].iloc[0]
            self._attach_pct_axis(ax_price, ylim, base_price)

            # SMA legend — upper left
            x_pos, y_start, y_step = 0.02, 0.95, 0.04

            rect = patches.Rectangle(
                (0.01, 0.78), 0.18, 0.19,
                transform=ax_price.transAxes,
                facecolor='white', alpha=0.7, edgecolor='gray', zorder=4
            )
            ax_price.add_patch(rect)

            ax_price.text(
                x_pos, y_start, f"Price: {latest_prices['Price']:.2f}",
                transform=ax_price.transAxes, color='black', fontsize=8,
                verticalalignment='top', fontweight='bold', zorder=5
            )

            for i, (label, color) in enumerate([
                ('SMA10', 'blue'), ('SMA20', 'orange'), ('SMA40', 'red')
            ]):
                ax_price.text(
                    x_pos, y_start - (i + 1) * y_step,
                    f"{label} (W): {latest_prices[label]:.2f}",
                    transform=ax_price.transAxes, color=color, fontsize=8,
                    verticalalignment='top', fontweight='bold', zorder=5
                )

            fig.suptitle(f"{ticker} - Weekly (3-Year) - {last_date}",
                         fontsize=12, fontweight='bold', y=1.01)
            fig.savefig(output_path, dpi=150, bbox_inches='tight')

            logger.info(f"Successfully saved weekly chart: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate weekly chart for {ticker}: {e}")
            return None

    def build_all(self, ticker: str, historical_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Orchestrates the generation of all charts for a given ticker.
        """
        results = {}
        try:
            df = self._prepare_dataframe(historical_data)

            daily_path = self.generate_daily_chart(ticker, df)
            if daily_path:
                results["daily"] = daily_path

            weekly_path = self.generate_weekly_chart(ticker, df)
            if weekly_path:
                results["weekly"] = weekly_path

        except Exception as e:
            logger.error(f"Error building charts for {ticker}: {e}")

        return results