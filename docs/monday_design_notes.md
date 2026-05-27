# Monday Checkpoint Design Notes — Big Apple Air Quality

## 1. Dataset Selected

**NYC Open Data — Air Quality and Health Impacts**
URL: https://data.cityofnewyork.us/Environment/Air-Quality-and-Health-Impacts/c3uy-2p5r/about_data

## 2. Why This Dataset Works

- Large, real-world dataset with a natural mix of numeric and categorical columns
- Contains multiple distinct entities (indicators, locations, time periods) that normalize cleanly into separate tables
- Enables both environmental and public health analysis — strong analytical story
- Publicly available, maintained by the NYC Department of Health
- Works well for comparing relational (MySQL) and document (MongoDB) storage approaches
- Time-series structure supports trend queries

## 3. Logical Entities (5 entities)

| Entity | Description |
|---|---|
| `indicators` | Each unique combination of indicator ID, name, measure type, and unit |
| `geo_types` | The classification of a geographic area (Borough, UHF42, Community District) |
| `locations` | A specific named place, tied to a geography type |
| `time_periods` | A labeled time window with a parsed start date and extracted year |
| `measurements` | One observed data value linking an indicator, a location, and a time period |

## 4. Draft MySQL Schema Summary

    Database: big_apple_air_quality

    raw_air_quality    — staging table; all VARCHAR/TEXT for safe CSV import
    indicators         — indicator_key PK | indicator_id | name | measure | measure_info
    geo_types          — geo_type_id PK  | geo_type_name UNIQUE
    locations          — location_id PK  | geo_join_id | geo_place_name | geo_type_id FK
    time_periods       — time_period_id PK | time_period | start_date | year_value
    measurements       — unique_id PK | indicator_key FK | location_id FK | time_period_id FK | data_value | message

## 5. Primary Keys and Foreign Keys

| Table | Primary Key | Foreign Keys |
|---|---|---|
| indicators | indicator_key (AUTO_INCREMENT) | — |
| geo_types | geo_type_id (AUTO_INCREMENT) | — |
| locations | location_id (AUTO_INCREMENT) | geo_type_id → geo_types(geo_type_id) |
| time_periods | time_period_id (AUTO_INCREMENT) | — |
| measurements | unique_id (from raw data) | indicator_key → indicators, location_id → locations, time_period_id → time_periods |

**Additional constraints:**

- UNIQUE KEY on (indicator_id, name, measure, measure_info) in `indicators`
- UNIQUE KEY on geo_type_name in `geo_types`
- UNIQUE KEY on (geo_join_id, geo_place_name, geo_type_id) in `locations`
- UNIQUE KEY on (time_period, start_date) in `time_periods`
- CHECK (data_value IS NULL OR data_value >= 0) in `measurements`

**Indexes:**

- idx_measurements_indicator on measurements(indicator_key)
- idx_measurements_location on measurements(location_id)
- idx_measurements_time on measurements(time_period_id)
- idx_locations_geo_type on locations(geo_type_id)

## 6. Core Analytical Questions

1. Which NYC locations have the highest average air pollution values?
2. How have major air quality indicators changed over time?
3. Which boroughs or neighborhoods have the highest pollution-related health impacts?
4. How do pollutant levels differ across geography types (boroughs vs. community districts)?
5. Which areas appear to have both high pollutant levels and high health-impact rates?

## 7. Cleaning and Splitting Plan

**Step 1 — Import raw CSV into MySQL staging:**
- Download CSV from NYC Open Data
- Use MySQL Workbench Table Data Import Wizard
- Import into `raw_air_quality` — all columns as VARCHAR/TEXT, no transformation needed at this stage

**Step 2 — Clean for Python/Streamlit use (clean_data.py):**
- Normalize column names to snake_case
- Convert unique_id and indicator_id to numeric
- Parse start_date to datetime
- Convert data_value to numeric
- Remove duplicate rows by unique_id
- Save to data/cleaned/air_quality_cleaned.csv

**Step 3 — Normalize within MySQL (mysql_normalize.sql):**
- Create a view (clean_air_quality) that casts types and trims whitespace directly from raw_air_quality
- INSERT IGNORE into dimension tables: indicators, geo_types, locations, time_periods
- INSERT IGNORE into measurements using FK joins across all dimension tables
- Run validation SELECT COUNT(*) queries to confirm row counts in each table
