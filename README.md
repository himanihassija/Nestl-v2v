# 🛡️ SHEild AI

**AI-Powered Women & Children Safety Intelligence Platform** — hackathon project

> 🚀 **Status: Stage 2** — nationwide coverage, children's safety data, and district-level intelligence added on top of the Stage 1 core dashboard.

---

## 💡 The Idea

Every year, NCRB publishes detailed crime data — but it's buried in dense PDF tables that almost nobody reads before they travel, relocate, or plan a route through an unfamiliar city. **SHEild AI** turns that raw, hard-to-parse government data into a single, visual, interactive dashboard: pick a city, and instantly see a relative safety score, a 3-year crime trend, and plain-language precautions generated for that specific risk level.

Stage 1 covered the 34 NCRB metropolitan cities. **Stage 2 expands this into a full national safety layer** — every Indian state capital/metro *and* all 8 Union Territories, down to the district level (73 locations total), plus a dedicated lens on crimes against children (POCSO, kidnapping/abduction), which Stage 1 didn't address at all.

## 🔗 Important Links

- **Live Deployment Link:** `[Insert URL here]`
- **Demo Video Link:** `[Insert YouTube/Drive URL here]`
- **GitHub Repository:** `https://github.com/himanihassija/Nestl-v2v`

## ✨ Features

**Carried over from Stage 1:**
- 📊 **Dashboard Overview** — key KPIs: locations analyzed, highest-risk city, high-risk zone count
- 🏙️ **City Safety Lookup** — case counts, crime rate, computed risk score, and a 2021–2023 crime trend chart per city
- 🗺️ **Interactive Risk Map** — geospatial view, toggle coloring by risk level or territory type, bubble-sized by case volume

**New in Stage 2:**
- 👧 **Children & UT Focus tab** — dedicated national context banner, full Union Territory breakdown (POCSO vs. kidnapping/abduction), and district-level deep dives for **Delhi's 10 districts** and **J&K's 17 districts**
- 🗺️ **Nationwide + UT coverage** — expanded from 34 metro cities to **73 locations**, covering all 8 Union Territories (Delhi, J&K, Puducherry, Andaman & Nicobar, Dadra & Nagar Haveli and Daman & Diu, Ladakh, Lakshadweep, Chandigarh) alongside State-level metros
- 🤖 **AI Safety Advisor** — expanded assessment with a live safety-score gauge, chargesheet rate, a simple next-year (2024) case projection, and a full exportable location summary table
- 📈 **Deeper Analytics** — Top 10 riskiest / safest locations, risk distribution, and a State/UT summary table with per-region aggregates
- ✅ **Data-verified pipeline** — the full 2021–2023 dataset for all 34 metro cities was cross-checked line-by-line against the original NCRB source PDF (zero discrepancies found), and every location has confirmed lat/lon coverage for the map

  **New in Stage 3:**
- 🛣️ **AI Safe Route Planner** — introduced an intelligent route planning system that generates multiple travel routes between two locations and prioritizes them based on safety rather than just distance.
- 📍 **Live Location Integration** — users can now use their current GPS location as the starting point for route planning, making safety recommendations more personalized and practical.
- 🗺️ **Interactive Route Visualization** — added dynamic map-based visualization of routes with clear start/end markers and route comparisons for easier decision-making.
- 🌙 **Modern UI with Theme Support** — completely redesigned the application interface with improved layouts, animations, responsive components, and support for both Light and Dark modes.
- 🤖 **Enhanced AI Safety Recommendations** — extended the existing AI safety engine to provide route-level safety insights and smarter travel recommendations using location-aware crime intelligence.
- 🔗 **Live Geocoding & Routing Services** — integrated external APIs to convert place names into geographic coordinates and fetch real-world routing information automatically.
- ⚙️ **Improved Project Architecture** — modularized the codebase by separating routing, simulation, and interface logic, making the application easier to maintain and extend.
- 🚀 **Performance & Usability Improvements** — optimized the application workflow, improved responsiveness, and enhanced the overall user experience while preserving all Stage 2 analytics and safety features.

### **New in Stage 4:**

