# src/tqa/utils/report_builder.py
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from fpdf import FPDF
from datetime import datetime
from config.settings import settings
from tqa.utils.data_formatter import format_large_number, format_currency

class PDFGenerator(FPDF):
    def __init__(self, compact: bool = False):
        super().__init__()
        self.compact = compact
        self.theme_primary = (46, 80, 119)  # Dark Blue #2E5077
        self.theme_success = (76, 175, 80)  # Green #4CAF50
        self.theme_danger = (244, 67, 54)   # Red #F44336
        self.theme_text = (50, 50, 50)
        self.theme_light_grey = (245, 245, 245)
        
        # Spacing configurations (Compact vs Roomy)
        self.spacing = {
            'chapter_h': 8 if compact else 10,
            'chapter_ln': 3 if compact else 5,
            'param_h': 8 if compact else 10,
            'param_ln_top': 4 if compact else 5,
            'param_row_h': 6 if compact else 7,
            'param_ln_bottom': 6 if compact else 10,
            'funnel_h': 9 if compact else 10,
            'funnel_ln': 6 if compact else 10,
            'ticker_font': 26 if compact else 28,
            'ticker_h': 12 if compact else 15,
            'ticker_nudge': 2 if compact else 4,
            'ticker_ln': 10 if compact else 15,
            'overview_h': 6 if compact else 8,
            'desc_ln': 3 if compact else 5,
            'metric_h': 14 if compact else 15,
            'metric_ln': 4 if compact else 5,
            'section_ln': 1 if compact else 4,
            'inline_ln': 0.5 if compact else 1.5
        }
        
        # Load Local Unicode Fonts (Inter)
        font_dir = Path("fonts")
        if (font_dir / "Inter-Regular.otf").exists():
            self.add_font("Inter", "", str(font_dir / "Inter-Regular.otf"))
            self.add_font("Inter", "B", str(font_dir / "Inter-Bold.otf"))
            self.add_font("Inter", "I", str(font_dir / "Inter-Italic.otf"))
            self.default_font = "Inter"
        else:
            # Fallback to system DejaVu if available
            font_path = "/usr/share/fonts/truetype/dejavu"
            if os.path.exists(font_path):
                self.add_font("DejaVu", "", f"{font_path}/DejaVuSans.ttf")
                self.add_font("DejaVu", "B", f"{font_path}/DejaVuSans-Bold.ttf")
                self.add_font("DejaVu", "I", f"{font_path}/DejaVuSans-Oblique.ttf")
                self.default_font = "DejaVu"
            else:
                self.default_font = "helvetica"

    def header(self):
        if self.page_no() == 1:
            self.set_fill_color(*self.theme_primary)
            self.rect(0, 0, 210, 40, 'F')
            self.set_text_color(255, 255, 255)
            self.set_font(self.default_font, "B", 24)
            self.set_xy(10, 10)
            self.cell(0, 15, "Techno-Quantamental Report", ln=True)
            self.set_font(self.default_font, "I", 10)
            self.cell(0, 5, f"Automated Institutional-Grade Analysis | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            self.ln(20)
        else:
            self.set_fill_color(*self.theme_primary)
            self.rect(0, 0, 210, 15, 'F')
            self.set_text_color(255, 255, 255)
            self.set_font(self.default_font, "B", 10)
            self.set_xy(10, 3)
            self.cell(100, 10, "Techno-Quantamental Analysis Report")
            self.cell(0, 10, f"Page {self.page_no()}", align="R")
            self.ln(15)
        self.set_text_color(*self.theme_text)

    def write_labeled_value(self, label: str, value: str, is_last: bool = False):
        self.set_font(self.default_font, "B", 9)
        self.write(5, f"{label}: ")
        self.set_font(self.default_font, "", 9)
        suffix = " | " if not is_last else ""
        self.write(5, f"{str(value)}{suffix}")

    def draw_badge(self, text: str, score: int):
        if score >= 8:
            color = self.theme_success
        elif score >= 5:
            color = (255, 152, 0)  # Orange
        else:
            color = self.theme_danger
            
        x, y = self.get_x(), self.get_y()
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font(self.default_font, "B", 10)
        
        w = self.get_string_width(text) + 10
        self.rounded_rect(x, y, w, 8, 2, 'F')
        self.cell(w, 8, text, align="C")
        self.set_text_color(*self.theme_text)
        return w

    def draw_metric_box(self, label: str, value: str, color=None, w=60, h=18):
        start_x = self.get_x()
        start_y = self.get_y()
        
        self.set_fill_color(*self.theme_light_grey)
        self.rect(start_x, start_y, w, h, 'F')
        
        self.set_font(self.default_font, "B", 7)
        self.set_text_color(100, 100, 100)
        self.set_xy(start_x + 2, start_y + 2)
        self.cell(w - 4, 4, label.upper(), ln=True)
        
        self.set_font(self.default_font, "B", 13)
        if color:
            self.set_text_color(*color)
        else:
            self.set_text_color(*self.theme_text)
        
        # Center value in the remaining space below the label
        label_bottom = start_y + 2 + 4  # label top offset + label height
        remaining_h = (start_y + h) - label_bottom
        value_h = 6  # approximate glyph height for font size 13
        centered_y = label_bottom + (remaining_h - value_h) / 2

        self.set_xy(start_x + 2, centered_y)
        self.cell(w - 4, value_h, str(value))
        
        self.set_xy(start_x + w, start_y)
        self.set_text_color(*self.theme_text)

    def chapter_title(self, label: str):
        self.set_font(self.default_font, "B", 14)
        self.set_text_color(*self.theme_primary)
        self.cell(0, self.spacing['chapter_h'], label, ln=True)
        self.line(self.l_margin, self.get_y(), 210 - self.r_margin, self.get_y())
        self.ln(self.spacing['chapter_ln'])
        self.set_text_color(*self.theme_text)

    def draw_parameter_grid(self, config: Dict[str, Any]):
        self.set_font(self.default_font, "B", 11)
        self.set_text_color(*self.theme_primary)
        self.cell(0, self.spacing['param_h'], "Run Configuration Parameters", ln=True)
        self.line(self.l_margin, self.get_y(), 210 - self.r_margin, self.get_y())
        self.ln(self.spacing['param_ln_top'])
        
        self.set_font(self.default_font, "", 9)
        self.set_text_color(*self.theme_text)
        
        params = []
        # Pipeline
        p = config.get("pipeline", {})
        params.extend([
            ("Model", str(config.get("model", p.get("model", "N/A")))),
            ("Universe Limit", str(config.get("universe_limit", p.get("universe_limit", "N/A")))),
            ("Prompt Mode", str(config.get("prompt_mode", p.get("prompt_mode", "N/A")))),
            ("Max News Chars", str(config.get("news_summary_max_chars", p.get("news_summary_max_chars", "N/A")))),
        ])
        
        # Fundamental
        f = config.get("fundamental_filters", {})
        params.extend([
            ("Min EPS Growth", f"{config.get('min_eps_growth', f.get('min_eps_growth', 'N/A'))}%"),
            ("Min Latest EPS", str(config.get("min_latest_eps", f.get("min_latest_eps", "None")))),
            ("Min Rev Growth", f"{config.get('min_rev_growth', f.get('min_rev_growth', 'N/A'))}%"),
            ("Max Rev Growth", f"{config.get('max_rev_growth', f.get('max_rev_growth', 'None'))}%"),
            ("Min Prev EPS", str(config.get("min_prev_eps", f.get("min_prev_eps", "None")))),
            ("Max Prev EPS", str(config.get("max_prev_eps", f.get("max_prev_eps", "None")))),
        ])

        # Market Cap
        mc = config.get("market_cap", {})
        def format_mc(val):
            try:
                if val is None or val == "None": return "None"
                # Use USD for config display since screener thresholds are usually conceptualized in USD or local
                # but for simplicity we'll keep the $ here or omit it if we don't know the intended currency of the config
                return f"${int(val):,}"
            except:
                return "None"

        min_mc = config.get('min_market_cap')
        if min_mc is None and mc.get('min_m'): min_mc = int(mc.get('min_m') * 1e6)
        
        max_mc = config.get('max_market_cap')
        if max_mc is None and mc.get('max_m'): max_mc = int(mc.get('max_m') * 1e6)

        params.extend([
            ("Min Market Cap", format_mc(min_mc)),
            ("Max Market Cap", format_mc(max_mc))
        ])

        # Draw in 2 columns
        col_w = (210 - self.l_margin - self.r_margin) / 2
        for i in range(0, len(params), 2):
            p1 = params[i]
            self.set_font(self.default_font, "B", 9)
            self.cell(35, self.spacing['param_row_h'], f"{p1[0]}:")
            self.set_font(self.default_font, "", 9)
            self.cell(col_w - 35, self.spacing['param_row_h'], p1[1])
            
            if i + 1 < len(params):
                p2 = params[i + 1]
                self.set_font(self.default_font, "B", 9)
                self.cell(35, self.spacing['param_row_h'], f"{p2[0]}:")
                self.set_font(self.default_font, "", 9)
                self.cell(col_w - 35, self.spacing['param_row_h'], p2[1], ln=True)
            else:
                self.ln(self.spacing['param_row_h'])

        # Technical Filters
        tech = config.get("technical_filters")
        if tech:
            self.ln(self.spacing['chapter_ln'])
            self.set_font(self.default_font, "B", 9)
            self.cell(0, 6, "Technical Filters:", ln=True)
            self.set_font(self.default_font, "", 8)
            filter_text = ", ".join(tech)
            self.multi_cell(0, 4, filter_text)
        
        self.ln(self.spacing['param_ln_bottom'])

    def funnel_infographic(self, stats: Dict[str, int]):
        self.chapter_title("Pipeline Filtering Funnel")
        
        u = stats.get("universe_count", 0)
        f = stats.get("fundamental_passed_count", 0)
        t = stats.get("technical_passed_count", 0)
        w = stats.get("final_watchlist_count", 0)

        def safe_pct(n, d):
            return (n / d * 100) if d > 0 else 0

        cols = [
            ("Universe (Initial)", f"{u}", "100%"),
            ("Fundamental Filter", f"{f}", f"{safe_pct(f, u):.1f}%"),
            ("Technical Filter", f"{t}", f"{safe_pct(t, f):.1f}%"),
        ]
        
        self.set_font(self.default_font, "B", 10)
        self.set_fill_color(*self.theme_primary)
        self.set_text_color(255, 255, 255)
        self.cell(80, self.spacing['funnel_h'], " Stage", 1, 0, 'L', True)
        self.cell(40, self.spacing['funnel_h'], " Count", 1, 0, 'C', True)
        self.cell(40, self.spacing['funnel_h'], " Retention", 1, 1, 'C', True)
        
        self.set_font(self.default_font, "", 10)
        self.set_text_color(*self.theme_text)
        for i, (label, count, pct) in enumerate(cols):
            fill = (i % 2 == 1)
            if fill: self.set_fill_color(*self.theme_light_grey)
            self.cell(80, self.spacing['funnel_h'], f" {label}", 1, 0, 'L', fill)
            self.cell(40, self.spacing['funnel_h'], count, 1, 0, 'C', fill)
            self.cell(40, self.spacing['funnel_h'], pct, 1, 1, 'C', fill)
        
        self.ln(self.spacing['funnel_ln'])

    def write_section(self, title: str, text: str, color=None):
        epw = self.epw
        self.set_font(self.default_font, "B", 10)
        if color:
            self.set_text_color(*color)
        else:
            self.set_text_color(*self.theme_primary)
        self.cell(0, 4, title, ln=True)
        self.line(self.get_x(), self.get_y(), self.get_x() + epw, self.get_y())
        self.ln(0.5)
        
        self.set_font(self.default_font, "", 9)
        self.set_text_color(*self.theme_text)
        self.multi_cell(epw, 4, str(text))
        self.ln(self.spacing['section_ln'])

    def write_inline_section(self, title: str, text: str, color=None):
        self.set_font(self.default_font, "B", 9)
        if color:
            self.set_text_color(*color)
        else:
            self.set_text_color(*self.theme_primary)
        
        self.write(4, f"{title}: ")
        self.set_font(self.default_font, "", 9)
        self.set_text_color(*self.theme_text)
        self.write(4, f"{str(text)}\n")
        self.ln(self.spacing['inline_ln'])

    def rounded_rect(self, x, y, w, h, r, style=''):
        k = self.k
        hp = self.h
        if style == 'F':
            op = 'f'
        elif style == 'FD' or style == 'DF':
            op = 'B'
        else:
            op = 'S'
        my_arc = 4 / 3 * (pow(2, 0.5) - 1)
        self._out(f'{(x) * k:.2f} {(hp - y) * k:.2f} m')
        xc = x + w
        yc = y + h
        self._out(f'{(xc - r) * k:.2f} {(hp - y) * k:.2f} l')
        self._arc(xc - r + r * my_arc, y, xc, y + r - r * my_arc, xc, y + r)
        self._out(f'{(xc) * k:.2f} {(hp - (yc - r)) * k:.2f} l')
        self._arc(xc, yc - r + r * my_arc, xc - r + r * my_arc, yc, xc - r, yc)
        self._out(f'{(x + r) * k:.2f} {(hp - yc) * k:.2f} l')
        self._arc(x + r - r * my_arc, yc, x, yc - r + r * my_arc, x, yc - r)
        self._out(f'{(x) * k:.2f} {(hp - (y + r)) * k:.2f} l')
        self._arc(x, y + r - r * my_arc, x + r - r * my_arc, y, x + r, y)
        self._out(op)

    def _arc(self, x1, y1, x2, y2, x3, y3):
        h = self.h
        self._out(f'{x1 * self.k:.2f} {(h - y1) * self.k:.2f} {x2 * self.k:.2f} {(h - y2) * self.k:.2f} {x3 * self.k:.2f} {(h - y3) * self.k:.2f} c')

def generate_pdf_report(session_id: str, min_confidence: float = 0.0, compact: Optional[bool] = None):
    session_dir = settings.REPORTS_DIR / "runs" / session_id
    config_path = session_dir / "run_config.json"
    prompts_path = session_dir / "prompts_debug.jsonl"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found for session {session_id}")
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Auto-detect compact mode if not explicitly provided
    if compact is None:
        prompt_mode = config.get("pipeline", {}).get("prompt_mode", "")
        compact = "can_slim" in prompt_mode.lower()

    stock_analyses = []
    if prompts_path.exists():
        with open(prompts_path, "r") as f:
            for line in f:
                try:
                    stock_analyses.append(json.loads(line))
                except:
                    continue
    
    final_stocks = []
    for entry in stock_analyses:
        response = entry.get("response")
        if not response: continue
        
        conf = response.get("confidence_score", 0)
        if conf >= min_confidence:
            final_stocks.append(entry)

    final_stocks.sort(key=lambda x: x.get("response", {}).get("confidence_score", 0), reverse=True)

    pdf = PDFGenerator(compact=compact)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.draw_parameter_grid(config)
    pdf.funnel_infographic(config.get("funnel_stats", {}))
    
    for stock in final_stocks:
        ticker = stock.get("ticker")
        res = stock.get("response", {})
        conf = res.get("confidence_score", 0)
        profile = stock.get("profile", {})
        
        pdf.add_page()
        
        # --- Ticker + Confidence badge row ---
        pdf.set_font(pdf.default_font, "B", pdf.spacing['ticker_font'])
        pdf.set_text_color(*pdf.theme_primary)
        pdf.cell(80, pdf.spacing['ticker_h'], ticker)

        pdf.set_y(pdf.get_y() + pdf.spacing['ticker_nudge'])
        pdf.set_x(120)
        pdf.draw_badge(f"CONFIDENCE: {conf}/10", conf)
        pdf.ln(pdf.spacing['ticker_ln'])

        # --- Company Profile Section ---
        if profile:
            pdf.set_font(pdf.default_font, "B", 10)
            pdf.set_text_color(*pdf.theme_primary)
            pdf.cell(0, pdf.spacing['overview_h'], "Company Overview", ln=True)
            pdf.set_font(pdf.default_font, "", 9)
            pdf.set_text_color(*pdf.theme_text)
            
            # --- Company Metadata Row 1 ---
            pdf.write_labeled_value("Sector", profile.get('sector', 'N/A'))
            pdf.write_labeled_value("Industry", profile.get('industry', 'N/A'))
            pdf.write_labeled_value("Country", profile.get('country', 'N/A'))
            pdf.write_labeled_value("Exchange", profile.get('exchange') or profile.get('exchangeShortName', 'N/A'), is_last=True)
            pdf.ln(5)

            # --- Company Metadata Row 2 ---
            currency = profile.get('currency', 'USD')
            mkt_cap = profile.get('marketCap') or profile.get('mktCap')
            mkt_cap_str = f"{format_currency(mkt_cap, currency)}" if mkt_cap else "N/A"
            # Since format_currency includes decimals and large number suffixes are usually better for market cap:
            mkt_cap_str = f"{currency} {format_large_number(mkt_cap)}" if mkt_cap else "N/A"
            pdf.write_labeled_value("Market Cap", mkt_cap_str)

            rev = profile.get('recent_revenue')
            rev_str = f"{currency} {format_large_number(rev)}" if rev else "N/A"
            pdf.write_labeled_value("Revenue", rev_str)
            
            earn = profile.get('recent_earnings')
            earn_str = f"{currency} {format_large_number(earn)}" if earn else "N/A"
            pdf.write_labeled_value("Earnings", earn_str, is_last=True)
            pdf.ln(6)
            
            desc = profile.get('description', '')
            if desc:
                if len(desc) > 500:
                    desc = desc[:500] + "..."
                pdf.set_font(pdf.default_font, "", 8) # No italics, smaller font
                pdf.multi_cell(0, 4, desc)
            pdf.ln(pdf.spacing['desc_ln'])
        
        pdf.set_text_color(*pdf.theme_text)

        # --- Metric boxes ---
        y_metrics = pdf.get_y()
        box_w = 46
        box_h = pdf.spacing['metric_h']
        spacing = 2

        currency = profile.get('currency', 'USD')
        pdf.draw_metric_box("Entry Pivot", format_currency(res.get('suggested_entry_pivot'), currency), pdf.theme_success, w=box_w, h=box_h)

        pdf.set_xy(pdf.get_x() + spacing, y_metrics)
        pdf.draw_metric_box("Stop Loss", format_currency(res.get('suggested_stop_loss'), currency), pdf.theme_danger, w=box_w, h=box_h)

        entry = res.get('suggested_entry_pivot')
        stop = res.get('suggested_stop_loss')
        rr_val, target_val = "N/A", "N/A"
        if isinstance(entry, (int, float)) and isinstance(stop, (int, float)) and entry > stop:
            risk = entry - stop
            reward = entry * 0.20
            rr_val = f"{(reward / risk):.2f}:1"
            target_val = format_currency(entry * 1.20, currency)

        pdf.set_xy(pdf.get_x() + spacing, y_metrics)
        pdf.draw_metric_box("Target (20%)", target_val, w=box_w, h=box_h)

        pdf.set_xy(pdf.get_x() + spacing, y_metrics)
        pdf.draw_metric_box("Reward/Risk", rr_val, w=box_w, h=box_h)

        pdf.set_y(y_metrics + box_h + pdf.spacing['metric_ln'])

        epw = pdf.epw

        # Define fields to exclude from dynamic section rendering (already shown in header/metrics)
        exclude_fields = {
            'ticker', 'confidence_score', 'suggested_entry_pivot', 'suggested_stop_loss',
            'is_breakout_safe'
        }

        # Fields to use compact rendering for
        compact_fields = {
            'c_current_earnings', 'a_annual_earnings', 'n_new_catalyst',
            's_supply_demand', 'l_leader_laggard', 'i_institutional_sponsorship',
            'm_market_direction',
            'institutional_trend_analysis', 'pocket_pivots_identified',
            'analyst_sentiment_summary', 'price_volume_footprint',
            'base_tightness_grading'
        }

        # Dynamic Section Rendering based on schema fields
        for field_name, field_value in res.items():
            if field_name in exclude_fields or not field_value:
                continue
            
            # Format field name for title (Compact labels)
            if field_name == 'c_current_earnings': title = "Current Quarterly Earnings"
            elif field_name == 'a_annual_earnings': title = "Annual Earnings Growth"
            elif field_name == 'n_new_catalyst': title = "New Catalyst"
            elif field_name == 's_supply_demand': title = "Supply and Demand"
            elif field_name == 'l_leader_laggard': title = "Leader or Laggard"
            elif field_name == 'i_institutional_sponsorship': title = "Institutional Sponsorship"
            elif field_name == 'm_market_direction': title = "Market Direction"
            else:
                title = field_name.replace('_', ' ').title()
            
            # Use color for specific sections
            section_color = None
            if 'risk' in field_name.lower() or 'bear' in field_name.lower():
                section_color = pdf.theme_danger
                
                # Render risks in a highlighted box
                curr_y = pdf.get_y()
                pdf.set_fill_color(255, 245, 245)
                
                pdf.set_font(pdf.default_font, "", 9)
                lines = pdf.multi_cell(epw - 4, 4, str(field_value), split_only=True)
                h = (len(lines) * 4) + 4 # some padding
                
                if curr_y + h > 250:
                    pdf.add_page()
                    curr_y = pdf.get_y()
                
                pdf.rect(pdf.l_margin, curr_y, epw, h, 'F')
                pdf.set_xy(pdf.l_margin, curr_y + 1)
                pdf.write_section(title, field_value, color=section_color)
                pdf.set_y(curr_y + h + 2)
            else:
                # Optimized color logic to avoid accidental green on pillars
                if field_name in ['bull_case', 'fundamental_catalyst']:
                    section_color = pdf.theme_success
                
                if field_name in compact_fields:
                    pdf.write_inline_section(title, field_value, color=section_color)
                else:
                    pdf.write_section(title, field_value, color=section_color)

        # --- Charts ---
        chart_dir = Path("data/charts")
        today = datetime.now().strftime("%Y-%m-%d")
        daily_chart = chart_dir / f"{ticker}_daily_{today}.png"
        weekly_chart = chart_dir / f"{ticker}_weekly_{today}.png"
        
        if not daily_chart.exists():
            matches = list(chart_dir.glob(f"{ticker}_daily_*.png"))
            if matches: daily_chart = matches[0]
        if not weekly_chart.exists():
            matches = list(chart_dir.glob(f"{ticker}_weekly_*.png"))
            if matches: weekly_chart = matches[0]

        if daily_chart.exists() or weekly_chart.exists():
            y_start = pdf.get_y()
            if y_start > 180:
                pdf.add_page()
                y_start = pdf.get_y()
            
            pdf.set_font(pdf.default_font, "B", 10)  # Reduced from 11 → 10
            pdf.set_text_color(*pdf.theme_primary)
            pdf.cell(0, 8, "Technical Charts (Daily & Weekly)", ln=True)
            y_img = pdf.get_y()
            
            if daily_chart.exists() and weekly_chart.exists():
                chart_w = (epw - 5) / 2
                pdf.image(str(daily_chart), x=pdf.l_margin, y=y_img, w=chart_w)
                pdf.image(str(weekly_chart), x=pdf.l_margin + chart_w + 5, y=y_img, w=chart_w)
                pdf.set_y(y_img + 75)
            elif daily_chart.exists():
                pdf.image(str(daily_chart), x=pdf.l_margin, y=y_img, w=epw)
                pdf.set_y(y_img + 100)
        
    timestamp = datetime.now().strftime("%H%M%S")
    conf_str = str(min_confidence).replace('.', 'p')
    # Save directly to data/reports as requested, instead of the session subfolder
    output_path = settings.REPORTS_DIR / f"TQA_Report_{session_id}_c{conf_str}_{timestamp}.pdf"
    
    pdf.output(str(output_path))
    return output_path