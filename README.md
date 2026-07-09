# 🛡️ SHEild AI

**AI-Powered Women's Safety Intelligence Platform** — hackathon project

SHEild AI turns historical crime data into actionable safety insights for Indian metropolitan cities using data analytics and geospatial visualization. It helps people quickly understand relative safety risk in a city and get practical, AI-generated precautions before they travel.

> 🚧 **Status: Stage 1** — core dashboard is live. More features planned in upcoming stages (see below).

---

## ✅ Stage 1 — What's Built

- **Dashboard Overview** — key metrics like total cities analyzed, highest-risk city, average risk score, and high-risk city count
- **City Safety Lookup** — select a city to see case counts, crime rate, computed risk score, and a 2021–2023 crime trend chart
- **Interactive Risk Map** — geospatial view of all cities, color-coded and sized by risk level
- **Analytics Dashboard** — top 5 / top 10 riskiest cities, risk distribution pie chart, and risk score histogram
- **AI Assistant Tab** — automated High/Medium/Low risk assessment with tailored safety recommendations for the selected city
- **Dataset** — NCRB Crime Against Women, Metropolitan Cities (2021–2023)

## 🔜 Planned for Next Stages

- [ ] Real-time crime data integration
- [ ] Sub-zone / locality-level risk mapping
- [ ] Route-based safety scoring
- [ ] Mobile app with live location sharing
- [ ] Improved ML-based risk prediction model

## 🛠️ Tech Stack

- **Python**
- **Streamlit** — web app framework
- **Pandas / NumPy** — data processing
- **Plotly** — interactive charts and maps
- **Scikit-learn** — risk scoring

## 📁 Project Structure

```
Nestl-v2v/
├── app.py                    # Main Streamlit application
├── simulation.py              # Risk calculation & recommendation logic
├── city_coordinates.py        # Lat/lon mapping for cities
├── women_safety_dataset.csv   # NCRB crime dataset
├── dataset women.pdf          # Source dataset reference
└── requirements.txt           # Python dependencies
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

## 📌 How It Works

1. Crime data is loaded and merged with city coordinates
2. A risk score is calculated per city based on case volume, crime rate, and trend direction
3. Cities are classified into **Low**, **Medium**, or **High** risk
4. The dashboard surfaces this through interactive visualizations and an AI assistant that generates context-aware safety recommendations

---

⚠️ Risk scores are relative estimates based on historical data — for awareness purposes only, not a prediction of individual crime.
