# Big Apple Air Quality

## Description

A database and dashboard project analyzing air quality and health impacts across New York City
neighborhoods. We build a normalized MySQL relational database and a MongoDB document database
from the NYC Open Data "Air Quality and Health Impacts" dataset, run analytical queries,
compare database performance, and visualize findings in a Streamlit dashboard.

## Dataset

| | |
|---|---|
| **Name** | Air Quality and Health Impacts |
| **Source** | [NYC Open Data](https://data.cityofnewyork.us/Environment/Air-Quality-and-Health-Impacts/c3uy-2p5r/about_data) |
| **Format** | CSV |
| **Columns** | Unique ID, Indicator ID, Name, Measure, Measure Info, Geo Type Name, Geo Join ID, Geo Place Name, Time Period, Start_Date, Data Value, Message |

## Project Goals

1. Build a normalized 5-table MySQL schema from a real public dataset
2. Build a MongoDB collection with equivalent documents for comparison
3. Write and compare analytical queries across both databases
4. Measure query performance and the impact of indexing
5. Build an interactive Streamlit dashboard to visualize key findings

## Folder Structure

```
Big-Apple-Air-Quality/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/              <- place downloaded CSV here: air_quality.csv
│   └── cleaned/          <- clean_data.py output goes here
├── docs/
│   ├── data_dictionary.md
│   └── monday_design_notes.md
├── sql/
│   ├── mysql_schema.sql       <- run first: creates DB and all tables
│   ├── mysql_normalize.sql    <- run second: normalizes raw data into tables
│   ├── mysql_queries.sql      <- run third: 5 analytical queries
│   └── mysql_performance.sql  <- run last: EXPLAIN and index timing tests
├── mongodb/
│   ├── mongo_setup.js         <- placeholder
│   └── mongo_queries.js       <- placeholder
├── scripts/
│   ├── clean_data.py          <- cleans CSV for Python/Streamlit use
│   └── load_mysql.py          <- placeholder for loading via Python
└── streamlit_app/
    └── app.py                 <- dashboard (placeholder)
```

## MySQL Setup Instructions

Follow these steps in order:

1. **Download the CSV** from NYC Open Data and save it to `data/raw/air_quality.csv`
2. **Clean the data for Python use** — run from the project root:
   ```
   python scripts/clean_data.py
   ```
   This creates `data/cleaned/air_quality_cleaned.csv`.
3. **Create the database** — open MySQL Workbench and run `sql/mysql_schema.sql`.
   This drops and recreates the `big_apple_air_quality` database with all tables.
4. **Import the raw CSV** — in MySQL Workbench, use the
   **Table Data Import Wizard** to import `data/raw/air_quality.csv` into the
   `raw_air_quality` table. Map all columns as text/varchar.
5. **Normalize the data** — run `sql/mysql_normalize.sql`.
   Check the validation row counts printed at the end to confirm the data loaded correctly.
6. **Run analytical queries** — open `sql/mysql_queries.sql` and run each query
   individually to explore the data.
7. **Run performance tests** — open `sql/mysql_performance.sql` and follow the
   section comments. Do not stop mid-way through Section 2 (index drop/restore).

## MySQL Schema Summary

Database: `big_apple_air_quality`

| Table | Purpose |
|---|---|
| `raw_air_quality` | Staging table — all VARCHAR/TEXT for safe CSV import |
| `indicators` | Unique indicator types (ID, name, measure, unit) |
| `geo_types` | Geography classifications (Borough, UHF42, CD, etc.) |
| `locations` | Named places with their geography type |
| `time_periods` | Distinct time windows with parsed start dates and year values |
| `measurements` | One row per data point; links all four dimension tables via foreign keys |

**Constraints and indexes:**
- PRIMARY KEY on every table
- FOREIGN KEYS: locations → geo_types; measurements → indicators, locations, time_periods
- UNIQUE KEY on natural keys in each dimension table
- CHECK constraint: `data_value IS NULL OR data_value >= 0` in measurements
- Four indexes on measurements and locations for join/filter performance

---

## MongoDB (Planned)

MongoDB collection setup and queries will be added during the MongoDB portion of the project.
See `mongodb/mongo_setup.js` and `mongodb/mongo_queries.js`.

---

## Streamlit Dashboard (Planned)

An interactive dashboard will be built after database queries are finalized.
See `streamlit_app/app.py`. Run with:
```
streamlit run streamlit_app/app.py
```

---

## Performance Comparison (Planned)

Runtime comparisons (MySQL vs. MongoDB) and EXPLAIN output will be documented
in `sql/mysql_performance.sql` and the final report.

---

## Final Presentation (Planned)

Presentation slides and a written summary of findings will be added to `docs/`
before the final project deadline.
