-- =============================================================================
-- mysql_normalize.sql
-- Big Apple Air Quality — Normalization Script
--
-- Prerequisites:
--   1. mysql_schema.sql has been run (database and tables exist).
--   2. The raw CSV has been imported into raw_air_quality via
--      MySQL Workbench Table Data Import Wizard.
--
-- This script:
--   1. Creates a cleaned view of raw_air_quality with proper types.
--   2. Populates the four dimension tables.
--   3. Populates the measurements fact table.
--   4. Runs validation row-count queries.
-- =============================================================================

USE big_apple_air_quality;


-- =============================================================================
-- STEP 1: Create a cleaned view
-- Casts all columns to correct types and trims whitespace.
-- Rows where unique_id_raw is not a number are excluded.
-- =============================================================================
CREATE OR REPLACE VIEW clean_air_quality AS
SELECT
    CAST(TRIM(unique_id_raw)    AS UNSIGNED)       AS unique_id,
    CAST(TRIM(indicator_id_raw) AS UNSIGNED)       AS indicator_id,
    TRIM(name)                                     AS name,
    TRIM(measure)                                  AS measure,
    COALESCE(NULLIF(TRIM(measure_info), ''), '')   AS measure_info,
    TRIM(geo_type_name)                            AS geo_type_name,
    TRIM(geo_join_id)                              AS geo_join_id,
    TRIM(geo_place_name)                           AS geo_place_name,
    TRIM(time_period)                              AS time_period,
    CASE
        WHEN NULLIF(TRIM(start_date_raw), '') IS NULL THEN NULL
        ELSE STR_TO_DATE(TRIM(start_date_raw), '%m/%d/%Y')
    END                                            AS start_date,
    CASE
        WHEN NULLIF(TRIM(data_value_raw), '') IS NULL THEN NULL
        ELSE CAST(TRIM(data_value_raw) AS DECIMAL(12, 4))
    END                                            AS data_value,
    NULLIF(TRIM(message), '')                      AS message
FROM raw_air_quality
WHERE TRIM(unique_id_raw) REGEXP '^[0-9]+$';


-- =============================================================================
-- STEP 2: Populate indicators
-- Each unique combination of indicator_id / name / measure / measure_info
-- becomes one row.
-- =============================================================================
INSERT IGNORE INTO indicators (indicator_id, name, measure, measure_info)
SELECT DISTINCT
    indicator_id,
    name,
    measure,
    measure_info
FROM clean_air_quality
WHERE indicator_id IS NOT NULL
  AND name         IS NOT NULL
  AND measure      IS NOT NULL;


-- =============================================================================
-- STEP 3: Populate geo_types
-- =============================================================================
INSERT IGNORE INTO geo_types (geo_type_name)
SELECT DISTINCT geo_type_name
FROM clean_air_quality
WHERE NULLIF(geo_type_name, '') IS NOT NULL;


-- =============================================================================
-- STEP 4: Populate locations
-- Joins to geo_types to resolve the foreign key.
-- =============================================================================
INSERT IGNORE INTO locations (geo_join_id, geo_place_name, geo_type_id)
SELECT DISTINCT
    c.geo_join_id,
    c.geo_place_name,
    gt.geo_type_id
FROM clean_air_quality c
JOIN geo_types gt ON gt.geo_type_name = c.geo_type_name
WHERE NULLIF(c.geo_join_id,    '') IS NOT NULL
  AND NULLIF(c.geo_place_name, '') IS NOT NULL;


-- =============================================================================
-- STEP 5: Populate time_periods
-- =============================================================================
INSERT IGNORE INTO time_periods (time_period, start_date, year_value)
SELECT DISTINCT
    time_period,
    start_date,
    YEAR(start_date)
FROM clean_air_quality
WHERE NULLIF(time_period, '') IS NOT NULL;


-- =============================================================================
-- STEP 6: Populate measurements
-- Resolves all four foreign keys via joins, then inserts one row per record.
-- =============================================================================
INSERT IGNORE INTO measurements
    (unique_id, indicator_key, location_id, time_period_id, data_value, message)
SELECT
    c.unique_id,
    i.indicator_key,
    l.location_id,
    tp.time_period_id,
    c.data_value,
    c.message
FROM clean_air_quality c
JOIN indicators  i  ON  i.indicator_id = c.indicator_id
                    AND i.name         = c.name
                    AND i.measure      = c.measure
                    AND i.measure_info = c.measure_info
JOIN geo_types   gt ON  gt.geo_type_name = c.geo_type_name
JOIN locations   l  ON  l.geo_join_id    = c.geo_join_id
                    AND l.geo_place_name = c.geo_place_name
                    AND l.geo_type_id    = gt.geo_type_id
JOIN time_periods tp ON tp.time_period   = c.time_period
                    AND (
                            tp.start_date = c.start_date
                         OR (tp.start_date IS NULL AND c.start_date IS NULL)
                        );


-- =============================================================================
-- VALIDATION: Row counts for all tables
-- Compare raw_air_quality vs measurements to confirm all rows transferred.
-- =============================================================================
SELECT 'raw_air_quality' AS table_name, COUNT(*) AS row_count FROM raw_air_quality
UNION ALL
SELECT 'indicators',   COUNT(*) FROM indicators
UNION ALL
SELECT 'geo_types',    COUNT(*) FROM geo_types
UNION ALL
SELECT 'locations',    COUNT(*) FROM locations
UNION ALL
SELECT 'time_periods', COUNT(*) FROM time_periods
UNION ALL
SELECT 'measurements', COUNT(*) FROM measurements;
