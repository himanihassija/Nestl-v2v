import streamlit as st
import pandas as pd
import plotly.express as px
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

.main{
    background-color:#f7f9fc;
}

h1,h2,h3{
    color:#1f2937;
}

div[data-testid="metric-container"]{
    background:white;
    padding:15px;
    border-radius:15px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🛡️ SHEild AI")
st.subheader("AI-Powered Women's Safety Intelligence Platform")

st.markdown("""
Transforming historical crime data into actionable safety insights using
AI, data analytics and geospatial visualization.

**Aligned with**
- SDG 5 – Gender Equality
- SDG 11 – Sustainable Cities
""")

st.divider()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv("women_safety_dataset.csv")

# --------------------------------------------------
# ADD COORDINATES
# --------------------------------------------------

coords = pd.DataFrame(
    [(city, lat, lon) for city, (lat, lon) in CITY_COORDINATES.items()],
    columns=["city", "lat", "lon"]
)

df = df.merge(coords, on="city", how="left")

# --------------------------------------------------

df = calculate_risk(df)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🛡️ SHEild AI")

st.sidebar.info("""
AI-Powered Women's Safety Intelligence Platform

Dataset:
NCRB Metropolitan Crime Against Women
(2021–2023)

This dashboard estimates relative safety risk using historical crime data.
""")

st.sidebar.markdown("---")

selected_city = st.sidebar.selectbox(
    "Select a City",
    sorted(df["city"].unique())
)

city_data = df[df["city"]==selected_city]

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.header("📊 Dashboard Overview")

c1,c2,c3,c4 = st.columns(4)
metrics = dashboard_metrics(df)

c1.metric("Cities", metrics["total_cities"])
c2.metric("Highest Risk", metrics["highest_risk_city"])
c3.metric("Average Risk", metrics["average_risk"])
c4.metric("High Risk Cities", metrics["high_risk"])
st.divider()

# --------------------------------------------------
# TABS
# --------------------------------------------------

tab1,tab2,tab3,tab4 = st.tabs(
    [
        "🏠 Dashboard",
        "🗺️ Risk Map",
        "📊 Analytics",
        "🤖 AI Assistant"
    ]
)
# ==========================================================
# TAB 1 - DASHBOARD
# ==========================================================

with tab1:

    st.header("📍 City Safety Dashboard")

    st.subheader(f"Selected City: {selected_city}")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Cases (2023)",
        int(city_data["cases_2023"].values[0])
    )

    col2.metric(
        "Crime Rate",
        round(float(city_data["crime_rate_2023"].values[0]), 2)
    )

    col3.metric(
        "Risk Score",
        round(float(city_data["risk_score"].values[0]), 2)
    )

    st.markdown("---")

    risk = city_data["risk_level"].values[0]

    if risk == "High":
        st.error(f"""
### 🚨 High Risk

**{selected_city}** is classified as a **High Risk** city based on:

- High number of reported cases
- Higher crime rate
- Increasing crime trend

**Recommendation**
- Prefer verified transport.
- Avoid isolated areas after dark.
- Share live location with trusted contacts.
- Stay alert in unfamiliar locations.
""")

    elif risk == "Medium":
        st.warning(f"""
### ⚠️ Medium Risk

**{selected_city}** falls under the Medium Risk category.

**Recommendation**
- Stay aware of surroundings.
- Prefer well-lit roads.
- Keep emergency contacts accessible.
""")

    else:

        st.success(f"""
### ✅ Low Risk

Historical data suggests comparatively lower risk.

Basic safety precautions are still recommended.
""")

    st.markdown("---")
    st.subheader("🛡️ Safety Recommendations")

    recommendations = generate_recommendation(risk)

    for rec in recommendations:
        st.write("✅", rec)

    st.subheader("📈 Crime Trend (2021–2023)")

    trend_df = pd.DataFrame({

        "Year":[
            "2021",
            "2022",
            "2023"
        ],

        "Cases":[
            city_data["cases_2021"].values[0],
            city_data["cases_2022"].values[0],
            city_data["cases_2023"].values[0]
        ]

    })

    trend_fig = px.line(

        trend_df,

        x="Year",

        y="Cases",

        markers=True,

        title=f"Crime Trend in {selected_city}"

    )

    st.plotly_chart(
        trend_fig,
        use_container_width=True
    )

# ==========================================================
# TAB 2 - MAP
# ==========================================================

