

import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

st.set_page_config(page_title="Big Apple Air Quality", layout="wide")

st.title("Big Apple Air Quality")
st.subheader("NYC Air Quality and Health Impacts Dashboard")

st.markdown("""
**Dataset:** NYC Open Data — Air Quality and Health Impacts

**Source:** [data.cityofnewyork.us](https://data.cityofnewyork.us/Environment/Air-Quality-and-Health-Impacts/c3uy-2p5r/about_data)

This dataset contains measurements of air quality indicators (PM2.5, NO2, Ozone, and more)
across New York City neighborhoods and boroughs, along with associated health impact metrics
such as asthma hospitalizations and respiratory event rates.
""")

client = MongoClient("mongodb://localhost:27017/")
db = client["big_apple_air_quality"]
measurements = db["measurements"]

pipeline = [
    {
        "$match": {
            "indicator.name": "Fine particles (PM 2.5)",
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
    {"$limit": 10}
]

results = list(measurements.aggregate(pipeline))
df = pd.DataFrame(results)

df = df.rename(columns={
    "_id": "Neighborhood",
    "average_pollution": "Average PM2.5"
})

st.markdown("### Top pollutant levels by neighborhood")

# Interactive controls
pollutant_options = [
    "Fine particles (PM 2.5)",
    "Nitrogen dioxide (NO2)",
    "Ozone (O3)"
]

selected_pollutant = st.selectbox(
    "Select air quality indicator:",
    pollutant_options
)

top_n = st.slider(
    "Select number of neighborhoods to show:",
    min_value=5,
    max_value=20,
    value=10
)

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
df = pd.DataFrame(results)

df = df.rename(columns={
    "_id": "Neighborhood",
    "average_pollution": "Average Value"
})

fig = px.bar(
    df,
    x="Average Value",
    y="Neighborhood",
    orientation="h",
    title=f"Highest Average {selected_pollutant} Levels by UHF42 Neighborhood",
    text="Average Value"
)

fig.update_layout(yaxis={"categoryorder": "total ascending"})

st.plotly_chart(fig, use_container_width=True)

st.markdown(f"""
**Interpretation:** This chart shows the UHF42 neighborhoods with the highest average **{selected_pollutant}** values.
The dropdown lets users choose the pollutant, and the slider controls how many neighborhoods are shown.
This chart is based on a MongoDB aggregation query that filters by indicator, groups by neighborhood,
and calculates the average value.
""")

st.markdown("---")

st.markdown("### Year-over-year air quality trend")

# Interactive controls for second visualization
trend_indicator_options = [
    "Fine particles (PM 2.5)",
    "Nitrogen dioxide (NO2)",
    "Ozone (O3)"
]

selected_trend_indicators = st.multiselect(
    "Select indicators to show in trend chart:",
    trend_indicator_options,
    default=trend_indicator_options
)

show_markers = st.checkbox(
    "Show markers on line chart",
    value=True
)

pipeline2 = [
    {
        "$match": {
            "indicator.name": {
                "$in": selected_trend_indicators
            }
        }
    },
    {
        "$group": {
            "_id": {
                "indicator": "$indicator.name",
                "time_period": "$time.time_period"
            },
            "average_value": {
                "$avg": "$data_value"
            }
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
trend_df = pd.DataFrame(results2)

if not trend_df.empty:
    trend_df = trend_df.sort_values("time_period")

    fig2 = px.line(
        trend_df,
        x="time_period",
        y="average_value",
        color="indicator",
        markers=show_markers,
        title="Average Air Quality Indicators Over Time"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    **Interpretation:** This chart compares selected air quality indicators across different NYC time periods.
    Users can choose which pollutants to display and whether to show point markers on the line chart.
    The visualization is generated directly from a MongoDB aggregation query using grouping and averaging operations.
    """)
else:
    st.warning("Please select at least one indicator to display the trend chart.")

st.markdown("---")

st.markdown(" ### Health impact comparison across boroughs")

pipeline3 = [
    {
        "$match": {
            "indicator.name": {
                "$regex": "asthma|hospitalization|death",
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
    {
        "$sort": {"average_health_impact": -1}
    },
    {
        "$limit": 10
    }
]

results3 = list(measurements.aggregate(pipeline3))
health_df = pd.DataFrame(results3)

health_df = health_df.rename(columns={
    "_id": "Neighborhood",
    "average_health_impact": "Average Health Impact"
})

fig3 = px.bar(
    health_df,
    x="Average Health Impact",
    y="Neighborhood",
    orientation="h",
    title="Top 10 Neighborhoods by Pollution-Related Health Impacts",
    text="Average Health Impact"
)

fig3.update_layout(yaxis={"categoryorder": "total ascending"})

st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
**Interpretation:** This chart shows the UHF42 neighborhoods with the highest average pollution-related health impact values, based on indicators such as asthma, hospitalization, and death-related measures. It uses a MongoDB aggregation query to filter health-related indicators, group by neighborhood, and calculate the average value.
""")