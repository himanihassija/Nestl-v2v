import streamlit as st
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

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="SHEild AI",
    page_icon="🛡️",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
}

h1, h2, h3 {
    color: #f8fafc;
}

div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 18px;
    border-radius: 16px;
    backdrop-filter: blur(10px);
}

.risk-badge-high {
    background: linear-gradient(135deg, #ef4444, #b91c1c);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
}

.risk-badge-medium {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
}

.risk-badge-low {
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.8rem;
}

.ut-card {
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 6px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🛡️ SHEild AI")
st.subheader("AI-Powered Women & Children Safety Intelligence Platform")

st.markdown("""
Comprehensive safety intelligence built on **NCRB Crime in India (2021–2023)** data —
covering **States**, **Union Territories**, and **District-level** breakdowns.

**Aligned with** SDG 5 – Gender Equality &nbsp;|&nbsp; SDG 11 – Sustainable Cities &nbsp;|&nbsp; SDG 16 – Peace & Justice
""")

st.divider()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:
    df = pd.read_csv("women_safety_dataset.csv")
except FileNotFoundError:
    st.error("❌ Dataset not found. Ensure 'women_safety_dataset.csv' is in the project root.")
    st.stop()

# Validate required columns
REQUIRED = ["city", "state_ut", "territory_type", "district",
            "cases_2021", "cases_2022", "cases_2023",
            "population_lakhs", "crime_rate_2023", "chargesheet_rate",
            "children_cases_2023", "pocso_2023", "kidnapping_children_2023"]
missing = [c for c in REQUIRED if c not in df.columns]
if missing:
    st.error(f"❌ Missing columns in dataset: {missing}")
    st.stop()

# Remove TOTAL rows if any
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
    st.warning(f"⚠️ Missing coordinates for: {missing_coords}")

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

📊 Data Source: NCRB Crime in India
🗓️ Coverage: 2021 – 2023
🗺️ Scope: States + All Union Territories
👧 Includes: Crimes against Children
""")

st.sidebar.markdown("---")

# Filter by territory type
territory_filter = st.sidebar.multiselect(
    "Filter by Territory Type",
    options=["State", "Union Territory"],
    default=["State", "Union Territory"]
)

df_filtered = df[df["territory_type"].isin(territory_filter)].copy()

# Filter by state/UT
all_uts = sorted(df_filtered["state_ut"].unique())
selected_ut = st.sidebar.selectbox("Filter by State/UT", ["All"] + all_uts)

if selected_ut != "All":
    df_display = df_filtered[df_filtered["state_ut"] == selected_ut].copy()
else:
    df_display = df_filtered.copy()

# City selector
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

st.header("📊 Dashboard Overview")

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

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 City Dashboard",
    "🗺️ Risk Map",
    "📊 Analytics",
    "👧 Children & UT Focus",
    "🤖 Safety Advisor"
])

# ==========================================================
# TAB 1 – CITY DASHBOARD
# ==========================================================

with tab1:
    st.header(f"📍 {selected_city}")

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
**🏙️ Location Details**
- **State / UT:** {row['state_ut']}
- **Territory Type:** {row['territory_type']}
- **District:** {row['district']}
- **Population:** {row['population_lakhs']} lakh
- **Chargesheet Rate:** {row['chargesheet_rate']}%

**🔍 Risk Classification**
- **Risk Level:** {row['risk_level']}
- **Predicted 2024 Cases:** {predict_next_year(row):,}

**👧 Children Safety (2023)**
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
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
                legend=dict(bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(trend_fig, use_container_width=True)

        # Risk alert
        risk = row["risk_level"]
        if risk == "High":
            st.error(f"""
### 🚨 High Risk Zone
**{selected_city}** ({row['district']} district, {row['state_ut']}) shows elevated crime indicators.
- High volume of reported cases relative to population
- Crime rate significantly above average
- Worsening or high trend over 2021–2023
""")
        elif risk == "Medium":
            st.warning(f"""
### ⚠️ Medium Risk Zone
**{selected_city}** has moderate safety concerns. Exercise standard precautions.
""")
        else:
            st.success(f"""
### ✅ Low Risk Zone
**{selected_city}** shows comparatively lower crime indicators. Basic safety practices remain important.
""")
    else:
        st.error("City data not found.")

# ==========================================================
# TAB 2 – RISK MAP
# ==========================================================

with tab2:
    st.header("🗺️ Women Safety Risk Map — India")

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

    st.caption("📌 Bubble size = total women cases (2023) | Colour = risk level or territory type")

# ==========================================================
# TAB 3 – ANALYTICS
# ==========================================================

with tab3:
    st.header("📊 Analytics Dashboard")

    a1, a2 = st.columns(2)

    with a1:
        st.subheader("🏆 Top 10 Highest Risk Locations")
        top10 = df_display.sort_values("risk_score", ascending=False).head(10)[
            ["city", "state_ut", "territory_type", "district", "risk_level", "risk_score", "cases_2023", "crime_rate_2023"]
        ]
        st.dataframe(top10, use_container_width=True, hide_index=True)

    with a2:
        st.subheader("🕊️ Top 10 Safest Locations")
        bot10 = df_display.sort_values("risk_score").head(10)[
            ["city", "state_ut", "territory_type", "district", "risk_level", "safety_score", "cases_2023"]
        ]
        st.dataframe(bot10, use_container_width=True, hide_index=True)

    st.markdown("---")

    bar_col, pie_col = st.columns(2)

    with bar_col:
        st.subheader("📈 Risk Score by Location")
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
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            xaxis_tickangle=-45
        )
        st.plotly_chart(bar, use_container_width=True)

    with pie_col:
        st.subheader("🥧 Risk Distribution")
        pie = px.pie(
            df_display,
            names="risk_level",
            title="Risk Category Distribution",
            color="risk_level",
            color_discrete_map={"Low": "#10b981", "Medium": "#f59e0b", "High": "#ef4444"},
            hole=0.4
        )
        pie.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8")
        )
        st.plotly_chart(pie, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 State / UT Summary")

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

# ==========================================================
# TAB 4 – CHILDREN & UT FOCUS
# ==========================================================

with tab4:
    st.header("👧 Children Safety & Union Territory Deep Dive")

    # ── National context banner ──
    st.info("""
**📊 National Context (NCRB 2023)**
India registered **1,77,335** crimes against children in 2023 (+9.2% from 2022).
Major categories: **Kidnapping & Abduction** (79,884 cases, 45%) · **POCSO Act** (67,694 cases, 38%)
""")

    st.markdown("---")
    st.subheader("🗺️ Union Territories — Complete Overview")

    ut_df = df[df["territory_type"] == "Union Territory"].copy()

    # UT KPI row
    ut_cols = st.columns(4)
    ut_cols[0].metric("UT Locations", len(ut_df))
    ut_cols[1].metric("Total UT Women Cases (2023)", f"{int(ut_df['cases_2023'].sum()):,}")
    ut_cols[2].metric("Total UT Children Cases (2023)", f"{int(ut_df['children_cases_2023'].sum()):,}")
    ut_cols[3].metric("UT High Risk Zones", int((ut_df["risk_level"] == "High").sum()))

    st.markdown("---")

    # UT breakdown table
    st.subheader("📋 All Union Territory Districts — Crime Data")
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
        st.subheader("🏙️ Women Cases by Union Territory (2023)")
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
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            coloraxis_showscale=False
        )
        st.plotly_chart(bar_ut, use_container_width=True)

    with ch2:
        st.subheader("👧 Children Crime Breakdown by UT (2023)")
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
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig_children, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Delhi Districts — Detailed Breakdown")

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
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
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
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            xaxis_tickangle=-35
        )
        st.plotly_chart(delhi_children, use_container_width=True)

    # J&K deep dive
    st.markdown("---")
    st.subheader("📍 Jammu & Kashmir — District Breakdown")

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
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        xaxis_tickangle=-45
    )
    st.plotly_chart(jk_fig, use_container_width=True)

# ==========================================================
# TAB 5 – SAFETY ADVISOR
# ==========================================================

with tab5:
    st.header("🤖 SHEild Safety Advisor")
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
            # Gauge chart for safety score
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=safety,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Safety Score", "font": {"color": "#94a3b8"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#94a3b8"},
                    "bar": {"color": "#10b981" if risk == "Low" else "#f59e0b" if risk == "Medium" else "#ef4444"},
                    "steps": [
                        {"range": [0, 33], "color": "rgba(239,68,68,0.15)"},
                        {"range": [33, 66], "color": "rgba(245,158,11,0.15)"},
                        {"range": [66, 100], "color": "rgba(16,185,129,0.15)"}
                    ],
                    "threshold": {
                        "line": {"color": "white", "width": 2},
                        "thickness": 0.75,
                        "value": safety
                    },
                    "bgcolor": "rgba(0,0,0,0)"
                },
                number={"font": {"color": "#f8fafc"}}
            ))
            gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                height=220,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(gauge, use_container_width=True)

        st.markdown("---")

        if risk == "High":
            st.error(f"""
### 🚨 High Risk Assessment
**{selected_city}** ({row['district']}, {row['state_ut']}) is in the **HIGH RISK** category.

**Observed Indicators:**
- Crime volume: **{int(row['cases_2023']):,} reported cases in 2023**
- Crime rate: **{row['crime_rate_2023']} per lakh population** (national avg: 66.2)
- Crime trend: {"📈 Increasing" if row['cases_2023'] > row['cases_2021'] else "📉 Declining"}
- Children at risk: **{int(row['children_cases_2023']):,} cases** including {int(row['pocso_2023'])} POCSO
""")
        elif risk == "Medium":
            st.warning(f"""
### ⚠️ Medium Risk Assessment
**{selected_city}** has moderate safety concerns. Stay aware and take standard precautions.

- Cases 2023: **{int(row['cases_2023']):,}**
- Crime rate: **{row['crime_rate_2023']}** per lakh population
""")
        else:
            st.success(f"""
### ✅ Lower Risk Zone
**{selected_city}** shows comparatively lower crime indicators based on NCRB 2023 data.

- Cases 2023: **{int(row['cases_2023']):,}**
- Safety Score: **{safety}/100**
""")

        st.subheader("🛡️ Safety Recommendations")
        recommendations = generate_recommendation(risk)
        for rec in recommendations:
            st.write("✅", rec)

        st.markdown("---")
        st.subheader("📌 Full Location Summary")
        summary = pd.DataFrame({
            "Metric": [
                "City / Location", "State / UT", "Territory Type", "District",
                "Risk Level", "Risk Score", "Safety Score",
                "Women Cases (2021)", "Women Cases (2022)", "Women Cases (2023)",
                "Crime Rate (2023)", "Chargesheet Rate",
                "Children Cases (2023)", "POCSO Cases (2023)",
                "Children Kidnapping (2023)", "Predicted Cases (2024)"
            ],
            "Value": [
                str(selected_city), str(row["state_ut"]), str(row["territory_type"]), str(row["district"]),
                str(risk), str(score), f"{safety}/100",
                str(int(row["cases_2021"])), str(int(row["cases_2022"])), str(int(row["cases_2023"])),
                str(row["crime_rate_2023"]), f"{row['chargesheet_rate']}%",
                str(int(row["children_cases_2023"])), str(int(row["pocso_2023"])),
                str(int(row["kidnapping_children_2023"])), str(predict_next_year(row))
            ]
        })
        st.dataframe(summary, use_container_width=True, hide_index=True)
    else:
        st.error("City data not found.")

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")
st.caption("""
🛡️ **SHEild AI — Women & Children Safety Intelligence Platform**

Built with Python · Streamlit · Plotly · Scikit-learn · Pandas

**Data Source:** National Crime Records Bureau (NCRB) — Crime in India 2021, 2022, 2023.
Coverage: Metropolitan Cities · State capitals · All 8 Union Territories (Delhi, J&K, Puducherry,
Andaman & Nicobar, Dadra & Nagar Haveli and Daman & Diu, Ladakh, Lakshadweep, Chandigarh).

⚠️ This platform provides relative risk analysis using historical data for awareness and educational purposes only.
It does not predict individual crimes or guarantee future safety outcomes.
""")