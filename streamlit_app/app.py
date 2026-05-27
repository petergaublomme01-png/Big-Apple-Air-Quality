import streamlit as st

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

st.info(
    "Charts and interactive visualizations will be added after database queries are finalized."
)

st.markdown("---")
st.markdown("**Planned sections:**")
st.markdown("- Top pollutant levels by neighborhood")
st.markdown("- Year-over-year PM2.5 trend")
st.markdown("- Health impact comparison across boroughs")
st.markdown("- MySQL vs. MongoDB performance comparison")
st.markdown("- Custom query explorer")
