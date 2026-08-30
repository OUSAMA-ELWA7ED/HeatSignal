# 🌡️⚡ HeatSignal

**Every degree has a price. We show you what it is.**

HeatSignal turns satellite-derived temperature data into real financial signals — a trading/dispatch signal for energy companies, and a plain-English cost estimate for households. Built for the **FortyGuard Hackathon**.

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FortyGuard](https://img.shields.io/badge/Powered%20by-FortyGuard%20Temperature%20API-E4572E)](https://fortyguard.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> 📺 **Demo video:** [Add YouTube/Loom link here]
> 🚀 **Live demo:** [Add live app link here]
>
> *(GitHub doesn't autoplay local video files in a README — the app itself autoplays `assets/hero_video.mp4` as a hero banner once it's running.)*

---

## Table of contents

- [What it does](#what-it-does)
- [Why it matters](#why-it-matters)
- [How it works](#how-it-works)
- [App tour](#app-tour)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Deployment](#deployment)
- [Data & methodology](#data--methodology)
- [Caveats](#caveats)
- [Roadmap](#roadmap)
- [Acknowledgments](#acknowledgments)

---

## What it does

HeatSignal pairs [FortyGuard's](https://fortyguard.com) satellite temperature data with public electricity demand data and fits a regression model between the two. That model then powers two very different tools in one app:

| | |
|---|---|
| 🏢 **For energy companies** | Turn a forecast temperature into a **sell/discharge** or **charge/store** signal — anticipate demand before the price moves. |
| 🏠 **For everyday users** | See roughly what a hot day **adds to your electricity bill**, and concrete ways to reduce it. |
| 📊 **Bring your own data** | Run the same regression toolkit against *your* outcome data — foot traffic, admissions, sales, anything correlated with temperature. |

## Why it matters

Temperature is one of the strongest, most predictable drivers of electricity demand — yet the link between "it's going to be hot tomorrow" and "this is what it costs" is rarely made explicit. HeatSignal makes that chain visible and interactive, for two audiences who each make a different decision because of it:

- **Traders & storage operators** get a lead-time signal instead of reacting after a price spike shows up on the market.
- **Households** get a concrete number instead of an abstract warning, plus actions they can actually take.

## How it works

```
FortyGuard Temperature API  ──┐
  (daily avg/min/max, °C)     ├──►  merge on date  ──►  OLS regression  ──►  signal / dollar estimate
EIA Electricity RTO API     ──┘
  (daily demand, MWh)
```

1. **Temperature** — a bounding-box area of interest is queried day-by-day via FortyGuard's `create_heatmap` endpoint.
2. **Demand** — hourly electricity demand for the matching balancing authority is pulled from the EIA Electricity RTO API and aggregated to a daily mean.
3. **Regression** — the two series are merged on date and fit with two models: a simple linear fit, and a cooling-degree-day model that captures the nonlinear jump in AC load once temperatures cross a comfort threshold.
4. **Translation** — the fitted relationship is turned into a trading signal (companies) or a cost estimate (users), live, as you move the slider.

## App tour

- **Home** — hero video, headline stats, and two entry points into the tool.
- **About** — full methodology, both regression models with live coefficients and R², raw `statsmodels` output, and caveats.
- **For Companies** — set a forecast temperature, get a predicted demand shift, a dollar impact, and a buy/sell/store signal, with the underlying regression chart.
- **For Users** — set a hot day's temperature, get an estimated extra cost, a cost-by-temperature table, and practical ways to reduce your bill.
- **Your Data** — upload your own CSV and see how the same toolkit generalizes to other outcome variables.

## Tech stack

- **[Streamlit](https://streamlit.io)** — UI and app framework
- **pandas / numpy** — data handling
- **statsmodels** — OLS regression
- **matplotlib** — regression chart
- **FortyGuard Temperature API** — source of temperature data (see the companion [Colab notebook](fortyguard_starter_colab.ipynb))
- **U.S. EIA Electricity RTO API** — source of electricity demand data

## Project structure

```
heatsignal_dashboard/
├── app.py                          # Main Streamlit app (all pages + styling)
├── requirements.txt                # Python dependencies
├── fortyguard_starter_colab.ipynb  # Notebook used to fetch + merge the dataset
├── assets/
│   └── hero_video.mp4              # Autoplaying hero banner video
└── data/
    ├── merged_data.csv             # Pre-fetched temperature + demand dataset
    └── README.md                   # How this dataset was generated
```

## Getting started

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/heatsignal.git
cd heatsignal

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`. No API keys are required to run the demo — it ships with a pre-fetched dataset (`data/merged_data.csv`).

Want fresh data or a different city? Regenerate it from the [FortyGuard starter notebook](fortyguard_starter_colab.ipynb), export as `merged_data.csv`, and drop it into `data/`.

## Deployment

This app is deployed for judging on **Hugging Face Spaces** (Streamlit SDK), chosen specifically because free Spaces auto-restart on the next visit rather than requiring a manual "wake up" click.

<details>
<summary>Deploy your own copy</summary>

1. Create a new Space at [huggingface.co/new-space](https://huggingface.co/new-space), SDK = **Streamlit**.
2. Push this repo's contents to the Space repo (or connect it via GitHub sync).
3. Hugging Face auto-detects `app.py` and `requirements.txt` — no extra config needed.
4. Your app is live at `https://huggingface.co/spaces/<username>/<space-name>`.

</details>

## Data & methodology

- **Case-study city:** Phoenix, AZ (EIA balancing authority `AZPS`)
- **Window:** June – July 2026, ~45 matched days
- **Model A (linear):** `demand_MWh = β₀ + β₁ · temp_°C`
- **Model B (cooling-degree-days):** `CDD = max(0, temp_°C − threshold)`, threshold = 26°C (≈79°F)

Full derivations, live-fitted coefficients, and raw regression summaries are on the **About** page inside the app.

## Caveats

- Single city, short time window — a production version would fit this per region, continuously.
- The $/MWh price used in the companies view is a rough, user-editable assumption, **not** a live market feed.
- Correlation, not a causal guarantee — temperature is a strong driver of cooling demand, but other seasonal effects aren't controlled for.
- This is a decision-support heuristic, not a trading or billing system.

## Roadmap

- [ ] Multi-city support with per-region regression refitting
- [ ] Live wholesale price feed instead of a fixed assumption
- [ ] Historical accuracy backtest view
- [ ] Investor-facing "opportunity" summary (market size, business case)

## Acknowledgments

- [FortyGuard](https://fortyguard.com) — Temperature API and hackathon
- [U.S. Energy Information Administration (EIA)](https://www.eia.gov/) — Electricity RTO demand data

---

<p align="center">Built for the FortyGuard Hackathon, 2026.</p>
