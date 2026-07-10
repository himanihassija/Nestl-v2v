import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from city_coordinates import CITY_COORDINATES

from simulation import (
    calculate_risk, 
    dashboard_metrics,
    generate_recommendation,
    top_risky_cities,
    predict_next_year
)
from route_planner import (
    geocode_place,
    get_route_alternatives,
    rank_routes
)

# --------------------------------------------------
# THEME STATE  — driven by URL query param set by the nav JS button
# --------------------------------------------------

_qp_theme  = st.query_params.get("theme", "dark")
_is_light  = _qp_theme == "light"
chart_text = "#334155" if _is_light else "#94a3b8"
chart_bg   = "rgba(0,0,0,0)"

# GPS coordinates pushed into the URL by the "Use My Current Location"
# button in the Safe Route Planner section (see bottom of this file).
_qp_user_lat = st.query_params.get("user_lat")
_qp_user_lon = st.query_params.get("user_lon")

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="SHEild AI",
    page_icon="🛡️",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS  — theme variables + sticky nav + transitions
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ═══════════════════════════════════════════
   DARK THEME — default  (:root)
   ═══════════════════════════════════════════ */
:root {
    --bg-start:         #0f172a;
    --bg-end:           #1e293b;
    --text-primary:     #f8fafc;
    --text-secondary:   #94a3b8;
    --chart-text:       #94a3b8;
    --nav-bg:           rgba(15, 23, 42, 0.97);
    --nav-border:       rgba(255, 255, 255, 0.09);
    --nav-link:         #94a3b8;
    --nav-link-hover:   rgba(255, 255, 255, 0.07);
    --card-bg:          rgba(255, 255, 255, 0.05);
    --card-border:      rgba(255, 255, 255, 0.10);
    --sidebar-start:    #1e293b;
    --sidebar-end:      #0f172a;
    --toggle-bg:        rgba(255, 255, 255, 0.08);
    --toggle-border:    rgba(255, 255, 255, 0.15);
    --toggle-color:     #94a3b8;
    --divider-color:    rgba(255, 255, 255, 0.10);
}

/* ═══════════════════════════════════════════
   LIGHT THEME  (:root.light-theme)
   ═══════════════════════════════════════════ */
:root.light-theme {
    --bg-start:         #f8fafc;
    --bg-end:           #e2e8f0;
    --text-primary:     #0f172a;
    --text-secondary:   #475569;
    --chart-text:       #1e293b;
    --nav-bg:           rgba(248, 250, 252, 0.97);
    --nav-border:       rgba(15, 23, 42, 0.09);
    --nav-link:         #475569;
    --nav-link-hover:   rgba(15, 23, 42, 0.07);
    --card-bg:          rgba(15, 23, 42, 0.04);
    --card-border:      rgba(15, 23, 42, 0.09);
    --sidebar-start:    #f1f5f9;
    --sidebar-end:      #e2e8f0;
    --toggle-bg:        rgba(15, 23, 42, 0.07);
    --toggle-border:    rgba(15, 23, 42, 0.14);
    --toggle-color:     #475569;
    --divider-color:    rgba(15, 23, 42, 0.10);
}

/* ═══════════════════════════════════════════
   SMOOTH TRANSITION ON EVERY ELEMENT
   ═══════════════════════════════════════════ */
*, *::before, *::after {
    transition:
        background      0.50s ease,
        background-color 0.50s ease,
        color           0.45s ease,
        border-color    0.45s ease,
        box-shadow      0.45s ease !important;
}

/* ── globals ── */
html { scroll-behavior: smooth; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── hide Streamlit's own header ── */
[data-testid="stHeader"] { display: none !important; }

/* ── main background ── */
.stApp,
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, var(--bg-start) 0%, var(--bg-end) 100%) !important;
}
.main { background: transparent !important; }

/* ── text colours ── */
h1, h2, h3, h4, h5, h6 { color: var(--text-primary) !important; }
p, li, label, .stMarkdown p, .stMarkdown li { color: var(--text-primary) !important; }

/* ── sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--sidebar-start) 0%, var(--sidebar-end) 100%) !important;
    top: 56px !important;
    height: calc(100vh - 56px) !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span { color: var(--text-primary) !important; }

/* ── metric cards ── */
div[data-testid="metric-container"] {
    background:    var(--card-bg)     !important;
    border: 1px solid var(--card-border) !important;
    padding: 18px;
    border-radius: 16px;
    backdrop-filter: blur(10px);
}
div[data-testid="metric-container"] label,
div[data-testid="metric-container"] div { color: var(--text-secondary) !important; }

/* ── dividers ── */
hr { border-color: var(--divider-color) !important; }

/* ══════════════════════════════════════════════
   PLOTLY CHART TEXT — theme-aware
   Works whether charts are in main DOM or same-origin iframes.
   The JS block also injects a stylesheet into every iframe.
   ══════════════════════════════════════════════ */
.js-plotly-plot text,
.svg-container text,
.plotly text {
    fill: var(--chart-text) !important;
    transition: fill 0.45s ease !important;
}

/* ══════════════════════════════════════════════
   DROPDOWN / SELECT / POPOVER — text visibility
   ══════════════════════════════════════════════ */

/* Select trigger box */
[data-baseweb="select"] > div {
    background: var(--card-bg)     !important;
    border-color: var(--card-border) !important;
    color: var(--text-primary)     !important;
}
/* Selected value text */
[data-baseweb="select"] [data-testid="stSelectboxVirtualDropdown"],
[data-baseweb="select"] span,
[data-baseweb="select"] input {
    color: var(--text-primary) !important;
}
/* Dropdown popover container */
[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: var(--sidebar-start) !important;
    border: 1px solid var(--card-border) !important;
}
/* Individual option rows */
[data-baseweb="menu"] [role="option"],
[data-baseweb="menu"] li,
[data-baseweb="menu"] li span,
[data-baseweb="list"] li,
[data-baseweb="list"] li span {
    background: transparent !important;
    color: var(--text-primary) !important;
}
/* Hover state for option rows */
[data-baseweb="menu"] [role="option"]:hover,
[data-baseweb="list"] li:hover {
    background: var(--nav-link-hover) !important;
    color: var(--text-primary) !important;
}
/* Highlighted / selected option */
[data-baseweb="menu"] [aria-selected="true"],
[data-baseweb="menu"] [data-highlighted="true"] {
    background: rgba(244, 63, 94, 0.12) !important;
    color: #f43f5e !important;
}
/* Multiselect tags */
[data-baseweb="tag"] {
    background: rgba(244, 63, 94, 0.15) !important;
    color: var(--text-primary) !important;
}
/* Radio buttons */
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label,
[data-testid="stToggle"] label { color: var(--text-primary) !important; }

