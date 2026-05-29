import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from pathlib import Path

st.set_page_config(page_title="Big Apple Air Quality", layout="wide")

st.title("Big Apple Air Quality")
st.subheader("NYC Air Quality and Health Impacts Dashboard")

st.markdown("""
**Dataset:** NYC Open Data — Air Quality and Health Impacts

**Source:** data.cityofnewyork.us

This dataset contains measurements of air quality indicators such as PM2.5, NO2, and ozone
across New York City neighborhoods and boroughs, along with associated health impact metrics
such as asthma hospitalizations and respiratory event rates.
""")

# Sidebar controls
st.sidebar.header("Dashboard Controls")

selected_pollutant = st.sidebar.selectbox(
    "Pollutant",
    ["Fine particles (PM 2.5)", "Nitrogen dioxide (NO2)", "Ozone (O3)"],
    index=0
)

top_n = st.sidebar.slider(
    "Number of locations to show",
    min_value=5,
    max_value=20,
    value=10
)

health_keyword = st.sidebar.selectbox(
    "Health impact type",
    ["asthma", "hospitalization", "death"],
    index=0
)

data_mode = st.sidebar.selectbox(
    "Data source display mode",
    ["MongoDB with SQL backup", "SQL outputs only"],
    index=0
)

show_raw = st.sidebar.checkbox("Show raw query result tables", value=False)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_OUTPUT_DIR = PROJECT_ROOT / "docs" / "sql_outputs"


def load_sql_csv(filename):
    path = SQL_OUTPUT_DIR / filename
    if not path.exists():
        st.warning(f"{filename} not found in docs/sql_outputs.")
        return None

    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.warning(f"Could not load {filename}: {e}")
        return None


def show_raw_table(title, df):
    if show_raw and df is not None:
        with st.expander(title):
            st.dataframe(df, use_container_width=True)


# MongoDB connection
mongo_ok = False
measurements = None

if data_mode == "MongoDB with SQL backup":
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
        client.server_info()
        db = client["big_apple_air_quality"]
        measurements = db["measurements"]
        mongo_ok = True
    except Exception as e:
        st.warning(f"MongoDB unavailable, using SQL CSV outputs instead. Details: {e}")


# Visualization 1
st.markdown("### Top Pollutant Levels by Neighborhood")

mongo_q1_shown = False

