# Data Dictionary — Air Quality and Health Impacts (NYC Open Data)

Each row in the raw dataset represents one measured value for a specific air quality or health indicator
at a specific NYC location and time period.

| Column | Description | Likely Data Type | How We Use It in the Database |
|---|---|---|---|
| **Unique ID** | A unique integer identifier for each measurement record | Integer | Primary key (`unique_id`) in the `measurements` table |
| **Indicator ID** | Numeric code identifying the type of air quality or health indicator | Integer | Stored in `indicators.indicator_id`; used to group related indicator rows |
| **Name** | Human-readable name of the indicator (e.g., "Fine particles (PM 2.5)") | VARCHAR(255) | Stored in `indicators.name`; used in query filters and result labels |
| **Measure** | The statistical measure type (e.g., "Mean", "Number", "Rate") | VARCHAR(255) | Stored in `indicators.measure`; differentiates measure types for the same indicator |
| **Measure Info** | The unit of measurement (e.g., "mcg/m3", "per 100,000 adults") | VARCHAR(100) | Stored in `indicators.measure_info`; defaults to empty string if absent |
| **Geo Type Name** | Classification of the geographic area (e.g., "Borough", "UHF42", "CD") | VARCHAR(100) | Basis for the `geo_types` table; links locations to their geography type |
| **Geo Join ID** | A code used to join geographic data to spatial maps or census boundaries | VARCHAR(50) | Stored in `locations.geo_join_id`; useful for mapping or GIS joins |
| **Geo Place Name** | The name of the geographic area (e.g., "Bronx", "Kingsbridge - Riverdale") | VARCHAR(255) | Stored in `locations.geo_place_name`; used in query results and the dashboard |
| **Time Period** | A text label for the measurement window (e.g., "Annual Average 2009") | VARCHAR(100) | Stored in `time_periods.time_period`; used for grouping and filtering by period |
| **Start_Date** | Start date of the measurement period (e.g., "01/01/2009"), raw format MM/DD/YYYY | DATE (raw: VARCHAR) | Parsed to DATE in `time_periods.start_date`; year extracted into `time_periods.year_value` |
| **Data Value** | The numeric measurement for the indicator at that location and time | DECIMAL(12,4) | Stored in `measurements.data_value`; subject to CHECK constraint (>= 0); nullable for suppressed values |
| **Message** | An optional note or flag (e.g., suppression notices or data quality warnings) | TEXT | Stored in `measurements.message`; NULL when absent |
