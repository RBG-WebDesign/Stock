# Strategy Definitions & Operational Guide: TQA Integration

## Tier 1: Alpha Drivers (Immediate Implementation)

These strategies represent the core of the techno-quantamental philosophy. They possess the highest expected value and align perfectly with EOD batch processing, leveraging fundamental shifts and clear institutional footprints.

### #51 Volatility Contraction Pattern (VCP)

* **Operational Definition:** A structural charting pattern popularized by Mark Minervini. It identifies the exact point where supply stops coming to market. It is characterized by a series of successive price consolidations (contractions), where each subsequent pullback is shallower than the last, accompanied by a severe "dry up" in trading volume.
* **Nuances & Insights:** The pattern visually represents the absorption of weak holders by strong institutional hands. It is the "calm before the storm."
* **Caveats:** VCPs are highly subjective. In messy, highly volatile markets, traders often hallucinate VCPs in what is actually just erratic chop. True VCPs require a prior established uptrend (minimum 30% advance).
* **TQA Integration Note:** Perfect for the Vision LLM, which excels at qualitative visual assessments like "tightness" and "dry ups" that are mathematically brittle to code. Screen deterministically for price > 50 SMA and 1-month consolidation, then pass the chart to the LLM specifically prompted to count contractions and verify volume dry-up.

### #1 The "First Profit" Small Cap Breakout

* **Operational Definition:** A fundamental strategy targeting small-cap companies that report a positive EPS (Earnings Per Share) quarter for the first time after a prolonged period (4+ quarters) of negative earnings (cash burn).
* **Nuances & Insights:** This exploits an institutional blind spot. Many funds are restricted from buying unprofitable companies. The transition to profitability triggers aggressive re-rating and massive capital inflows as the stock hits institutional radars.
* **Caveats:** Small-cap boards are notorious for using a single "engineered" profitable quarter as a liquidity event to issue secondary offerings. A strict check against share dilution is mandatory to avoid toxic financing traps.
* **TQA Integration Note:** Extremely high expected value and highly deterministic. Use FMP's `income-statement-api` to scan for the first positive EPS after 4 quarters of negative EPS. Crucially, cross-reference with `company-shares-float-liquidity-api` or balance sheet data to filter out companies with massive quarter-over-quarter share count increases to avoid toxic financing traps.

### #54 Relative Strength (RS) Sector Rotation

* **Operational Definition:** A quantitative macro strategy that measures the mathematical outperformance of specific sectors and individual equities against a benchmark (usually the S&P 500) over 3-month and 6-month windows.
* **Nuances & Insights:** "Relative Strength" in this context is not the RSI indicator; it is actual price divergence. When the SPY drops 2% but a specific stock is up 1%, that stock has immense RS. It proves that institutional money is supporting the bid regardless of market gravity.
* **Caveats:** This strategy naturally lags at the absolute bottom of a bear market, as it requires time for new trends to establish statistical dominance.

### #44 Volume Doesn't Lie

* **Operational Definition:** A volume-centric breakout strategy triggered when an asset clears a major daily resistance level on at least 200% (2x) of its 50-day average trading volume.
* **Nuances & Insights:** Price can be manipulated by low-liquidity sweeps, but sustained, massive volume is the undeniable footprint of institutional accumulation.
* **Caveats:** Location is everything. Massive volume breaking out of a 6-month base is highly bullish (accumulation). Massive volume after a stock has already run up 300% over 4 weeks often signals a volume climax (distribution and exhaustion).
* **TQA Integration Note:** Like VCPs, volume analysis is well-suited for the LLM. Algorithmically screen for the volume criteria, but use the LLM to provide contextual confirmation (e.g., verifying if the volume occurs at the breakout of a base rather than a climax top).

### #3 Post-Earnings AVWAP Accumulation