/* ═══════════════════════════════════════════
   STICKY NAVIGATION BAR
   ═══════════════════════════════════════════ */
.sheild-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 999999;
    background:    var(--nav-bg)     !important;
    border-bottom: 1px solid var(--nav-border) !important;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    display: flex;
    align-items: center;
    gap: 2px;
    padding: 0 20px;
    height: 56px;
    box-sizing: border-box;
    box-shadow: 0 4px 32px rgba(0, 0, 0, 0.5);
}

.sheild-nav-brand {
    font-size: 1rem;
    font-weight: 700;
    color: #f43f5e !important;
    letter-spacing: -0.3px;
    padding-right: 20px;
    border-right: 1px solid var(--nav-border);
    margin-right: 8px;
    white-space: nowrap;
    flex-shrink: 0;
}

.sheild-nav a {
    color: var(--nav-link) !important;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 8px;
    white-space: nowrap;
    border-bottom: 2px solid transparent;
    display: inline-block;
}
.sheild-nav a:hover {
    color: var(--text-primary) !important;
    background: var(--nav-link-hover) !important;
    border-bottom-color: rgba(244, 63, 94, 0.45);
}

/* Theme toggle button — injected into nav by JS */
#theme-toggle-btn {
    margin-left: auto;
    background: var(--toggle-bg);
    border: 1px solid var(--toggle-border);
    color: var(--toggle-color);
    width: 38px; height: 38px;
    border-radius: 10px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    padding: 0;
}
#theme-toggle-btn:hover {
    background: var(--nav-link-hover);
    border-color: rgba(244, 63, 94, 0.4);
    color: var(--text-primary);
}
#theme-toggle-btn svg { width: 17px; height: 17px; stroke: currentColor; }

/* ── section anchors ── */
.section-anchor {
    display: block;
    height: 0;
    visibility: hidden;
    scroll-margin-top: 72px;
}

/* ── push content below nav ── */
.block-container {
    padding-top:    72px !important;
    padding-bottom: 40px !important;
}