- 🧭 **Advanced Safe Route Intelligence** — upgraded the route planner with a hybrid safety-ranking engine that evaluates multiple real-world driving routes using NCRB crime data, travel time, and distance to recommend the safest available option instead of only the shortest path.

- 📍 **Smart GPS & Location Search** — added browser-based GPS detection along with live place search, allowing users to start navigation from their current location or any searched destination across India.

- 🗺️ **Real-World Navigation Support** — introduced detailed turn-by-turn navigation, multiple route alternatives, interactive route comparison, and dynamic map visualization for a complete navigation experience.

- 🔄 **Multi-Provider Routing & Geocoding** — integrated Google Routes and Google Geocoding APIs with automatic OpenStreetMap (OSRM & Nominatim) fallbacks, ensuring reliable routing and location lookup even when one service is unavailable.

- 🛡️ **Enhanced Route Risk Analysis** — expanded the AI safety engine to analyze routes based on nearby NCRB crime intelligence, helping users choose paths that minimize exposure to higher-risk locations.

- ⚙️ **Resilient Backend Architecture** — redesigned the routing module with modular components, automatic API fallback mechanisms, environment-based configuration, and improved maintainability for future extensions.

- 🎨 **Refined User Experience** — polished the interface with smoother interactions, improved responsiveness, sticky navigation, enhanced Light/Dark theme support, and a more seamless end-to-end workflow.

- 🚀 **Performance & Reliability Improvements** — optimized route generation, geocoding, and overall application performance while preserving all Stage 3 analytics, AI safety insights, and dashboard capabilities.


## 🛠️ Tech Stack & Tools

- **Python 3.8+**
- **Streamlit** — web app framework
- **Pandas / NumPy** — data processing and merging
- **Plotly** — interactive charts, gauge, and geospatial map
- **Scikit-learn** (`MinMaxScaler`) — feature normalization for the weighted risk-scoring model
- **AI tools used:** Claude (Anthropic) — used throughout Stage 2 for code review, cross-verifying the dataset against the source NCRB PDF, catching bugs (unused imports, a hardcoded filename dependency, dead code paths), and drafting this documentation
  <!-- Add/adjust this line if you also used ChatGPT, Copilot, etc. -->

## 📁 Project Structure

```
Nestl-v2v/
├── app.py                     # Main Streamlit application (5 tabs)
├── simulation.py               # Risk scoring, recommendations, projections
├── city_coordinates.py         # Lat/lon mapping for all 73 locations
├── women_safety_dataset.csv    # NCRB dataset — women + children crime, 2021–2023
├── dataset_women.pdf           # Source NCRB reference document
└── requirements.txt            # Python dependencies
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+

### Installation

```bash
git clone https://github.com/himanihassija/Nestl-v2v.git
cd Nestl-v2v
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

## 📌 Documentation — How It Works

1. **Data ingestion:** `women_safety_dataset.csv` (women's crime + children's crime, 2021–2023, sourced from NCRB) is loaded and merged with per-city coordinates from `city_coordinates.py`.
2. **Risk scoring:** Each location gets a weighted composite score — 50% case volume, 30% crime rate per lakh population, 20% year-over-year trend (all min-max normalized) — blended with a 15% children's-crime component where that data is available.
3. **Classification:** Locations are bucketed into **Low / Medium / High** risk using percentile thresholds (33rd/66th) computed once across the full dataset, so labels stay consistent whether you're viewing all of India or filtering down to a single state.
4. **Presentation:** Five tabs surface this through KPIs, an interactive map, comparative analytics, a UT/children-focused deep dive, and an AI-generated advisor that turns the numeric risk level into specific, actionable precautions.

**Coordinating with AI tools:** Claude was used as a second set of eyes on the codebase after Stage 1 — it independently re-derived every metro city's 2021–2023 figures from the raw NCRB PDF table and diffed them against the CSV to confirm data accuracy before Stage 2 features were built on top of it, then reviewed `app.py` and `simulation.py` for logic bugs and unused code paths.

---

⚠️ Risk scores are relative estimates based on historical NCRB data — for awareness purposes only, not a prediction of individual crime.