* **Operational Definition:** A technical strategy utilizing the Anchored Volume Weighted Average Price (AVWAP). The VWAP calculation is explicitly anchored to the opening minute of a major post-earnings trading session.
* **Nuances & Insights:** An earnings release fundamentally resets the valuation of a company. By anchoring the VWAP to this exact event, you track the true average cost basis of all market participants acting on the new information, creating a highly reliable, dynamic support line.
* **Caveats:** If the earnings gap occurs on mediocre volume, the AVWAP loses its statistical gravity and becomes meaningless.
* **TQA Integration Note:** Introduces architectural friction. TQA is designed as an EOD scanner using daily/weekly charts. Calculating an exact AVWAP from the opening minute of earnings requires intraday data (e.g., FMP's `5-minute-interval-stock-chart-api`), which increases network I/O and processing complexity.

### #46 Yesterday Hammer Today Strength

* **Operational Definition:** A two-day candlestick continuation strategy. Day 1 features a "Hammer" candle (long lower wick, closing near the high). Day 2 requires the price to break and hold above the high of Day 1.
* **Nuances & Insights:** The hammer visually represents intraday capitulation followed by aggressive buyer intervention. Requiring Day 2 confirmation prevents buying into a "dead cat bounce" that lacks follow-through.
* **Caveats:** This setup requires a supportive broader market tailwind. In severe downtrends, hammers are frequently violated the very next day.

### #47 Engulfing

* **Operational Definition:** A reversal strategy based on the daily Bullish or Bearish Engulfing candlestick pattern, where the real body of the current candle completely covers the real body of the prior candle.
* **Nuances & Insights:** An engulfing candle represents a violent, wholesale shift in market psychology and momentum. It is most effective when it occurs at major structural turning points (e.g., the absolute bottom of a prolonged downtrend).
* **Caveats:** Because the engulfing candle is inherently large, placing a stop-loss at its low mathematically requires a wider risk parameter, necessitating smaller position sizing.

### #41 Trend Play

* **Operational Definition:** A multi-timeframe strategy that requires the alignment of moving average "ribbons" (e.g., 10, 20, 50 EMAs) across both the Daily and Weekly charts, ensuring the asset is in a synchronized uptrend.
* **Nuances & Insights:** Trading in the direction of multi-timeframe confluence provides the highest probability of success, as you face minimal structural resistance.
* **Caveats:** Moving averages are mathematically lagging indicators. By the time daily and weekly ribbons perfectly align, the initial explosive move has already occurred.

### #55 The "Dead Cat" Gap Short

* **Operational Definition:** A specialized short-selling strategy deployed 1-to-3 days after a massive gap down caused by a fundamental catalyst (e.g., disastrous earnings). The entry occurs when retail "bag-holders" attempt to buy the dip, creating a weak rally into a declining moving average (like the 8-EMA), which is then aggressively shorted.
* **Nuances & Insights:** This capitalizes purely on trapped psychology. Existing shareholders hope for a bounce to break even and sell, while short-sellers pile in at resistance, creating a dual-force wave of selling pressure.
* **Caveats:** If the stock is heavily shorted prior to the earnings release, any positive forward guidance on the earnings call can spark a brutal short-squeeze, invalidating the setup entirely.
* **TQA Integration Note:** Introduces mechanical complexities of short selling (borrow fees, margin, unlimited risk, short squeezes). Since TQA currently focuses on long setups, it is recommended to isolate short strategies into a separate, future module.

### #24 Nice Chart

* **Operational Definition:** A composite, highly filtered quantitative setup that requires a strict alignment of RSI levels, specific moving average stacking, and a bullish broader market regime before triggering a new high breakout alert.
* **Nuances & Insights:** This is a "quality over quantity" approach. It systematically filters out noise and low-probability setups, resulting in a high win rate.
* **Caveats:** Heavy composite filtering is highly prone to over-optimization (curve-fitting). In less-than-perfect markets, this strategy may issue zero alerts for weeks.
* **TQA Integration Note:** Highly quantitative. This should be built entirely within `src/tqa/screener/` as deterministic filters. If a stock passes these strict regression/RSI mathematical filters, the LLM is mostly needed just for final visual verification rather than complex pattern detection.

---

## Tier 2: Core Enhancements (High Feasibility, Secondary Priority)

These strategies are fully compatible with EOD batching but require nuanced handling of broader market regimes to avoid false signals.

### #39 Tailwind

* **Operational Definition:** A trend-following strategy relying on slow, methodical moving average crossovers (e.g., 9 EMA crossing the 20 EMA) on daily timeframes.
* **Nuances & Insights:** Structurally safe and operates well on low-beta, grinding large-cap stocks. It assumes institutions are actively defending the moving averages.
* **Caveats:** Brutally ineffective in ranging, choppy markets, resulting in continuous whipsaw losses.

### #4 The "Orderly March"

* **Operational Definition:** A quantitative swing strategy that screens for a high 20-day Linear Regression slope coupled with an $R^2$ value above 0.8, targeting stocks moving in tight, predictable channels.
* **Nuances & Insights:** Excellent for risk-averse traders as it naturally filters out highly volatile, erratic charts in favor of mathematical stability.
* **Caveats:** Will consistently miss hyper-growth, explosive multi-baggers. A sudden fundamental news event can instantly shatter the regression channel.
* **TQA Integration Note:** Similar to #24, this should be built purely as a deterministic mathematical filter within `src/tqa/screener/`.

### #12 Cuts Like a Knife (Short)

* **Operational Definition:** Shorting the breakdown of key support levels immediately following a negative earnings report.
* **Nuances & Insights:** Aligns technical breakdowns with fundamental degradation. It thrives on the panic of institutional funds unwinding large positions over several days.
* **Caveats:** The opening 15 minutes post-earnings are purely chaotic price discovery. Shorting the initial print is gambling; waiting for the intraday lower-high is required.
* **TQA Integration Note:** Like #55, keep shorting mechanics sequestered until long pipelines are fully hardened.

### #6 Alpha Predator

* **Operational Definition:** A multi-timeframe alignment strategy that specifically looks to buy pullbacks on sub-$20 momentum stocks that remain "green" across weekly, daily, and intraday charts.
* **Nuances & Insights:** Buying pullbacks in an established trend is statistically safer than buying the initial breakout, assuming the broader momentum is intact.
* **Caveats:** Sub-$20 equities are inherently volatile. What looks like a standard pullback can instantly morph into a structural reversal.

### #37 Strong Stock Pulling Back

* **Operational Definition:** Buying dips on stocks that are exhibiting high Relative Strength while the broader S&P 500 is undergoing a noticeable correction.
* **Nuances & Insights:** You are parking capital in the market's chosen leaders. When the S&P 500 finally finds support and bounces, these stocks typically explode to new highs.
* **Caveats:** If the S&P 500 correction turns into a full-blown liquidation event, correlations go to 1, and the market will drag even the strongest stocks down with it.

### #9 Bullish Pullback & #33 Quarterback & #17 Got Dough Wants to Go

* **Operational Definition:** A cluster of mathematical dip-buying strategies targeting specific retracements (e.g., a flat 25% drop from highs, or precise Fibonacci levels like 38.2% or 50%) on fundamentally strong names.
* **Nuances & Insights:** These strategies attempt to mathematically define where algorithmic buy programs will step in to support a prior winner.
* **Caveats:** Distinguishing a "healthy 25% technical pullback" from a "fatal fundamental breakdown" is incredibly difficult without deep qualitative context.
* **TQA Integration Note:** Defining structural "swing highs" and "swing lows" mathematically for Fibonacci retracements is famously difficult and prone to edge-case failures. Instead, pass the chart to the Vision LLM and specifically prompt it: "Is this a constructive pullback to the 50 SMA or a structural breakdown?"

### #28 On Support

* **Operational Definition:** A contrarian swing-trading strategy that buys large-cap equities (>$20) exactly as they touch historic, well-defined daily support levels.
* **Nuances & Insights:** Relies on the predictable, smoother price action of mega-caps and the tendency of markets to range rather than trend.
* **Caveats:** Modern algorithmic sweeping often intentionally pierces obvious retail support levels to trigger stop-losses (liquidity grabs) before immediately bouncing the price back up.

### #43 The Vault

* **Operational Definition:** An oversold mean-reversion strategy that refuses to catch falling knives. It waits for the oversold stock to actually break back above the previous day's resistance before triggering an entry.
* **Nuances & Insights:** Much safer than blind dip-buying. It forces the market to prove that buyers have actually regained control of the intraday trend.
* **Caveats:** Deeply oversold stocks often require a long time to repair technical damage, meaning the capital may be tied up in "dead money" as the stock bases sideways for weeks.

---

## Part 3: TQA Advanced Approaches & Prompt Pipelines

Leveraging the premium access to the Financial Modeling Prep (FMP) API, the system can extract sophisticated fundamental context that most retail screeners cannot.

### 1. The "Smart Money Footprint" Approach
While technical volume implies institutional accumulation, FMP allows us to verify it explicitly.
*   **The Strategy:** Screen for standard technical bases, but overlay fundamental insider/institutional data. A VCP is much more likely to resolve upward if insiders are buying the float.
*   **FMP Data:** Utilize `positions-summary-api` or insider trading endpoints to track the velocity of institutional accumulation quarter-over-quarter.
*   **Implementation:** Add a pre-screening step requiring institutional ownership to have increased by >X% in the last reported quarter before sending the payload to the LLM.

### 2. The "Peer Dominance" Analysis
Stocks move in groups. A breakout in a stock is more likely to succeed if its sector and direct peers are also showing strength, but the target stock is the fundamental leader.
*   **The Strategy:** Don't just analyze the stock in a vacuum; force the LLM to compare it against its closest competitors.
*   **FMP Data:** Use `company-peer-comparison-api` combined with `financial-ratios-api` and `key-metrics-api`.
*   **Implementation:** Build a new prompt that feeds the LLM the target ticker's data *and* an aggregated baseline of its top 3 peers.

### 3. Analyst Re-rating Momentum
*   **The Strategy:** Price often follows analyst upgrades. A stock transitioning from a consensus "Hold" to "Buy" creates a mechanical tailwind as funds re-allocate.
*   **FMP Data:** `upgrades-downgrades-consensus-bulk-api` and `price-target-summary-api`.
*   **Implementation:** Filter for stocks whose average price target has been revised upward by >15% in the last 30 days while the stock is consolidating in a base.

---

### Draft Prompts for `config/prompts.yaml`

Based on these new strategies, here are drafted prompts for the LLM analysis pipeline:

#### 1. The "First Profit" Turnaround Prompt
```yaml
first_profit_analyst: |
  Analyze {ticker} for a "First Profit" structural turnaround.
  
  FUNDAMENTAL DATA:
  {fundamentals}
  
  CONTEXT:
  This company has just posted its first profitable quarter after a prolonged period of cash burn.
  
  Part 1: Earnings Quality & Dilution (CRITICAL)
  - Examine the Income Statement: Was profitability driven by actual revenue growth and margin expansion, or just extreme cost-cutting/one-time accounting gains?
  - Examine Share Float/Outstanding: Has the company significantly diluted shareholders to survive? If share count has exploded YoY, this is a toxic trap. Call it out immediately.
  
  Part 2: Technical Reaction
  - Look at the attached charts. How is the market absorbing this fundamental shift? 
  - Is there massive volume stepping in (Institutional re-rating)? 
  - Is the stock forming a constructive base, or is it a wild, uncontrollable gap up?
  
  Output your findings strictly in the TurnaroundOutput JSON format.
```

#### 2. The Peer Comparative Prompt
```yaml
sector_leader_analyst: |
  Determine if {ticker} is the true fundamental and technical leader among its peers.
  
  TARGET METRICS: {fundamentals}
  PEER AVERAGE METRICS: {peer_data}
  
  Part 1: Fundamental Dominance
  - Compare {ticker}'s ROE, Gross Margins, and EPS growth against the Peer Average. 
  - Does {ticker} possess a clear quantitative moat?
  
  Part 2: Relative Strength (Technical)
  - Review the attached charts. While you don't have peer charts, analyze the target's trend structure. 
  - Is it heavily outperforming the broader market (SPY/QQQ proxy)?
  
  Output your findings strictly in the SectorLeaderOutput JSON format, detailing exactly why this stock should command a premium valuation over its peers.
```

#### 3. The "False Breakout / Liquidity Grab" Invalidation Prompt
*(Ideal as a secondary check or in a "Review" pipeline for Tier 2 strategies like "On Support")*
```yaml
liquidity_grab_reviewer: |
  Review the recent price action of {ticker} specifically to identify if recent moves are institutional accumulation or manipulative liquidity grabs.
  
  Look closely at the Daily chart:
  - Did the price recently pierce a major obvious support level (e.g., the 200 SMA or a long-term horizontal line) only to immediately violently reverse back up on high volume? (This is a bullish liquidity grab / trap).
  - Conversely, did it recently break out to new highs, stall immediately, and reverse back into the base? (This is a bearish bull trap).
  
  Define the exact price level that proves the current trend is genuine, and output in the LiquidityReviewOutput JSON format.
```