if mongo_ok:
    try:
        pipeline = [
            {
                "$match": {
                    "indicator.name": selected_pollutant,
                    "location.geo_type_name": "UHF42"
                }
            },
            {
                "$group": {
                    "_id": "$location.geo_place_name",
                    "average_pollution": {"$avg": "$data_value"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"average_pollution": -1}},
            {"$limit": top_n}
        ]

        results = list(measurements.aggregate(pipeline))
        q1_mongo_df = pd.DataFrame(results)

        if not q1_mongo_df.empty:
            q1_mongo_df = q1_mongo_df.rename(
                columns={
                    "_id": "Neighborhood",
                    "average_pollution": "Average Value"
                }
            )

            fig_q1_mongo = px.bar(
                q1_mongo_df,
                x="Average Value",
                y="Neighborhood",
                orientation="h",
                title=f"Top {top_n} UHF42 Neighborhoods by Average {selected_pollutant}",
                text="Average Value"
            )
            fig_q1_mongo.update_traces(texttemplate="%{x:.2f}", textposition="outside")
            fig_q1_mongo.update_layout(
                yaxis={"categoryorder": "total ascending"},
                xaxis_title="Average Pollution Value",
                yaxis_title="Neighborhood"
            )

            st.plotly_chart(fig_q1_mongo, use_container_width=True)
            st.caption("Source: MongoDB aggregation query.")
            show_raw_table("Pollution query results (MongoDB)", q1_mongo_df)
            mongo_q1_shown = True
        else:
            st.warning(f"MongoDB returned no data for {selected_pollutant}. Showing SQL backup.")

    except Exception as e:
        st.warning(f"MongoDB Q1 query failed. Showing SQL backup. Details: {e}")

if not mongo_q1_shown:
    q1_df = load_sql_csv("Q1_SQL.csv")

    if q1_df is not None:
        if "pollutant" in q1_df.columns:
            q1_df = q1_df[q1_df["pollutant"] == selected_pollutant]

        required_cols = {"location", "avg_pollution_value"}
        if not required_cols.issubset(q1_df.columns):
            st.warning(f"Q1_SQL.csv is missing required columns: {required_cols}")
        elif q1_df.empty:
            st.warning(f"Q1_SQL.csv has no rows for {selected_pollutant}.")
        else:
            q1_df = q1_df.sort_values("avg_pollution_value", ascending=False).head(top_n)
            color_col = "geography_type" if "geography_type" in q1_df.columns else None

            fig_q1 = px.bar(
                q1_df,
                x="avg_pollution_value",
                y="location",
                orientation="h",
                color=color_col,
                title=f"Top Locations by Average {selected_pollutant} (SQL Output)",
                text="avg_pollution_value",
                labels={
                    "avg_pollution_value": "Average Pollution Value",
                    "location": "Location",
                    "geography_type": "Geography Type"
                }
            )
            fig_q1.update_traces(texttemplate="%{x:.2f}", textposition="outside")
            fig_q1.update_layout(yaxis={"categoryorder": "total ascending"})

            st.plotly_chart(fig_q1, use_container_width=True)
            st.caption("Source: MySQL query output CSV.")
            show_raw_table("Pollution query results (SQL)", q1_df)

st.markdown("""
**Interpretation:** This chart identifies locations with the highest average values for the selected
pollutant. Pollutants are viewed separately because PM2.5, NO2, and ozone use different units.
""")

st.markdown("---")


# Visualization 2
st.markdown("### Air Quality Indicators Over Time")

indicator_options = ["Fine particles (PM 2.5)", "Nitrogen dioxide (NO2)", "Ozone (O3)"]

selected_indicators = st.multiselect(
    "Select indicators to display",
    options=indicator_options,
    default=indicator_options
)

mongo_q2_shown = False

if mongo_ok:
    try:
        pipeline2 = [
            {
                "$match": {
                    "indicator.name": {"$in": selected_indicators}
                }
            },
            {
                "$group": {
                    "_id": {
                        "indicator": "$indicator.name",
                        "time_period": "$time.time_period"
                    },
                    "average_value": {"$avg": "$data_value"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "indicator": "$_id.indicator",
                    "time_period": "$_id.time_period",
                    "average_value": 1
                }
            }
        ]

        results2 = list(measurements.aggregate(pipeline2))
        trend_mongo_df = pd.DataFrame(results2)

        if not trend_mongo_df.empty:
            year_extracted = trend_mongo_df["time_period"].astype(str).str.extract(r"(\d{4})")

            if year_extracted[0].notna().any():
                trend_mongo_df["year"] = year_extracted[0].astype(float)
                x_col = "year"
                x_label = "Year"
            else:
                x_col = "time_period"
                x_label = "Time Period"

            trend_mongo_df = trend_mongo_df.sort_values(x_col)

            fig_q2_mongo = px.line(
                trend_mongo_df,
                x=x_col,
                y="average_value",
                color="indicator",
                markers=True,
                title="Air Quality Indicators Over Time",
                labels={
                    x_col: x_label,
                    "average_value": "Average Value",
                    "indicator": "Indicator"
                }
            )

            st.plotly_chart(fig_q2_mongo, use_container_width=True)
            st.caption("Source: MongoDB aggregation query.")
            show_raw_table("Trend query results (MongoDB)", trend_mongo_df)
            mongo_q2_shown = True
        else:
            st.warning("MongoDB returned no trend data. Showing SQL backup.")

    except Exception as e:
        st.warning(f"MongoDB Q2 query failed. Showing SQL backup. Details: {e}")

if not mongo_q2_shown:
    q2_df = load_sql_csv("Q2_SQL.csv")

    if q2_df is not None:
        if "pollutant" in q2_df.columns and selected_indicators:
            q2_df = q2_df[q2_df["pollutant"].isin(selected_indicators)]

        required_cols = {"avg_pollution_value"}
        if not required_cols.issubset(q2_df.columns):
            st.warning(f"Q2_SQL.csv is missing required columns: {required_cols}")
        elif q2_df.empty:
            st.warning("Q2_SQL.csv has no rows for the selected indicators.")
        else:
            if "year" in q2_df.columns:
                x_col = "year"
                x_label = "Year"
            elif "time_period" in q2_df.columns:
                extracted = q2_df["time_period"].astype(str).str.extract(r"(\d{4})")
                if extracted[0].notna().any():
                    q2_df["year"] = extracted[0].astype(float)
                    x_col = "year"
                    x_label = "Year"
                else:
                    x_col = "time_period"
                    x_label = "Time Period"
            else:
                st.warning("Q2_SQL.csv needs either a year or time_period column.")
                x_col = None

            if x_col:
                q2_df = q2_df.sort_values(x_col)
                color_col = "pollutant" if "pollutant" in q2_df.columns else None

                fig_q2 = px.line(
                    q2_df,
                    x=x_col,
                    y="avg_pollution_value",
                    color=color_col,
                    markers=True,
                    title="Air Quality Indicators Over Time (SQL Output)",
                    labels={
                        x_col: x_label,
                        "avg_pollution_value": "Average Value",
                        "pollutant": "Indicator"
                    }
                )

                st.plotly_chart(fig_q2, use_container_width=True)
                st.caption("Source: MySQL query output CSV.")
                show_raw_table("Trend query results (SQL)", q2_df)

st.markdown("""
**Interpretation:** This trend view shows how average pollutant values changed over time. It helps
show whether air quality indicators improved, worsened, or followed different patterns depending
on the pollutant.
""")

st.markdown("---")


# Visualization 3
st.markdown("### Health Impact Comparison by Neighborhood")

mongo_q3_shown = False

if mongo_ok:
    try:
        pipeline3 = [
            {
                "$match": {
                    "indicator.name": {
                        "$regex": health_keyword,
                        "$options": "i"
                    },
                    "location.geo_type_name": "UHF42"
                }
            },
            {
                "$group": {
                    "_id": "$location.geo_place_name",
                    "average_health_impact": {"$avg": "$data_value"},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"average_health_impact": -1}},
            {"$limit": top_n}
        ]

        results3 = list(measurements.aggregate(pipeline3))
        health_mongo_df = pd.DataFrame(results3)

        if not health_mongo_df.empty:
            health_mongo_df = health_mongo_df.rename(
                columns={
                    "_id": "Neighborhood",
                    "average_health_impact": "Average Health Impact"
                }
            )

            fig_q3_mongo = px.bar(
                health_mongo_df,
                x="Average Health Impact",
                y="Neighborhood",
                orientation="h",
                title=f"Top {top_n} Neighborhoods by {health_keyword.title()}-Related Health Impact",
                text="Average Health Impact"
            )
            fig_q3_mongo.update_traces(texttemplate="%{x:.2f}", textposition="outside")
            fig_q3_mongo.update_layout(
                yaxis={"categoryorder": "total ascending"},
                xaxis_title="Average Health Impact",
                yaxis_title="Neighborhood"
            )

            st.plotly_chart(fig_q3_mongo, use_container_width=True)
            st.caption("Source: MongoDB aggregation query.")
            show_raw_table("Health impact query results (MongoDB)", health_mongo_df)
            mongo_q3_shown = True
        else:
            st.warning(f"MongoDB returned no data for health keyword '{health_keyword}'. Showing SQL backup.")

    except Exception as e:
        st.warning(f"MongoDB Q3 query failed. Showing SQL backup. Details: {e}")

if not mongo_q3_shown:
    q3_df = load_sql_csv("Q3_SQL.csv")

    if q3_df is not None:
        if "health_impact_indicator" in q3_df.columns:
            q3_df = q3_df[
                q3_df["health_impact_indicator"].str.contains(
                    health_keyword,
                    case=False,
                    na=False
                )
            ]

        required_cols = {"location", "avg_health_impact_value"}
        if not required_cols.issubset(q3_df.columns):
            st.warning(f"Q3_SQL.csv is missing required columns: {required_cols}")
        elif q3_df.empty:
            st.warning(f"Q3_SQL.csv has no rows matching '{health_keyword}'.")
        else:
            q3_df = q3_df.sort_values("avg_health_impact_value", ascending=False).head(top_n)
            color_col = "geography_type" if "geography_type" in q3_df.columns else None

            fig_q3 = px.bar(
                q3_df,
                x="avg_health_impact_value",
                y="location",
                orientation="h",
                color=color_col,
                title=f"Highest {health_keyword.title()}-Related Health Impacts (SQL Output)",
                text="avg_health_impact_value",
                labels={
                    "avg_health_impact_value": "Average Health Impact",
                    "location": "Location",
                    "geography_type": "Geography Type"
                }
            )
            fig_q3.update_traces(texttemplate="%{x:.2f}", textposition="outside")
            fig_q3.update_layout(yaxis={"categoryorder": "total ascending"})

            st.plotly_chart(fig_q3, use_container_width=True)
            st.caption("Source: MySQL query output CSV.")
            show_raw_table("Health impact query results (SQL)", q3_df)

st.markdown(f"""
**Interpretation:** This chart focuses on estimated health burden rather than direct pollution
concentration. It highlights neighborhoods or boroughs with higher pollution-related
{health_keyword} impact values.
""")

st.markdown("---")


# Visualization 4
st.markdown("### PM2.5 Pollution and Asthma Impact Overlap")

q4_df = load_sql_csv("Q4_SQL.csv")

if q4_df is not None:
    required_cols = {"avg_pm25_value", "avg_pm25_asthma_impact", "location"}

    if not required_cols.issubset(q4_df.columns):
        st.warning(f"Q4_SQL.csv is missing required columns: {required_cols}")
    else:
        color_col = "geography_type" if "geography_type" in q4_df.columns else None

        fig_q4 = px.scatter(
            q4_df,
            x="avg_pm25_value",
            y="avg_pm25_asthma_impact",
            color=color_col,
            hover_name="location",
            title="PM2.5 Pollution vs. PM2.5-Related Asthma Impact (SQL Output)",
            labels={
                "avg_pm25_value": "Average PM2.5 Level",
                "avg_pm25_asthma_impact": "PM2.5-Related Asthma Impact",
                "geography_type": "Geography Type"
            }
        )

        st.plotly_chart(fig_q4, use_container_width=True)
        st.caption("Source: MySQL query output CSV.")
        show_raw_table("PM2.5/asthma overlap SQL output", q4_df)

        st.markdown("""
**Interpretation:** This custom query compares PM2.5 pollution levels with PM2.5-related asthma
impact estimates. The relationship is not perfectly one-to-one, which suggests that health burden
may also depend on population vulnerability and local conditions.
""")

st.markdown("---")


# Key takeaway
st.markdown("### Key Takeaway")
st.markdown("""
The dashboard combines MongoDB aggregation queries with SQL query outputs to communicate the
project's four findings. MongoDB supports live aggregation from the document database, while the
SQL CSV outputs provide reliable query-backed visuals for location rankings, time trends, health
impacts, and the PM2.5/asthma overlap analysis.
""")