/* ── badge styles ── */
.risk-badge-high {
    background: linear-gradient(135deg, #ef4444, #b91c1c);
    color: white; padding: 4px 12px; border-radius: 20px;
    font-weight: 600; font-size: 0.8rem;
}
.risk-badge-medium {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white; padding: 4px 12px; border-radius: 20px;
    font-weight: 600; font-size: 0.8rem;
}
.risk-badge-low {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white; padding: 4px 12px; border-radius: 20px;
    font-weight: 600; font-size: 0.8rem;
}
.ut-card {
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 12px; padding: 16px; margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# STICKY NAVIGATION HTML
# --------------------------------------------------

st.markdown("""
<nav class="sheild-nav" id="sheild-nav">
  <span class="sheild-nav-brand">🛡️ SHEild AI</span>
  <a href="#sec-city">City Dashboard</a>
  <a href="#sec-map">Risk Map</a>
  <a href="#sec-analytics">Analytics</a>
  <a href="#sec-children">Children &amp; UT Focus</a>
  <a href="#sec-advisor">Safety Advisor</a>
  <a href="#sec-route">Safe Route</a>
</nav>
""", unsafe_allow_html=True)

# --------------------------------------------------
# THEME TOGGLE BUTTON
# Runs inside a sandboxed iframe (st.components.v1.html).
# Uses window.parent to access and modify the Streamlit
# app's top-level document — works on localhost (same origin).
# A MutationObserver re-injects the button if Streamlit
# re-renders the nav on widget interaction.
# --------------------------------------------------

# Determine theme string for JS injection
_theme_js = "light" if _is_light else "dark"

components.html(f"""
<script>
(function () {{
    var SUN  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';
    var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';

    /* ── Apply Python-driven theme class immediately on every render ── */
    var pd = window.parent.document;
    if ("{_theme_js}" === "light") {{
        pd.documentElement.classList.add("light-theme");
    }} else {{
        pd.documentElement.classList.remove("light-theme");
    }}

    /* ─────────────────────────────────────────────
       applyChartFonts — injects a <style> into every same-origin
       Plotly iframe so SVG text elements get the right fill color.
       Falls back silently for any cross-origin frame.
       Also updates any Plotly text living directly in the main DOM.
    ───────────────────────────────────────────── */
    function applyChartFonts(isLight) {{
        var col = isLight ? '#1e293b' : '#94a3b8';
        var css = 'text{{fill:' + col + '!important;transition:fill 0.45s ease!important}}';

        /* 1. Main-DOM Plotly elements */
        pd.querySelectorAll('.js-plotly-plot text, .svg-container text, .plotly text').forEach(function(el) {{
            el.style.setProperty('fill', col, 'important');
        }});

        /* 2. Any same-origin iframe that contains Plotly SVG */
        pd.querySelectorAll('iframe').forEach(function(f) {{
            try {{
                var doc = f.contentDocument;
                if (!doc || !doc.body) return;
                if (!doc.querySelector('text')) return;   /* not a chart iframe */
                /* Inject / update a persistent <style> tag */
                var s = doc.getElementById('_sheild_ct');
                if (!s) {{
                    s = doc.createElement('style');
                    s.id = '_sheild_ct';
                    (doc.head || doc.documentElement).appendChild(s);
                }}
                s.textContent = css;
                /* Also forcibly set fill on every text node that exists now */
                doc.querySelectorAll('text').forEach(function(t) {{
                    t.style.setProperty('fill', col, 'important');
                }});
            }} catch(e) {{ /* cross-origin — ignore */ }}
        }});
    }}

    /* Run immediately, then keep re-applying every second so new charts pick it up */
    applyChartFonts("{_theme_js}" === "light");
    setInterval(function () {{
        applyChartFonts(pd.documentElement.classList.contains('light-theme'));
    }}, 1000);

    function setBtn(btn, isLight) {{
        btn.innerHTML = isLight ? MOON : SUN;
        btn.title = isLight ? 'Switch to dark mode' : 'Switch to light mode';
        btn.setAttribute('aria-label', btn.title);
    }}

    function inject() {{
        var nav = pd.getElementById('sheild-nav');
        if (!nav) {{ setTimeout(inject, 200); return; }}
        if (pd.getElementById('theme-toggle-btn')) return;

        var isLight = pd.documentElement.classList.contains('light-theme');

        var btn = pd.createElement('button');
        btn.id = 'theme-toggle-btn';
        setBtn(btn, isLight);

        btn.addEventListener('click', function () {{
            var light = pd.documentElement.classList.toggle('light-theme');
            setBtn(btn, light);
            /* Apply chart fonts immediately — no page reload needed */
            applyChartFonts(light);
        }});

        nav.appendChild(btn);
    }}

    inject();

    /* Re-inject if Streamlit re-renders and removes the button */
    var observer = new pd.defaultView.MutationObserver(function () {{
        if (pd.getElementById('sheild-nav') && !pd.getElementById('theme-toggle-btn')) {{
            inject();
        }}
    }});
    observer.observe(pd.body, {{ childList: true, subtree: false }});
}})();
</script>
""", height=0)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🛡️ SHEild AI")
st.subheader("AI-Powered Women & Children Safety Intelligence Platform")

st.markdown("""
Comprehensive safety intelligence built on **NCRB Crime in India** data —
covering **States**, **Union Territories**, and **District-level** breakdowns.""")

st.divider()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:
    df = pd.read_csv("women_safety_dataset.csv")
except FileNotFoundError:
    st.error("Dataset not found. Ensure 'women_safety_dataset.csv' is in the project root.")
    st.stop()

REQUIRED = ["city", "state_ut", "territory_type", "district",
            "cases_2021", "cases_2022", "cases_2023",
            "population_lakhs", "crime_rate_2023", "chargesheet_rate",
            "children_cases_2023", "pocso_2023", "kidnapping_children_2023"]
missing = [c for c in REQUIRED if c not in df.columns]
if missing:
    st.error(f"Missing columns in dataset: {missing}")
    st.stop()

df = df[df["city"].str.upper() != "TOTAL 34 CITIES"].copy()

# --------------------------------------------------
# ADD COORDINATES
# --------------------------------------------------

coords = pd.DataFrame(
    [(city, lat, lon) for city, (lat, lon) in CITY_COORDINATES.items()],
    columns=["city", "lat", "lon"]
)
df = df.merge(coords, on="city", how="left")

missing_coords = df[df["lat"].isna()]["city"].tolist()
if missing_coords:
    st.warning(f"Missing coordinates for: {missing_coords}")

# --------------------------------------------------
# CALCULATE RISK
# --------------------------------------------------

df = calculate_risk(df)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🛡️ SHEild AI")

st.sidebar.info("""
**AI-Powered Safety Intelligence**

Data Source: NCRB Crime in India
Coverage: 2021 – 2023
Scope: States + All Union Territories
Includes: Crimes against Children
""")

st.sidebar.markdown("---")

territory_filter = st.sidebar.multiselect(
    "Filter by Territory Type",
    options=["State", "Union Territory"],
    default=["State", "Union Territory"]
)

df_filtered = df[df["territory_type"].isin(territory_filter)].copy()

all_uts = sorted(df_filtered["state_ut"].unique())
selected_ut = st.sidebar.selectbox("Filter by State/UT", ["All"] + all_uts)

if selected_ut != "All":
    df_display = df_filtered[df_filtered["state_ut"] == selected_ut].copy()
else:
    df_display = df_filtered.copy()

selected_city = st.sidebar.selectbox(
    "Select a City/District",
    sorted(df_display["city"].unique())
)

city_data = df[df["city"] == selected_city]

st.sidebar.markdown("---")
st.sidebar.markdown("**Data Source:** NCRB – Crime Against Women & Children in Metropolitan Cities and Union Territories (2021–2023).")

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.header("Dashboard Overview")

metrics = dashboard_metrics(df_display)
ut_count = df_display[df_display["territory_type"] == "Union Territory"]["state_ut"].nunique()
children_total = int(df_display["children_cases_2023"].sum())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Locations", metrics["total_cities"])
c2.metric("UTs Covered", ut_count)
c3.metric("Highest Risk", metrics["highest_risk_city"])
c4.metric("High Risk Zones", metrics["high_risk"])
c5.metric("Children Cases (2023)", f"{children_total:,}")

st.divider()

# ==========================================================
# SECTION 1 – CITY DASHBOARD
# ==========================================================

st.markdown('<div id="sec-city" class="section-anchor"></div>', unsafe_allow_html=True)

st.header("City Dashboard")
st.subheader(f"Location: {selected_city}")

if not city_data.empty:
    row = city_data.iloc[0]
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Cases (2023)", f"{int(row['cases_2023']):,}")
    col2.metric("Crime Rate (per lakh)", round(float(row["crime_rate_2023"]), 1))
    col3.metric("Risk Score", round(float(row["risk_score"]), 2))
    col4.metric("Safety Score", f"{round(float(row['safety_score']), 1)}/100")

    st.markdown("---")

    info_col, trend_col = st.columns([1, 2])

    with info_col:
        st.markdown(f"""
**Location Details**
- **State / UT:** {row['state_ut']}
- **Territory Type:** {row['territory_type']}
- **District:** {row['district']}
- **Population:** {row['population_lakhs']} lakh
- **Chargesheet Rate:** {row['chargesheet_rate']}%

**Risk Classification**
- **Risk Level:** {row['risk_level']}
- **Predicted 2024 Cases:** {predict_next_year(row):,}

**Children Safety (2023)**
- **Total Cases:** {int(row['children_cases_2023']):,}
- **POCSO Cases:** {int(row['pocso_2023']):,}
- **Kidnapping:** {int(row['kidnapping_children_2023']):,}
""")

    with trend_col:
        trend_df = pd.DataFrame({
            "Year": ["2021", "2022", "2023"],
            "Women Cases": [
                int(row["cases_2021"]),
                int(row["cases_2022"]),
                int(row["cases_2023"])
            ],
            "Children Cases": [
                int(row["children_cases_2021"]),
                int(row["children_cases_2022"]),
                int(row["children_cases_2023"])
            ]
        })

        trend_fig = go.Figure()
        trend_fig.add_trace(go.Scatter(
            x=trend_df["Year"], y=trend_df["Women Cases"],
            mode="lines+markers", name="Women Cases",
            line=dict(color="#f43f5e", width=3),
            marker=dict(size=10)
        ))
        trend_fig.add_trace(go.Scatter(
            x=trend_df["Year"], y=trend_df["Children Cases"],
            mode="lines+markers", name="Children Cases",
            line=dict(color="#8b5cf6", width=3),
            marker=dict(size=10)
        ))
        trend_fig.update_layout(
            title=f"Crime Trend — {selected_city}",
            xaxis_title="Year",
            yaxis_title="Reported Cases",
            plot_bgcolor=chart_bg,
            paper_bgcolor=chart_bg,
            font=dict(color=chart_text),
            legend=dict(bgcolor=chart_bg)
        )
        st.plotly_chart(trend_fig, use_container_width=True)

    risk = row["risk_level"]
    if risk == "High":
        st.error(f"""
### High Risk Zone
**{selected_city}** ({row['district']} district, {row['state_ut']}) shows elevated crime indicators.
- High volume of reported cases relative to population
- Crime rate significantly above average
- Worsening or high trend over 2021–2023
""")
    elif risk == "Medium":
        st.warning(f"""
### Medium Risk Zone
**{selected_city}** has moderate safety concerns. Exercise standard precautions.
""")
    else:
        st.success(f"""
### Lower Risk Zone
**{selected_city}** shows comparatively lower crime indicators. Basic safety practices remain important.
""")
else:
    st.error("City data not found.")

st.divider()

# ==========================================================
# SECTION 2 – RISK MAP
# ==========================================================

st.markdown('<div id="sec-map" class="section-anchor"></div>', unsafe_allow_html=True)

st.header("Risk Map")
st.subheader("Women Safety Risk Map — India")

map_df = df_display.dropna(subset=["lat", "lon"])

col_map1, col_map2 = st.columns([3, 1])

with col_map1:
    map_view = st.radio(
        "Colour by", ["Risk Level", "Territory Type"], horizontal=True
    )

if map_view == "Risk Level":
    color_col = "risk_level"
    color_map = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"}
else:
    color_col = "territory_type"
    color_map = {"State": "#3b82f6", "Union Territory": "#a855f7"}

map_fig = px.scatter_map(
    map_df,
    lat="lat",
    lon="lon",
    hover_name="city",
    hover_data={
        "state_ut": True,
        "territory_type": True,
        "district": True,
        "risk_level": True,
        "risk_score": ":.2f",
        "cases_2023": True,
        "children_cases_2023": True,
        "crime_rate_2023": True,
        "lat": False,
        "lon": False
    },
    color=color_col,
    size="cases_2023",
    size_max=30,
    zoom=4,
    height=650,
    color_discrete_map=color_map
)
map_fig.update_layout(
    map_style="carto-darkmatter",
    margin=dict(l=0, r=0, t=0, b=0)
)
st.plotly_chart(map_fig, use_container_width=True)

st.caption("Bubble size = total women cases (2023) | Colour = risk level or territory type")

st.divider()

# ==========================================================
# SECTION 3 – ANALYTICS
# ==========================================================

st.markdown('<div id="sec-analytics" class="section-anchor"></div>', unsafe_allow_html=True)

st.header("Analytics Dashboard")

a1, a2 = st.columns(2)

with a1:
    st.subheader("Top 10 Highest Risk Locations")
    top10 = df_display.sort_values("risk_score", ascending=False).head(10)[
        ["city", "state_ut", "territory_type", "district", "risk_level", "risk_score", "cases_2023", "crime_rate_2023"]
    ]
    st.dataframe(top10, use_container_width=True, hide_index=True)

with a2:
    st.subheader("Top 10 Safest Locations")
    bot10 = df_display.sort_values("risk_score").head(10)[
        ["city", "state_ut", "territory_type", "district", "risk_level", "safety_score", "cases_2023"]
    ]
    st.dataframe(bot10, use_container_width=True, hide_index=True)

st.markdown("---")

bar_col, pie_col = st.columns(2)

with bar_col:
    st.subheader("Risk Score by Location")
    top15 = df_display.sort_values("risk_score", ascending=False).head(15)
    bar = px.bar(
        top15,
        x="city",
        y="risk_score",
        color="risk_level",
        title="Top 15 Locations by Risk Score",
        color_discrete_map={"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"},
        hover_data=["state_ut", "territory_type", "district"]
    )
    bar.update_layout(
        plot_bgcolor=chart_bg,
        paper_bgcolor=chart_bg,
        font=dict(color=chart_text),
        xaxis_tickangle=-45
    )
    st.plotly_chart(bar, use_container_width=True)

with pie_col:
    st.subheader("Risk Distribution")
    pie = px.pie(
        df_display,
        names="risk_level",
        title="Risk Category Distribution",
        color="risk_level",
        color_discrete_map={"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"},
        hole=0.4
    )
    pie.update_layout(
        plot_bgcolor=chart_bg,
        paper_bgcolor=chart_bg,
        font=dict(color=chart_text)
    )
    st.plotly_chart(pie, use_container_width=True)

st.markdown("---")
st.subheader("State / UT Summary")

ut_summary = df_display.groupby(["state_ut", "territory_type"]).agg(
    Locations=("city", "count"),
    Total_Women_Cases_2023=("cases_2023", "sum"),
    Total_Children_Cases_2023=("children_cases_2023", "sum"),
    Avg_Crime_Rate=("crime_rate_2023", "mean"),
    High_Risk_Zones=("risk_level", lambda x: (x == "High").sum())
).reset_index().round(1)
ut_summary.columns = [
    "State/UT", "Territory Type", "Locations",
    "Women Cases (2023)", "Children Cases (2023)",
    "Avg Crime Rate", "High Risk Zones"
]
ut_summary = ut_summary.sort_values("Women Cases (2023)", ascending=False)
st.dataframe(ut_summary, use_container_width=True, hide_index=True)

st.divider()

# ==========================================================
# SECTION 4 – CHILDREN & UT FOCUS
# ==========================================================

st.markdown('<div id="sec-children" class="section-anchor"></div>', unsafe_allow_html=True)

st.header("Children Safety & Union Territory Deep Dive")

st.info("""
**National Context (NCRB 2023)**
India registered **1,77,335** crimes against children in 2023 (+9.2% from 2022).
Major categories: **Kidnapping & Abduction** (79,884 cases, 45%) · **POCSO Act** (67,694 cases, 38%)
""")

st.markdown("---")
st.subheader("Union Territories — Complete Overview")

ut_df = df[df["territory_type"] == "Union Territory"].copy()

ut_cols = st.columns(4)
ut_cols[0].metric("UT Locations", len(ut_df))
ut_cols[1].metric("Total UT Women Cases (2023)", f"{int(ut_df['cases_2023'].sum()):,}")
ut_cols[2].metric("Total UT Children Cases (2023)", f"{int(ut_df['children_cases_2023'].sum()):,}")
ut_cols[3].metric("UT High Risk Zones", int((ut_df["risk_level"] == "High").sum()))

st.markdown("---")

st.subheader("All Union Territory Districts — Crime Data")
ut_table = ut_df[[
    "city", "state_ut", "district", "cases_2021", "cases_2022", "cases_2023",
    "crime_rate_2023", "children_cases_2023", "pocso_2023",
    "kidnapping_children_2023", "risk_level", "safety_score"
]].sort_values("cases_2023", ascending=False).copy()

ut_table.columns = [
    "City/Town", "Union Territory", "District",
    "Women Cases 2021", "Women Cases 2022", "Women Cases 2023",
    "Crime Rate (per lakh)", "Children Cases 2023",
    "POCSO Cases 2023", "Children Kidnapping 2023",
    "Risk Level", "Safety Score"
]
st.dataframe(ut_table, use_container_width=True, hide_index=True)

st.markdown("---")

ch1, ch2 = st.columns(2)

with ch1:
    st.subheader("Women Cases by Union Territory (2023)")
    ut_agg = ut_df.groupby("state_ut").agg(
        Women_Cases=("cases_2023", "sum"),
        Children_Cases=("children_cases_2023", "sum"),
        POCSO=("pocso_2023", "sum"),
        Locations=("city", "count")
    ).reset_index().sort_values("Women_Cases", ascending=True)

    bar_ut = px.bar(
        ut_agg,
        x="Women_Cases",
        y="state_ut",
        orientation="h",
        color="Women_Cases",
        color_continuous_scale="Reds",
        title="Total Reported Women Cases by UT (2023)",
        labels={"Women_Cases": "Cases", "state_ut": "Union Territory"}
    )
    bar_ut.update_layout(
        plot_bgcolor=chart_bg,
        paper_bgcolor=chart_bg,
        font=dict(color=chart_text),
        coloraxis_showscale=False
    )
    st.plotly_chart(bar_ut, use_container_width=True)

with ch2:
    st.subheader("Children Crime Breakdown by UT (2023)")
    ut_children = ut_df.groupby("state_ut").agg(
        POCSO=("pocso_2023", "sum"),
        Kidnapping=("kidnapping_children_2023", "sum")
    ).reset_index()

    fig_children = go.Figure()
    fig_children.add_trace(go.Bar(
        name="POCSO Cases",
        x=ut_children["state_ut"],
        y=ut_children["POCSO"],
        marker_color="#a855f7"
    ))
    fig_children.add_trace(go.Bar(
        name="Kidnapping",
        x=ut_children["state_ut"],
        y=ut_children["Kidnapping"],
        marker_color="#f43f5e"
    ))
    fig_children.update_layout(
        barmode="group",
        title="Children Crime by UT — POCSO vs Kidnapping (2023)",
        plot_bgcolor=chart_bg,
        paper_bgcolor=chart_bg,
        font=dict(color=chart_text),
        xaxis_tickangle=-30
    )
    st.plotly_chart(fig_children, use_container_width=True)

st.markdown("---")
st.subheader("Delhi Districts — Detailed Breakdown")

delhi_df = df[df["state_ut"] == "Delhi"].sort_values("cases_2023", ascending=False)

dl1, dl2 = st.columns(2)

with dl1:
    delhi_bar = px.bar(
        delhi_df,
        x="city",
        y="cases_2023",
        color="risk_level",
        title="Delhi Districts — Women Cases (2023)",
        color_discrete_map={"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"},
        hover_data=["district", "crime_rate_2023", "children_cases_2023"]
    )
    delhi_bar.update_layout(
        plot_bgcolor=chart_bg,
        paper_bgcolor=chart_bg,
        font=dict(color=chart_text),
        xaxis_tickangle=-35
    )
    st.plotly_chart(delhi_bar, use_container_width=True)

with dl2:
    delhi_children = px.bar(
        delhi_df,
        x="city",
        y=["pocso_2023", "kidnapping_children_2023"],
        title="Delhi Districts — Children Crime (2023)",
        barmode="group",
        color_discrete_map={
            "pocso_2023": "#a855f7",
            "kidnapping_children_2023": "#f43f5e"
        },
        labels={
            "value": "Cases",
            "variable": "Crime Type",
            "pocso_2023": "POCSO",
            "kidnapping_children_2023": "Kidnapping"
        }
    )
    delhi_children.update_layout(
        plot_bgcolor=chart_bg,
        paper_bgcolor=chart_bg,
        font=dict(color=chart_text),
        xaxis_tickangle=-35
    )
    st.plotly_chart(delhi_children, use_container_width=True)

st.markdown("---")
st.subheader("Jammu & Kashmir — District Breakdown")

jk_df = df[df["state_ut"] == "Jammu & Kashmir"].sort_values("cases_2023", ascending=False)
jk_table = jk_df[[
    "city", "district", "cases_2021", "cases_2022", "cases_2023",
    "crime_rate_2023", "children_cases_2023", "pocso_2023",
    "kidnapping_children_2023", "risk_level"
]].copy()
jk_table.columns = [
    "City/Town", "District", "Women 2021", "Women 2022", "Women 2023",
    "Crime Rate", "Children 2023", "POCSO", "Kidnapping", "Risk"
]
st.dataframe(jk_table, use_container_width=True, hide_index=True)

jk_fig = px.bar(
    jk_df,
    x="city",
    y="cases_2023",
    color="risk_level",
    title="J&K Districts — Women Cases (2023)",
    color_discrete_map={"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"},
    hover_data=["district", "crime_rate_2023"]
)
jk_fig.update_layout(
    plot_bgcolor=chart_bg,
    paper_bgcolor=chart_bg,
    font=dict(color=chart_text),
    xaxis_tickangle=-45
)
st.plotly_chart(jk_fig, use_container_width=True)

st.divider()

# ==========================================================
# SECTION 5 – SAFETY ADVISOR
# ==========================================================

st.markdown('<div id="sec-advisor" class="section-anchor"></div>', unsafe_allow_html=True)

st.header("Safety Advisor")
st.subheader(f"Assessment for: {selected_city}")

if not city_data.empty:
    row = city_data.iloc[0]
    risk = row["risk_level"]
    score = round(float(row["risk_score"]), 2)
    safety = round(float(row["safety_score"]), 1)

    adv_col1, adv_col2 = st.columns([1, 2])

    with adv_col1:
        st.metric("Risk Score", score)
        st.metric("Safety Score", f"{safety}/100")
        st.metric("Predicted Cases (2024)", f"{predict_next_year(row):,}")
        st.metric("Children Cases (2023)", f"{int(row['children_cases_2023']):,}")

    with adv_col2:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=safety,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Safety Score", "font": {"color": chart_text}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": chart_text},
                "bar": {"color": "#10b981" if risk == "Low" else "#f59e0b" if risk == "Medium" else "#ef4444"},
                "steps": [
                    {"range": [0, 33], "color": "rgba(239,68,68,0.15)"},
                    {"range": [33, 66], "color": "rgba(245,158,11,0.15)"},
                    {"range": [66, 100], "color": "rgba(16,185,129,0.15)"}
                ],
                "threshold": {
                    "line": {"color": chart_text, "width": 2},
                    "thickness": 0.75,
                    "value": safety
                },
                "bgcolor": chart_bg
            },
            number={"font": {"color": chart_text}}
        ))
        gauge.update_layout(
            paper_bgcolor=chart_bg,
            height=220,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(gauge, use_container_width=True)

    st.markdown("---")

    if risk == "High":
        st.error(f"""
### High Risk Assessment
**{selected_city}** ({row['district']}, {row['state_ut']}) is in the **HIGH RISK** category.

**Observed Indicators:**
- Crime volume: **{int(row['cases_2023']):,} reported cases in 2023**
- Crime rate: **{row['crime_rate_2023']} per lakh population** (national avg: 66.2)
- Crime trend: {"Increasing" if row['cases_2023'] > row['cases_2021'] else "Declining"}
- Children at risk: **{int(row['children_cases_2023']):,} cases** including {int(row['pocso_2023'])} POCSO
""")
    elif risk == "Medium":
        st.warning(f"""
### Medium Risk Assessment
**{selected_city}** has moderate safety concerns. Stay aware and take standard precautions.

- Cases 2023: **{int(row['cases_2023']):,}**
- Crime rate: **{row['crime_rate_2023']}** per lakh population
""")
    else:
        st.success(f"""
### Lower Risk Zone
**{selected_city}** shows comparatively lower crime indicators based on NCRB 2023 data.

- Cases 2023: **{int(row['cases_2023']):,}**
- Safety Score: **{safety}/100**
""")

    st.subheader("Safety Recommendations")
    recommendations = generate_recommendation(risk)
    for rec in recommendations:
        st.write(rec)


else:
    st.error("City data not found.")

st.divider()

# ==========================================================
# SECTION 6 – SAFE ROUTE PLANNER
# ==========================================================

st.markdown('<div id="sec-route" class="section-anchor"></div>', unsafe_allow_html=True)

st.header("Safe Route Planner")
st.subheader("Point A → Point B, weighted by NCRB crime data")

st.info("""
**How this works:** like Google Maps' shortest-path routing, this pulls real road-network
routes between your two points (via OpenStreetMap's OSRM routing engine) — but instead of
ranking them purely by distance/time, each alternative is also scored by how close it passes
to higher-crime cities in this project's 34-city NCRB dataset. Use the slider below to weigh
**Fastest** vs **Safest**.

⚠️ **Data granularity note:** the NCRB data used here is reported at the **city/district
level** (annual aggregate counts), not per street or per road. "Safest route" therefore means
*stays further from higher-crime cities/districts along the way* — not a block-by-block safety
score.
""")

covered_cities = sorted(CITY_COORDINATES.keys())

# --------------------------------------------------
# "USE MY LOCATION" BUTTON
# Uses the browser's Geolocation API, then writes lat/lon into the
# URL's query params (same pattern the theme toggle uses to talk to
# the parent Streamlit page) so Python can read it back after rerun.
# --------------------------------------------------

components.html("""
<div style="margin-bottom:10px;">
  <button id="gps-btn" style="
      background:#f43f5e; color:white; border:none; border-radius:8px;
      padding:8px 16px; font-family:Inter,sans-serif; font-size:0.85rem;
      font-weight:600; cursor:pointer;">
      📍 Use My Current Location as Start Point
  </button>
</div>
<script>
document.getElementById('gps-btn').addEventListener('click', function () {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by this browser.');
        return;
    }
    navigator.geolocation.getCurrentPosition(function (pos) {
        var lat = pos.coords.latitude.toFixed(6);
        var lon = pos.coords.longitude.toFixed(6);
        var url = new URL(window.parent.location.href);
        url.searchParams.set('user_lat', lat);
        url.searchParams.set('user_lon', lon);
        window.parent.location.href = url.toString();
    }, function (err) {
        alert('Could not get your location: ' + err.message);
    });
});
</script>
""", height=55)

if _qp_user_lat and _qp_user_lon:
    st.success(
        f"📍 Using your current GPS location as the start point: "
        f"({float(_qp_user_lat):.4f}, {float(_qp_user_lon):.4f})"
    )

route_col1, route_col2 = st.columns(2)

with route_col1:
    st.markdown("**Start Point**")
    origin_mode = st.radio(
        "Origin input",
        ["Use GPS location", "Pick a covered city", "Enter an address"],
        label_visibility="collapsed",
        index=0 if (_qp_user_lat and _qp_user_lon) else 1,
        key="origin_mode"
    )
    origin_city_pick = None
    origin_address = None
    if origin_mode == "Pick a covered city":
        origin_city_pick = st.selectbox("From city", covered_cities, key="origin_city")
    elif origin_mode == "Enter an address":
        origin_address = st.text_input(
            "From address", placeholder="e.g. Connaught Place, Delhi", key="origin_addr"
        )

with route_col2:
    st.markdown("**Destination**")
    dest_mode = st.radio(
        "Destination input",
        ["Pick a covered city", "Enter an address"],
        label_visibility="collapsed",
        key="dest_mode"
    )
    dest_city_pick = None
    dest_address = None
    if dest_mode == "Pick a covered city":
        dest_city_pick = st.selectbox(
            "To city", covered_cities, index=min(1, len(covered_cities) - 1), key="dest_city"
        )
    else:
        dest_address = st.text_input(
            "To address", placeholder="e.g. Gateway of India, Mumbai", key="dest_addr"
        )

safety_weight_pct = st.slider(
    "Priority — Fastest ⟷ Safest",
    min_value=0, max_value=100, value=50, step=10,
    help=(
        "0 = shortest/fastest route regardless of crime data. "
        "100 = prioritize routes that stay furthest from higher-crime cities "
        "and favor better-lit, busier roads."
    )
)
safety_weight = safety_weight_pct / 100

include_lighting = st.checkbox(
    "🔦 Also analyze street lighting & road type (via OpenStreetMap)",
    value=True,
    help=(
        "Checks whether the roads on each route are tagged as lit, and whether "
        "they're major/busy roads vs minor or isolated ones — used as a proxy for "
        "dimly-lit or empty stretches, since crime data alone can't tell us that. "
        "Only works for shorter routes (under ~60km) and needs a live connection "
        "to OpenStreetMap; uncheck for a faster, crime-data-only result."
    )
)

find_route_clicked = st.button("🔍 Find Route", type="primary")

if find_route_clicked:
    # ---- Resolve origin coordinates ----
    origin_coords = None
    if origin_mode == "Use GPS location":
        if _qp_user_lat and _qp_user_lon:
            origin_coords = (float(_qp_user_lat), float(_qp_user_lon))
        else:
            st.error(
                "No GPS location captured yet — click 'Use My Current Location' above "
                "and allow the browser's permission prompt first."
            )
    elif origin_mode == "Pick a covered city":
        origin_coords = CITY_COORDINATES.get(origin_city_pick)
    else:
        with st.spinner(f"Locating '{origin_address}'..."):
            origin_coords = geocode_place(origin_address)
        if origin_coords is None:
            st.error(f"Couldn't find a location for '{origin_address}'. Try a more specific address.")

    # ---- Resolve destination coordinates (biased toward origin, if we have it) ----
    dest_coords = None
    if origin_coords and dest_mode == "Enter an address":
        with st.spinner(f"Locating '{dest_address}'..."):
            dest_coords = geocode_place(dest_address, bias_coords=origin_coords)
        if dest_coords is None:
            st.error(f"Couldn't find a location for '{dest_address}'. Try a more specific address, or check the spelling.")
    elif dest_mode == "Pick a covered city":
        dest_coords = CITY_COORDINATES.get(dest_city_pick)
    else:
        with st.spinner(f"Locating '{dest_address}'..."):
            dest_coords = geocode_place(dest_address)
        if dest_coords is None:
            st.error(f"Couldn't find a location for '{dest_address}'. Try a more specific address, or check the spelling.")

    if origin_coords and dest_coords:
        with st.spinner("Fetching route alternatives from the road network..."):
            raw_routes = get_route_alternatives(origin_coords, dest_coords)

        if not raw_routes:
            st.error("""
Couldn't fetch a route right now. This usually means either:
- the public OSRM routing server is temporarily unavailable, or
- this environment doesn't have outbound internet access.

Try again in a moment, or deploy this app somewhere with normal internet access.
""")
            st.session_state.pop("route_results", None)
        else:
            with st.spinner("Scoring routes against NCRB data" + (" and street-level features..." if include_lighting else "...")):
                ranked = rank_routes(
                    raw_routes, df,
                    safety_weight=safety_weight,
                    include_street_lighting=include_lighting,
                )
            st.session_state["route_results"] = {
                "ranked": ranked,
                "origin_coords": origin_coords,
                "dest_coords": dest_coords,
            }

# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

def _risk_badge(avg_risk):
    """Soft, non-alarming qualitative label for a route's crime-proximity score."""
    if avg_risk < 0.35:
        return "🟢 Low", "#10b981"
    elif avg_risk < 0.65:
        return "🟡 Moderate", "#f59e0b"
    else:
        return "🟠 Elevated", "#f97316"


if "route_results" in st.session_state:
    result = st.session_state["route_results"]
    ranked = result["ranked"]
    origin_coords = result["origin_coords"]
    dest_coords = result["dest_coords"]

    st.markdown("---")
    st.subheader(f"{len(ranked)} Route Alternative(s) Found")

    best = ranked[0]
    tag_str = " · ".join(best.get("tags", [])) or "Recommended"
    badge_label, badge_color = _risk_badge(best["risk_info"]["avg_risk"])

    st.success(f"""
### ✅ Recommended: {tag_str}
**{best.get('road_summary', 'Route')}**
- **Distance:** {best['distance_km']} km
- **Area Crime-Data Signal:** {badge_label}
""")

    lighting = best.get("lighting_info", {})
    if lighting.get("available"):
        lit_txt = f"{lighting['lit_coverage_pct']}% explicitly tagged as lit" if lighting.get("lit_coverage_pct") is not None else "lighting tags not widely available for this area"
        st.caption(
            f"🔦 Street check: **{lighting['major_road_pct']}%** of this route runs along major/busier roads · {lit_txt}. "
            f"(Based on OpenStreetMap tagging — coverage varies by area.)"
        )
    elif include_lighting:
        st.caption("🔦 Street lighting/road-type data wasn't available for this route (route may be too long, or OpenStreetMap didn't respond in time).")

    if best.get("risk_tied_with_alternative"):
        st.caption(
            "⚖️ Note: the top two routes score within 1% of each other overall — "
            "given available data, they're effectively equally safe. The pick above "
            "is the faster of the two near-tied options."
        )

    if best["risk_info"]["nearby_cities"]:
        with st.expander("ℹ️ See the crime-data detail behind this score"):
            if len(best["risk_info"]["nearby_cities"]) == 1:
                only_city = best["risk_info"]["nearby_cities"][0]["city"]
                st.caption(
                    f"**{only_city}** is the only one of the NCRB-covered cities/districts "
                    f"within the 40 km search radius of this route, so it's driving this score."
                )
            near_df = pd.DataFrame(best["risk_info"]["nearby_cities"])
            near_df.columns = ["City", "Distance from Route (km)", "Risk Level", "Risk Score"]
            st.dataframe(near_df, use_container_width=True, hide_index=True)
            st.caption(
                "Reminder: NCRB data here is city/district-level, not street-level — "
                "this reflects the wider area, not the specific road."
            )
    else:
        st.caption("No NCRB-covered city/district falls within reach of this route — crime-data signal is neutral here.")

    # --------------------------------------------------
    # COMPARE ALL ALTERNATIVES — visual cards + chart
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("**Compare All Alternatives**")

    cmp_cols = st.columns(len(ranked))
    for i, (col, r) in enumerate(zip(cmp_cols, ranked)):
        with col:
            badge_label, badge_color = _risk_badge(r["risk_info"]["avg_risk"])
            tags_html = "".join(
                f'<span style="background:#f43f5e;color:white;border-radius:6px;'
                f'padding:2px 8px;font-size:0.75rem;margin-right:4px;">{t}</span>'
                for t in r.get("tags", [])
            )
            st.markdown(f"""
<div style="border:1px solid rgba(148,163,184,0.3); border-radius:12px; padding:14px; height:100%;">
  <div style="margin-bottom:6px;">{tags_html}</div>
  <div style="font-weight:600; font-size:0.95rem; margin-bottom:8px;">{r.get('road_summary', f'Route {i+1}')}</div>
  <div style="font-size:1.4rem; font-weight:700;">{r['distance_km']} km</div>
  <div style="color:{badge_color}; font-weight:600; margin-top:4px;">{badge_label} crime-data signal</div>
</div>
""", unsafe_allow_html=True)
            safety_pct = round((1 - r.get("norm_safety", 0)) * 100)
            st.progress(max(0, min(100, safety_pct)) / 100, text=f"Relative safety: {safety_pct}%")
            lt = r.get("lighting_info", {})
            if lt.get("available"):
                st.caption(f"🔦 {lt['major_road_pct']}% major/busy roads")

    # Grouped bar chart: distance vs. relative safety, side by side
    chart_labels = [r.get("road_summary", f"Route {i+1}")[:28] for i, r in enumerate(ranked)]
    distances = [r["distance_km"] for r in ranked]
    safety_pcts = [round((1 - r.get("norm_safety", 0)) * 100) for r in ranked]

    compare_fig = go.Figure()
    compare_fig.add_trace(go.Bar(
        x=chart_labels, y=distances, name="Distance (km)",
        marker_color="#3b82f6", yaxis="y1"
    ))
    compare_fig.add_trace(go.Bar(
        x=chart_labels, y=safety_pcts, name="Relative Safety (%)",
        marker_color="#10b981", yaxis="y2"
    ))
    compare_fig.update_layout(
        barmode="group",
        yaxis=dict(title="Distance (km)", color=chart_text),
        yaxis2=dict(title="Relative Safety (%)", overlaying="y", side="right",
                     range=[0, 100], color=chart_text),
        xaxis=dict(color=chart_text),
        legend=dict(orientation="h", y=1.15, font=dict(color=chart_text)),
        paper_bgcolor=chart_bg, plot_bgcolor=chart_bg,
        height=380, margin=dict(t=40, b=10)
    )
    st.plotly_chart(compare_fig, use_container_width=True)
    st.caption(
        "Higher **Relative Safety** = lower combined crime-proximity + street-lighting/road-type "
        "signal, compared only among the alternatives shown above — not an absolute safety score."
    )

    # ---- Map ----
    st.markdown("---")
    st.markdown("**Route Map**")

    route_colors = ["#10b981", "#3b82f6", "#f59e0b", "#a855f7"]
    route_map = go.Figure()

    for i, r in enumerate(ranked):
        lats = [c[0] for c in r["coords"]]
        lons = [c[1] for c in r["coords"]]
        label = r.get("road_summary", f"Route {i + 1}") + (f" — {', '.join(r['tags'])}" if r.get("tags") else "")
        route_map.add_trace(go.Scattermap(
            lat=lats, lon=lons, mode="lines",
            line=dict(width=5 if i == 0 else 3, color=route_colors[i % len(route_colors)]),
            opacity=1.0 if i == 0 else 0.55,
            name=label,
            hoverinfo="name"
        ))

    route_map.add_trace(go.Scattermap(
        lat=[origin_coords[0]], lon=[origin_coords[1]],
        mode="markers+text", marker=dict(size=16, color="#10b981"),
        text=["Start"], textposition="top right", name="Start"
    ))
    route_map.add_trace(go.Scattermap(
        lat=[dest_coords[0]], lon=[dest_coords[1]],
        mode="markers+text", marker=dict(size=16, color="#ef4444"),
        text=["Destination"], textposition="top right", name="Destination"
    ))

    risk_color = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"}
    for c in best["risk_info"]["nearby_cities"]:
        city_row = df[df["city"] == c["city"]]
        if city_row.empty:
            continue
        crow = city_row.iloc[0]
        route_map.add_trace(go.Scattermap(
            lat=[crow["lat"]], lon=[crow["lon"]],
            mode="markers",
            marker=dict(size=10, color=risk_color.get(c["risk_level"], "#94a3b8")),
            name=f"{c['city']} ({c['risk_level']} risk)",
            hoverinfo="name"
        ))

    mid_lat = (origin_coords[0] + dest_coords[0]) / 2
    mid_lon = (origin_coords[1] + dest_coords[1]) / 2

    route_map.update_layout(
        map=dict(
            style="carto-darkmatter" if not _is_light else "carto-positron",
            center=dict(lat=mid_lat, lon=mid_lon),
            zoom=9
        ),
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(bgcolor=chart_bg, font=dict(color=chart_text)),
        paper_bgcolor=chart_bg
    )
    st.plotly_chart(route_map, use_container_width=True)

    st.caption(
        "Green route = top recommendation for your chosen Fastest/Safest priority. "
        "Markers show nearby NCRB-covered cities colored by risk level. "
        "Routing via OSRM (OpenStreetMap) · Geocoding via Nominatim (OpenStreetMap)."
    )
