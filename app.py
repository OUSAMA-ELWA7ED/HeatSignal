import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="HeatSignal — Temperature Into Money", page_icon="🌡️", layout="wide")

DATA_PATH = Path("data/merged_data.csv")
VIDEO_PATH = Path("assets/hero_video.mp4")

DEFAULT_PRICE_PER_MWH = 45.0  # rough U.S. wholesale average; retail is higher

# ---------- Theme ----------
TEMP_HOT = "#E4572E"     # red-orange — temperature
TEMP_DEEP = "#B23A1A"
ELEC_BLUE = "#2E86DE"    # blue — electricity / demand / price
ELEC_DEEP = "#1B4F8C"
INK = "#1C2733"
PAPER = "#FBFAF8"

CITY_NAME = "Phoenix, AZ"
EIA_RESPONDENT = "AZPS"
THRESHOLD_C = 26.0

PAGES = [
    ("Home", "🏠"),
    ("About", "🧭"),
    ("For Companies", "🏢"),
    ("For Users", "🏠"),
    ("Your Data", "📊"),
]

if "page" not in st.session_state:
    st.session_state.page = "Home"

# =====================================================================
# GLOBAL STYLE
# =====================================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {{
    --temp: {TEMP_HOT};
    --temp-deep: {TEMP_DEEP};
    --elec: {ELEC_BLUE};
    --elec-deep: {ELEC_DEEP};
    --ink: {INK};
}}

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
h1, h2, h3, h4 {{ font-family: 'Poppins', sans-serif; color: var(--ink); }}

.stApp {{
    background:
        radial-gradient(circle at 8% 0%, rgba(228,87,46,0.07), transparent 42%),
        radial-gradient(circle at 95% 12%, rgba(46,134,222,0.08), transparent 40%),
        {PAPER};
}}