with tab2:

    st.header("🗺️ Women Safety Risk Map")

    map_fig = px.scatter_mapbox(

        df,

        lat="lat",

        lon="lon",

        hover_name="city",

        hover_data=[
            "risk_score",
            "cases_2023",
            "crime_rate_2023"
        ],

        color="risk_level",

        size="risk_score",

        zoom=3.8,

        height=700,

        color_discrete_map={

            "Low":"green",

            "Medium":"orange",

            "High":"red"

        }

    )

    map_fig.update_layout(

        mapbox_style="carto-positron",

        margin=dict(

            l=0,

            r=0,

            t=0,

            b=0

        )

    )

    st.plotly_chart(

        map_fig,

        use_container_width=True

    )
# ==========================================================
# TAB 3 - ANALYTICS
# ==========================================================

with tab3:

    st.header("📊 Analytics Dashboard")

    st.subheader("🏆 Top 5 Highest Risk Cities")

    top5 = top_risky_cities(df)[
    ["city", "risk_level", "risk_score", "cases_2023", "crime_rate_2023"]
]

    st.dataframe(
        top5,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.subheader("📈 Top 10 Cities by Risk Score")

    top10 = (
        df.sort_values("risk_score", ascending=False)
        .head(10)
    )

    bar = px.bar(
        top10,
        x="city",
        y="risk_score",
        color="risk_level",
        title="Top 10 Highest Risk Cities",
        color_discrete_map={
            "Low": "green",
            "Medium": "orange",
            "High": "red"
        }
    )

    st.plotly_chart(
        bar,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("🥧 Risk Distribution")

    pie = px.pie(
        df,
        names="risk_level",
        title="Distribution of Risk Categories",
        color="risk_level",
        color_discrete_map={
            "Low": "green",
            "Medium": "orange",
            "High": "red"
        }
    )

    st.plotly_chart(
        pie,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("📊 Risk Score Distribution")

    hist = px.histogram(
        df,
        x="risk_score",
        nbins=10,
        color="risk_level",
        title="Distribution of AI Risk Scores",
        color_discrete_map={
            "Low": "green",
            "Medium": "orange",
            "High": "red"
        }
    )

    st.plotly_chart(
        hist,
        use_container_width=True
    )

# ==========================================================
# TAB 4 - AI ASSISTANT
# ==========================================================

with tab4:

    st.header("🤖 SHEild AI Assistant")

    st.subheader(f"Safety Assessment for {selected_city}")

    risk = city_data["risk_level"].values[0]
    score = round(float(city_data["risk_score"].values[0]), 2)
    cases = int(city_data["cases_2023"].values[0])
    rate = round(float(city_data["crime_rate_2023"].values[0]), 2)

    st.metric("AI Risk Score", score)

    if risk == "High":

        st.error(f"""
### 🚨 AI Assessment

Based on historical NCRB crime data,
**{selected_city}** is categorized as **HIGH RISK**.

**Observed Indicators**
- High crime volume
- Elevated crime rate
- Increasing trend over recent years

### Recommended Precautions

✅ Prefer verified cab services

✅ Share live location

✅ Avoid isolated streets late at night

✅ Stay in well-lit public places

✅ Save emergency contacts

⚠️ This assessment is based on historical city-level crime statistics and should be used for awareness purposes.
""")

    elif risk == "Medium":

        st.warning(f"""
### ⚠️ AI Assessment

**{selected_city}** falls under the **MEDIUM RISK** category.

Recommendations:

• Stay alert in unfamiliar areas

• Prefer populated routes

• Inform trusted contacts while travelling

• Use emergency helpline features when necessary
""")

    else:

        st.success(f"""
### ✅ AI Assessment

Historical crime indicators suggest comparatively lower risk.

Recommendations:

• Continue following basic safety precautions

• Use trusted transportation

• Remain aware of surroundings
""")

    st.markdown("---")

    st.subheader("📌 Selected City Summary")

    summary = pd.DataFrame({

        "Metric": [

            "City",

            "Risk Level",

            "Risk Score",

            "Cases (2023)",

            "Crime Rate"

        ],

        "Value": [

            selected_city,

            risk,

            score,

            cases,

            rate

        ]

    })

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")

st.caption("""
🛡️ **SHEild AI — AI-Powered Women's Safety Intelligence Platform**

Built using:
- Python
- Streamlit
- Plotly
- Scikit-learn
- Pandas

**Data Source:** National Crime Records Bureau (NCRB) – Crime Against Women in Metropolitan Cities (2021–2023).

This platform provides relative risk analysis using historical data for awareness and educational purposes. It does not predict individual crimes or guarantee future safety outcomes.
""")
