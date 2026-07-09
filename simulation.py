import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# ==========================================================
# CALCULATE RISK SCORE
# ==========================================================

def calculate_risk(df):
    """
    Calculates risk score and assigns risk levels.
    """

    df = df.copy()

    # Crime Trend
    df["trend"] = df["cases_2023"] - df["cases_2021"]

    # Normalize Features
    scaler = MinMaxScaler()

    df[
        [
            "cases_norm",
            "crime_norm",
            "trend_norm"
        ]
    ] = scaler.fit_transform(
        df[
            [
                "cases_2023",
                "crime_rate_2023",
                "trend"
            ]
        ]
    )

    # Weighted Risk Score
    df["risk_score"] = (
        0.5 * df["cases_norm"]
        + 0.3 * df["crime_norm"]
        + 0.2 * df["trend_norm"]
    )

    # Convert to Safety Score (0–100)
    df["safety_score"] = (1 - df["risk_score"]) * 100
    df["safety_score"] = df["safety_score"].round(1)

    # Percentile Thresholds
    low = df["risk_score"].quantile(0.33)
    high = df["risk_score"].quantile(0.66)

    def classify(score):

        if score <= low:
            return "Low"

        elif score <= high:
            return "Medium"

        return "High"

    df["risk_level"] = df["risk_score"].apply(classify)

    return df


# ==========================================================
# SIMULATE CRIME CHANGE
# ==========================================================

def simulate_crime_change(df, percentage):
    """
    Simulates increase/decrease in crime cases.
    Example:
        20 -> increase by 20%
       -10 -> decrease by 10%
    """

    simulated = df.copy()

    simulated["cases_2023"] = (
        simulated["cases_2023"]
        * (1 + percentage / 100)
    ).round()

    simulated = calculate_risk(simulated)

    return simulated


# ==========================================================
# CITY SUMMARY
# ==========================================================

def get_city_summary(df, city):

    row = df[df["city"] == city].iloc[0]

    return {

        "city": row["city"],

        "cases_2021": int(row["cases_2021"]),

        "cases_2022": int(row["cases_2022"]),

        "cases_2023": int(row["cases_2023"]),

        "crime_rate": float(row["crime_rate_2023"]),

        "risk_score": round(float(row["risk_score"]), 2),

        "risk_level": row["risk_level"],

        "safety_score": round(float(row["safety_score"]), 1)

    }


# ==========================================================
# AI RECOMMENDATIONS
# ==========================================================

def generate_recommendation(risk_level):

    if risk_level == "High":

        return [
            "Avoid isolated roads after dark.",
            "Prefer verified cab services.",
            "Share live location with trusted contacts.",
            "Keep emergency numbers easily accessible.",
            "Travel in groups whenever possible."
        ]

    elif risk_level == "Medium":

        return [
            "Remain aware of surroundings.",
            "Prefer well-lit public routes.",
            "Use trusted transportation.",
            "Inform family while travelling."
        ]

    else:

        return [
            "Continue following basic safety practices.",
            "Stay aware of surroundings.",
            "Use verified transport during late hours."
        ]


# ==========================================================
# DASHBOARD METRICS
# ==========================================================

def dashboard_metrics(df):

    return {

        "total_cities": len(df),

        "highest_risk_city":
            df.loc[
                df["risk_score"].idxmax(),
                "city"
            ],

        "average_risk":
            round(df["risk_score"].mean(), 2),

        "average_safety":
            round(df["safety_score"].mean(), 1),

        "high_risk":
            (df["risk_level"] == "High").sum(),

        "medium_risk":
            (df["risk_level"] == "Medium").sum(),

        "low_risk":
            (df["risk_level"] == "Low").sum()

    }


# ==========================================================
# TOP RISKY CITIES
# ==========================================================

def top_risky_cities(df, n=5):

    return (
        df.sort_values(
            "risk_score",
            ascending=False
        )
        .head(n)
    )


# ==========================================================
# SAFEST CITIES
# ==========================================================

def safest_cities(df, n=5):

    return (
        df.sort_values(
            "risk_score"
        )
        .head(n)
    )


# ==========================================================
# RISK DISTRIBUTION
# ==========================================================

def risk_distribution(df):

    return (
        df["risk_level"]
        .value_counts()
        .reset_index()
        .rename(
            columns={
                "index": "Risk Level",
                "risk_level": "Count"
            }
        )
    )


# ==========================================================
# FUTURE PREDICTION (Simple Projection)
# ==========================================================

def predict_next_year(city_row):
    """
    Projects next year's cases using a simple linear trend.
    """

    change = (
        city_row["cases_2023"]
        - city_row["cases_2022"]
    )

    prediction = city_row["cases_2023"] + change

    return max(0, int(prediction))