/* ---------- Top nav ---------- */
.st-key-topnav {{
    position: sticky; top: 0; z-index: 999;
    background: rgba(251,250,248,0.92);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid rgba(0,0,0,0.06);
    padding: 0.6rem 0.4rem 0.7rem;
    margin: -1rem -1rem 1.6rem;
    box-shadow: 0 2px 14px rgba(0,0,0,0.04);
}}
.st-key-topnav .stButton button {{
    border-radius: 999px !important;
    border: 1.5px solid rgba(0,0,0,0.08) !important;
    background: white !important;
    color: var(--ink) !important;
    font-weight: 600 !important;
    padding: 0.45rem 0.8rem !important;
    transition: all 0.15s ease;
}}
.st-key-topnav .stButton button:hover {{
    border-color: var(--elec) !important;
    color: var(--elec-deep) !important;
    transform: translateY(-1px);
}}
.st-key-topnav [data-testid="baseButton-primary"] {{
    background: linear-gradient(90deg, var(--temp), var(--elec)) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(46,134,222,0.25);
}}
.brand {{
    font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 1.35rem;
    background: linear-gradient(90deg, var(--temp), var(--elec));
    -webkit-background-clip: text; background-clip: text; color: transparent;
    padding-top: 4px;
}}
.brand-sub {{ font-size: 0.72rem; color: #8a8f98; letter-spacing: 0.06em; text-transform: uppercase; margin-top: -6px;}}

/* ---------- Hero ---------- */
.hero-slogan {{
    font-family: 'Poppins', sans-serif; font-size: 2.4rem; font-weight: 800;
    text-align: center; line-height: 1.25; margin: 0.4rem 0 0.3rem;
    background: linear-gradient(90deg, var(--temp-deep), var(--elec-deep));
    -webkit-background-clip: text; background-clip: text; color: transparent;
}}
.hero-sub {{ text-align: center; font-size: 1.08rem; color: #5b6169; max-width: 700px; margin: 0 auto 1.3rem; }}
[data-testid="stVideo"] {{ margin-bottom: 0.4rem; }}
[data-testid="stVideo"] video {{
    border-radius: 20px; max-height: 440px; width: 100%; object-fit: cover;
    box-shadow: 0 14px 34px rgba(28,39,51,0.18);
}}
.legend-row {{ display: flex; gap: 24px; align-items: center; justify-content: center; margin: 0.9rem 0 0.4rem; font-size: 0.88rem; color: #666; }}
.legend-dot {{ display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }}
.temp-chip {{ color: var(--temp-deep); font-weight: 700; }}
.elec-chip {{ color: var(--elec-deep); font-weight: 700; }}

/* ---------- Cards ---------- */
.metric-card {{
    background: white; border-radius: 16px; padding: 1.1rem 1.3rem; margin: 0.4rem 0 1rem;
    border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 6px 18px rgba(28,39,51,0.05);
}}
.metric-card .label {{ font-size: 0.82rem; color: #7a7f87; margin-bottom: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em;}}
.metric-card .value {{ font-size: 1.7rem; font-weight: 800; font-family: 'Poppins', sans-serif; }}
.metric-note {{ font-size: 0.85rem; color: #8a8f98; }}

.info-card {{
    background: white; border-radius: 18px; padding: 1.4rem 1.5rem; height: 100%;
    border: 1px solid rgba(0,0,0,0.05); box-shadow: 0 8px 22px rgba(28,39,51,0.06);
    transition: transform 0.15s ease;
}}
.info-card:hover {{ transform: translateY(-3px); }}
.info-card .icon {{ font-size: 1.8rem; margin-bottom: 0.4rem; display: block; }}
.info-card h4 {{ margin: 0 0 0.4rem; }}
.info-card p {{ color: #5b6169; font-size: 0.93rem; line-height: 1.5; }}
.info-card.temp-border {{ border-top: 4px solid var(--temp); }}
.info-card.elec-border {{ border-top: 4px solid var(--elec); }}

.step-num {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 30px; height: 30px; border-radius: 50%; color: white; font-weight: 700;
    background: linear-gradient(135deg, var(--temp), var(--elec)); margin-bottom: 0.5rem;
}}

/* ---------- Gauge sliders ---------- */
.slider-label {{ font-weight: 700; font-size: 0.95rem; margin-bottom: -0.4rem; color: var(--ink); }}
.gauge-track {{ position: relative; height: 10px; border-radius: 999px; margin: 30px 0 22px; }}
.gauge-marker {{
    position: absolute; top: -30px; transform: translateX(-50%);
    background: var(--ink); color: white; font-size: 0.78rem; font-weight: 700;
    padding: 2px 10px; border-radius: 999px; white-space: nowrap;
    box-shadow: 0 3px 8px rgba(0,0,0,0.18);
}}
.gauge-marker::after {{
    content: ""; position: absolute; bottom: -5px; left: 50%; transform: translateX(-50%);
    border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid var(--ink);
}}
.gauge-scale {{ display:flex; justify-content: space-between; font-size: 0.72rem; color: #9aa0a8; margin-top: -14px;}}

.st-key-temp_slider [role="slider"] {{ background-color: var(--temp) !important; border-color: var(--temp) !important; }}
.st-key-temp_slider [role="slider"]:focus {{ box-shadow: 0 0 0 8px rgba(228,87,46,0.18) !important; }}
.st-key-temp_slider [data-baseweb="slider"] div div {{ background: var(--temp) !important; }}

.st-key-elec_slider [role="slider"] {{ background-color: var(--elec) !important; border-color: var(--elec) !important; }}
.st-key-elec_slider [role="slider"]:focus {{ box-shadow: 0 0 0 8px rgba(46,134,222,0.18) !important; }}
.st-key-elec_slider [data-baseweb="slider"] div div {{ background: var(--elec) !important; }}

/* ---------- Tabs / expanders / misc ---------- */
div[data-testid="stExpander"] {{ border-radius: 12px !important; border: 1px solid rgba(0,0,0,0.06) !important; }}
.badge {{
    display: inline-block; padding: 3px 12px; border-radius: 999px; font-size: 0.75rem;
    font-weight: 700; margin-right: 6px;
}}
.badge-temp {{ background: rgba(228,87,46,0.12); color: var(--temp-deep); }}
.badge-elec {{ background: rgba(46,134,222,0.12); color: var(--elec-deep); }}
hr {{ border-color: rgba(0,0,0,0.06); }}
</style>
""", unsafe_allow_html=True)


# =====================================================================
# TOP NAV
# =====================================================================
with st.container(key="topnav"):
    cols = st.columns([2.2, 1, 1, 1, 1, 1])
    with cols[0]:
        st.markdown('<div class="brand">🌡️⚡ HeatSignal</div><div class="brand-sub">Temperature into money</div>', unsafe_allow_html=True)
    for col, (name, icon) in zip(cols[1:], PAGES):
        with col:
            is_active = st.session_state.page == name
            if st.button(f"{icon} {name}", key=f"nav_{name}",
                         type="primary" if is_active else "secondary",
                         use_container_width=True):
                st.session_state.page = name
                st.rerun()

page = st.session_state.page


# =====================================================================
# SHARED HELPERS
# =====================================================================
def colored_metric(label, value, color):
    st.markdown(
        f'<div class="metric-card"><div class="label">{label}</div>'
        f'<div class="value" style="color:{color}">{value}</div></div>',
        unsafe_allow_html=True
    )


def info_card(icon, title, text, border=""):
    st.markdown(
        f'<div class="info-card {border}"><span class="icon">{icon}</span>'
        f'<h4>{title}</h4><p>{text}</p></div>',
        unsafe_allow_html=True
    )


def gradient_gauge(value, min_v, max_v, unit, low_color, high_color):
    pct = max(0.0, min(1.0, (value - min_v) / (max_v - min_v))) * 100
    st.markdown(f'''
    <div class="gauge-track" style="background: linear-gradient(90deg, {low_color}, {high_color});">
        <div class="gauge-marker" style="left: {pct}%;">{value:,.1f}{unit}</div>
    </div>
    <div class="gauge-scale"><span>{min_v:,.0f}{unit}</span><span>{max_v:,.0f}{unit}</span></div>
    ''', unsafe_allow_html=True)


@st.cache_data
def load_data():
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH, parse_dates=["date"])
    return None


@st.cache_data
def fit_models(df):
    X = sm.add_constant(df["avg_temp_c"])
    y = df["demand_mwh"]
    linear_model = sm.OLS(y, X).fit()

    df = df.copy()
    df["cooling_degrees"] = (df["avg_temp_c"] - THRESHOLD_C).clip(lower=0)
    X_cdd = sm.add_constant(df["cooling_degrees"])
    cdd_model = sm.OLS(y, X_cdd).fit()
    return linear_model, cdd_model


merged_df = load_data()

if merged_df is None:
    st.warning(
        "No dataset found at `data/merged_data.csv`. Export `merged_df` from the FortyGuard "
        "analysis notebook (`merged_df.to_csv('merged_data.csv', index=False)`) and drop it "
        "into this app's `data/` folder to power the demo with real numbers."
    )
    st.stop()

linear_model, cdd_model = fit_models(merged_df)
slope_mwh_per_c = linear_model.params["avg_temp_c"]
baseline_temp = merged_df["avg_temp_c"].mean()
baseline_demand = linear_model.predict([1, baseline_temp])[0]


def temp_c_to_f(c):
    return c * 9 / 5 + 32


# =====================================================================
# PAGE: HOME
# =====================================================================
def render_home():
    st.markdown('<div class="hero-slogan">Every degree has a price.<br>We show you what it is.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">Turning street-level temperature data into dollars — for the '
        'companies who trade energy, and the people who pay for it.</div>',
        unsafe_allow_html=True
    )

    if VIDEO_PATH.exists():
        try:
            st.video(str(VIDEO_PATH), autoplay=True, muted=True, loop=True)
        except TypeError:
            # Older Streamlit without autoplay/loop/muted kwargs
            st.video(str(VIDEO_PATH))
    else:
        st.info("Add your video to assets/hero_video.mp4 to show it here.")

    st.markdown(
        f'<div class="legend-row">'
        f'<span><span class="legend-dot" style="background:{TEMP_HOT}"></span>Temperature</span>'
        f'<span><span class="legend-dot" style="background:{ELEC_BLUE}"></span>Electricity demand and price</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        colored_metric("Days analyzed", f"{len(merged_df)}", INK)
    with c2:
        colored_metric("Case-study city", CITY_NAME, TEMP_DEEP)
    with c3:
        colored_metric("Model fit (R²)", f"{linear_model.rsquared:.2f}", ELEC_DEEP)
    with c4:
        colored_metric("°C → demand slope", f"{slope_mwh_per_c:+.1f} MWh/°C", TEMP_DEEP)

    st.divider()
    st.markdown("### Two ways to use this")
    cc1, cc2 = st.columns(2)
    with cc1:
        info_card("🏢", "I trade or manage energy",
                   "Turn a temperature forecast into a buy/sell/store signal — anticipate demand "
                   "before the price moves, the way storage and trading desks do.",
                   border="temp-border")
        if st.button("Open the companies view →", use_container_width=True):
            st.session_state.page = "For Companies"
            st.rerun()
    with cc2:
        info_card("🏠", "I just pay an electric bill",
                   "See roughly what a hot week costs you, and get concrete ways to blunt the "
                   "hit before the bill arrives.",
                   border="elec-border")
        if st.button("Open the household view →", use_container_width=True):
            st.session_state.page = "For Users"
            st.rerun()

    st.divider()
    st.markdown("### How it works")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown('<span class="step-num">1</span>', unsafe_allow_html=True)
        st.markdown("**Temperature data**  \nFortyGuard's satellite-derived heatmaps give a daily average, min, and max temperature for an area of interest.")
    with s2:
        st.markdown('<span class="step-num">2</span>', unsafe_allow_html=True)
        st.markdown("**Regression model**  \nThat temperature is regressed against EIA electricity demand — plain linear, and a cooling-degree-day version.")
    with s3:
        st.markdown('<span class="step-num">3</span>', unsafe_allow_html=True)
        st.markdown("**Dollar impact**  \nThe demand shift is converted into a price signal for traders, or an extra-cost estimate for households.")

    st.markdown(
        '<p class="metric-note">Data sources: FortyGuard Temperature API (AOI heatmaps) and the U.S. EIA '
        'Electricity RTO API. See the About page for full methodology and caveats.</p>',
        unsafe_allow_html=True
    )


# =====================================================================
# PAGE: ABOUT / METHODOLOGY
# =====================================================================
def render_about():
    st.subheader("🧭 About & methodology")
    st.write(
        "HeatSignal is a demo built on top of the **FortyGuard Temperature API Hackathon starter kit** "
        "(Track 7 — Data Analysis & Correlation). It pairs remote-sensed temperature data with public "
        "electricity demand data to show, concretely, how heat turns into cost."
    )

    st.markdown("#### Data pipeline")
    p1, p2, p3 = st.columns(3)
    with p1:
        info_card("🛰️", "1. Temperature",
                   f"A small area of interest around <b>{CITY_NAME}</b> is queried day-by-day via "
                   "FortyGuard's <code>create_heatmap</code> endpoint, returning AOI-wide average, "
                   "min, and max temperature in °C.", border="temp-border")
    with p2:
        info_card("⚡", "2. Demand",
                   f"Hourly electricity demand for balancing authority <b>{EIA_RESPONDENT}</b> is pulled "
                   "from the EIA Electricity RTO API and aggregated to a daily mean in MWh.",
                   border="elec-border")
    with p3:
        info_card("🔗", "3. Merge & regress",
                   "The two series are joined on date. Rows with missing values are dropped, leaving "
                   f"<b>{len(merged_df)} matched days</b> used in every chart in this app.")

    st.markdown("#### The two models")
    m1, m2 = st.columns(2)
    with m1:
        st.markdown("**Model A — simple linear**")
        st.latex(r"\text{demand}_{\text{MWh}} = \beta_0 + \beta_1 \cdot \text{temp}_{°C}")
        st.write(
            f"Fitted slope **β₁ = {slope_mwh_per_c:+.1f} MWh per °C** "
            f"(R² = {linear_model.rsquared:.2f}). Every extra degree Celsius is associated with "
            f"roughly {abs(slope_mwh_per_c):.0f} MWh of additional average demand in this sample."
        )
    with m2:
        st.markdown("**Model B — cooling-degree-days**")
        st.latex(r"\text{CDD} = \max(0,\ \text{temp}_{°C} - T_{\text{threshold}})")
        st.write(
            f"Air-conditioning load doesn't kick in until people actually need cooling, so this "
            f"version zeroes out temperatures below a comfort threshold of "
            f"**{THRESHOLD_C:.0f}°C ({temp_c_to_f(THRESHOLD_C):.0f}°F)** before regressing "
            f"(R² = {cdd_model.rsquared:.2f})."
        )

    with st.expander("See the raw regression output"):
        t1, t2 = st.tabs(["Linear model", "Cooling-degree-day model"])
        with t1:
            st.text(str(linear_model.summary()))
        with t2:
            st.text(str(cdd_model.summary()))

    with st.expander("Peek at the merged dataset"):
        st.dataframe(merged_df.head(10), use_container_width=True)

    st.markdown("#### Caveats — read before trusting a number here")
    st.markdown(f"""
- **Single city, short window.** This demo covers {len(merged_df)} days for {CITY_NAME} only. A production
  version would run this per-region and re-fit continuously.
- **Price is an assumption, not a market feed.** The default of ${DEFAULT_PRICE_PER_MWH:.0f}/MWh is a rough
  wholesale approximation you can override — it is *not* pulled from a live market.
- **Correlation, not a causal guarantee.** Temperature is a strong driver of cooling demand, but weather also
  correlates with other seasonal effects (tourism, school schedules, etc.) that aren't controlled for here.
- **This is a heuristic, not a trading or billing system.** Treat every signal and dollar figure in this app as
  directional, not authoritative.
""")


# =====================================================================
# PAGE: FOR COMPANIES
# =====================================================================
def render_companies():
    st.subheader("🏢 Turn a temperature forecast into a trading signal")
    st.write(
        "The idea behind storage-arbitrage projects: don't just react to price — anticipate it. "
        "Temperature predicts demand, demand predicts price pressure. Here's that chain made explicit."
    )

    st.markdown('<span class="badge badge-temp">Temperature in</span><span class="badge badge-elec">Dollars out</span>', unsafe_allow_html=True)
    st.write("")

    c1, c2 = st.columns([1, 1.4])
    with c1:
        price_per_mwh = st.number_input(
            "Assumed price ($ / MWh)", min_value=1.0, value=DEFAULT_PRICE_PER_MWH, step=1.0,
            help="Replace with a real regional wholesale price for an accurate figure."
        )
        st.markdown(
            '<p class="metric-note">Wholesale electricity prices swing hard with demand — this is the '
            'lever that turns MWh into money below.</p>', unsafe_allow_html=True
        )
    with c2:
        st.markdown('<div class="slider-label">🌡️ Forecast temperature for tomorrow</div>', unsafe_allow_html=True)
        with st.container(key="temp_slider"):
            forecast_temp = st.slider(
                "Forecast temperature for tomorrow (°C)", label_visibility="collapsed",
                min_value=float(merged_df["avg_temp_c"].min()),
                max_value=float(merged_df["avg_temp_c"].max()) + 5,
                value=float(merged_df["avg_temp_c"].mean()),
                key="companies_temp_slider"
            )
        gradient_gauge(forecast_temp, float(merged_df["avg_temp_c"].min()),
                        float(merged_df["avg_temp_c"].max()) + 5, "°C", "#FFD59E", TEMP_HOT)
        st.caption(f"≈ {temp_c_to_f(forecast_temp):.0f}°F")

    predicted_demand = linear_model.predict([1, forecast_temp])[0]
    demand_delta = predicted_demand - baseline_demand
    dollar_delta = demand_delta * price_per_mwh

    m1, m2, m3 = st.columns(3)
    with m1:
        colored_metric("Predicted demand", f"{predicted_demand:,.0f} MWh", INK)
    with m2:
        colored_metric("Shift vs. average day", f"{demand_delta:+,.0f} MWh", TEMP_DEEP if demand_delta > 0 else ELEC_DEEP)
    with m3:
        colored_metric("Dollar impact", f"${dollar_delta:+,.0f}", TEMP_DEEP if demand_delta > 0 else ELEC_DEEP)

    if demand_delta > 0:
        st.success(
            f"**Signal: SELL / DISCHARGE.** At {forecast_temp:.1f}°C ({temp_c_to_f(forecast_temp):.0f}°F), "
            f"demand is projected above baseline — this is a high-price window. A battery-storage operator "
            f"would typically discharge stored energy now rather than hold it."
        )
    else:
        st.info(
            f"**Signal: CHARGE / STORE.** At {forecast_temp:.1f}°C ({temp_c_to_f(forecast_temp):.0f}°F), "
            f"demand is projected at or below baseline — this is a lower-price window, a better time to "
            f"charge storage for later discharge on a hotter day."
        )

    st.markdown(
        f'<p class="metric-note">Based on a regression of {len(merged_df)} days: each 1°C increase '
        f'is associated with {slope_mwh_per_c:+.1f} MWh in average demand (R²={linear_model.rsquared:.2f}). '
        f'This is a simplified heuristic, not a production trading model.</p>',
        unsafe_allow_html=True
    )

    with st.expander("See the underlying regression"):
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.scatter(merged_df["avg_temp_c"], merged_df["demand_mwh"], alpha=0.55, color=ELEC_BLUE, edgecolor="white")
        ax.axline((baseline_temp, baseline_demand), slope=slope_mwh_per_c, color=TEMP_HOT, linewidth=2.2)
        ax.scatter([forecast_temp], [predicted_demand], color=TEMP_DEEP, s=90, zorder=5, label="Your forecast")
        ax.set_xlabel("Avg daily temperature (°C)")
        ax.set_ylabel("Avg daily demand (MWh)")
        ax.legend()
        ax.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig)

    st.markdown("#### Why this matters for storage & trading desks")
    st.markdown("""
- **Anticipate, don't react.** By the time a price spike shows up on a market feed, the profitable window to
  charge storage cheaply has often already closed. A temperature forecast gives lead time.
- **Cooling-degree-days sharpen the signal near the threshold.** Near the comfort threshold, small temperature
  moves barely move demand; above it, each extra degree matters much more — see the About page for the
  cooling-degree-day model.
- **Regional recalibration is essential.** The slope above is specific to this city's climate and grid mix.
  A deployed version would fit this per balancing authority and refresh it regularly.
""")


# =====================================================================
# PAGE: FOR USERS
# =====================================================================
def render_users():
    st.subheader("🏠 What a hot week actually costs you")
    st.write(
        "Utilities pass rising demand costs on to customers. Here's a rough estimate of what "
        "temperature swings mean for a typical household bill, plus concrete ways to blunt it."
    )

    c1, c2 = st.columns([1, 1.4])
    with c1:
        monthly_bill = st.number_input("Your typical monthly electricity bill ($)", min_value=10.0, value=150.0, step=10.0)
        st.markdown(
            '<p class="metric-note">Used only to scale the demand ratio below into a dollar figure — '
            'not connected to your real meter data.</p>', unsafe_allow_html=True
        )
    with c2:
        st.markdown('<div class="slider-label">🌡️ A hot day\'s temperature this month</div>', unsafe_allow_html=True)
        with st.container(key="temp_slider"):
            hot_days_temp = st.slider(
                "A hot day's temperature this month (°C)", label_visibility="collapsed",
                min_value=float(merged_df["avg_temp_c"].mean()),
                max_value=float(merged_df["avg_temp_c"].max()) + 5,
                value=float(merged_df["avg_temp_c"].max()),
                key="users_temp_slider"
            )
        gradient_gauge(hot_days_temp, float(merged_df["avg_temp_c"].mean()),
                        float(merged_df["avg_temp_c"].max()) + 5, "°C", "#FFD59E", TEMP_HOT)
        st.caption(f"≈ {temp_c_to_f(hot_days_temp):.0f}°F")

    demand_ratio = linear_model.predict([1, hot_days_temp])[0] / baseline_demand
    est_extra_cost = monthly_bill * max(demand_ratio - 1, 0)

    m1, m2 = st.columns(2)
    with m1:
        colored_metric(f"Extra cost at {hot_days_temp:.0f}°C vs. an average day", f"${est_extra_cost:,.0f} / month equiv.", ELEC_DEEP)
    with m2:
        colored_metric("Demand vs. average day", f"{(demand_ratio - 1) * 100:+.0f}%", TEMP_DEEP if demand_ratio > 1 else ELEC_DEEP)

    st.markdown(
        '<p class="metric-note">Rough estimate scaled from the regional demand-temperature relationship, '
        'not your actual meter data — a real product would connect to your utility account for precision.</p>',
        unsafe_allow_html=True
    )

    st.markdown("#### What a range of hot days would cost")
    sample_temps = np.linspace(baseline_temp, float(merged_df["avg_temp_c"].max()) + 5, 6)
    rows = []
    for t in sample_temps:
        ratio = linear_model.predict([1, t])[0] / baseline_demand
        rows.append({
            "Temperature": f"{t:.0f}°C / {temp_c_to_f(t):.0f}°F",
            "Demand vs. average": f"{(ratio - 1) * 100:+.0f}%",
            "Est. extra cost": f"${monthly_bill * max(ratio - 1, 0):,.0f}"
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("#### Ways to blunt the hit")
    cc1, cc2 = st.columns(2)
    with cc1:
        info_card("🌅", "Pre-cool during cheap hours",
                   "Run AC harder in the early morning (lower demand, often lower rates) so the unit "
                   "works less during peak afternoon heat.", border="temp-border")
        info_card("🔌", "Shift heavy appliances off-peak",
                   "Laundry, dishwashers, and EV charging during off-peak hours avoid adding to the "
                   "exact demand spike that drives prices up.", border="elec-border")
    with cc2:
        info_card("📡", "Watch the forecast, not just the thermostat",
                   "A hot day like the one you set above is a signal, not a surprise — plan usage "
                   "around it a day ahead.", border="temp-border")
        info_card("🌡️", "Small setpoint changes compound",
                   "Each degree you raise your thermostat during a hot spell meaningfully reduces "
                   "your contribution to peak demand — and your bill.", border="elec-border")


# =====================================================================
# PAGE: YOUR DATA
# =====================================================================
def render_own_data():
    st.subheader("📊 Run this on your own outcome data")
    st.write(
        "Upload a CSV with columns `date, lat, lon, outcome_value` and see how it would correlate "
        "with local temperature. This is the same toolkit used to build the demand model in this app — "
        "swap in hospital admissions, foot traffic, ridership, ice-cream sales, anything you want to test."
    )

    st.markdown("#### Expected format")
    example = pd.DataFrame({
        "date": ["2026-06-01", "2026-06-02"],
        "lat": [33.4484, 33.4484],
        "lon": [-112.0740, -112.0740],
        "outcome_value": [128, 142],
    })
    st.dataframe(example, use_container_width=True, hide_index=True)

    uploaded = st.file_uploader("Upload CSV", type="csv")
    if uploaded is not None:
        st.info(
            "This demo ships with the pre-fetched temperature dataset for the app above and doesn't call "
            "the FortyGuard API live. To regress your uploaded outcomes against fresh temperature data, run "
            "`regression_toolkit(client, your_csv_path)` from the FortyGuard starter notebook with this file."
        )
        preview = pd.read_csv(uploaded)
        st.dataframe(preview.head(), use_container_width=True)

    with st.expander("How `regression_toolkit()` works, from the notebook"):
        st.markdown("""
1. Reads your CSV and groups rows by unique **(lat, lon)** pairs — batching API calls by location rather
   than per-row, since many rows typically share the same site.
2. For each location, builds a small bounding-box AOI and fetches daily temperature from FortyGuard for
   every date present in your data.
3. Merges your `outcome_value` with the fetched temperature on date and location.
4. Runs the same OLS regression used above, so you get a slope and R² for *your* outcome variable against
   temperature — no code changes required, just a differently-shaped CSV.
""")


# =====================================================================
# ROUTING
# =====================================================================
if page == "Home":
    render_home()
elif page == "About":
    render_about()
elif page == "For Companies":
    render_companies()
elif page == "For Users":
    render_users()
elif page == "Your Data":
    render_own_data()
