-- =============================================================================
-- mysql_performance.sql
-- Big Apple Air Quality — Query Performance Testing
--
-- Run these statements in MySQL Workbench AFTER mysql_normalize.sql completes.
-- Purpose: observe execution plans and measure the impact of indexes.
--
-- WARNING: Section 2 temporarily drops an index. Always execute the full
--          section so the index is recreated before you run other queries.
-- =============================================================================

USE big_apple_air_quality;


-- =============================================================================
-- SECTION 1: EXPLAIN for the PM2.5 filter query
-- Look at the "type", "key", and "rows" columns in the output.
-- A good result shows "ref" or "range" in type and uses an index in "key".
-- =============================================================================
EXPLAIN
SELECT
    l.geo_place_name,
    gt.geo_type_name,
    tp.time_period,
    tp.start_date,
    i.name,
    i.measure,
    m.data_value
FROM measurements  m
JOIN indicators    i  ON i.indicator_key   = m.indicator_key
JOIN locations     l  ON l.location_id     = m.location_id
JOIN geo_types     gt ON gt.geo_type_id    = l.geo_type_id
JOIN time_periods  tp ON tp.time_period_id = m.time_period_id
WHERE i.name LIKE '%PM2.5%'
  AND m.data_value IS NOT NULL
ORDER BY m.data_value DESC
LIMIT 20;


-- =============================================================================
-- SECTION 2: Before-and-after index comparison
--
-- This section drops idx_measurements_indicator, runs EXPLAIN without it,
-- then recreates it. This shows how much MySQL relies on that index.
--
-- WARNING: Execute all steps in this section. Do NOT stop after Step 3.
-- =============================================================================

-- Step 1: EXPLAIN *with* idx_measurements_indicator present (baseline)
-- Note the "key" and "rows" values before dropping the index.
EXPLAIN
SELECT
    m.unique_id,
    m.data_value,
    i.name
FROM measurements m
JOIN indicators i ON i.indicator_key = m.indicator_key
WHERE i.name LIKE '%PM2.5%';


-- Step 2: Drop the index
-- WARNING: Remember to run Steps 4 and 5 below to recreate it.
DROP INDEX idx_measurements_indicator ON measurements;


-- Step 3: EXPLAIN the same query WITHOUT the index
-- Compare "key" (likely NULL now) and "rows" (likely much higher) to Step 1.
EXPLAIN
SELECT
    m.unique_id,
    m.data_value,
    i.name
FROM measurements m
JOIN indicators i ON i.indicator_key = m.indicator_key
WHERE i.name LIKE '%PM2.5%';


-- Step 4: Recreate the index
-- IMPORTANT: Do not skip this step. Other queries depend on this index.
CREATE INDEX idx_measurements_indicator ON measurements (indicator_key);


-- Step 5: Confirm the index is restored — EXPLAIN should match Step 1 again.
EXPLAIN
SELECT
    m.unique_id,
    m.data_value,
    i.name
FROM measurements m
JOIN indicators i ON i.indicator_key = m.indicator_key
WHERE i.name LIKE '%PM2.5%';


-- =============================================================================
-- SECTION 3: Runtime comparison using MySQL profiling
--
-- Steps:
--   1. Run: SET profiling = 1;
--   2. Run each sample query below.
--   3. Run: SHOW PROFILES;  — this shows duration for each query.
--
-- You can repeat this after dropping/restoring an index to compare timings.
-- =============================================================================

SET profiling = 1;


-- Runtime Query A: Aggregation by indicator
SELECT
    i.name,
    COUNT(m.unique_id)            AS record_count,
    ROUND(AVG(m.data_value), 4)   AS avg_value
FROM measurements m
JOIN indicators i ON i.indicator_key = m.indicator_key
WHERE m.data_value IS NOT NULL
GROUP BY i.indicator_key, i.name;


-- Runtime Query B: Year-over-year PM2.5 trend
SELECT
    tp.year_value,
    ROUND(AVG(m.data_value), 4)   AS avg_pm25
FROM measurements  m
JOIN indicators    i  ON i.indicator_key   = m.indicator_key
JOIN time_periods  tp ON tp.time_period_id = m.time_period_id
WHERE i.name LIKE '%PM2.5%'
  AND m.data_value IS NOT NULL
  AND tp.year_value IS NOT NULL
GROUP BY tp.year_value
ORDER BY tp.year_value;


-- Runtime Query C: Average value by location and geography type
SELECT
    gt.geo_type_name,
    l.geo_place_name,
    ROUND(AVG(m.data_value), 4)   AS avg_value
FROM measurements m
JOIN locations  l  ON l.location_id  = m.location_id
JOIN geo_types  gt ON gt.geo_type_id = l.geo_type_id
WHERE m.data_value IS NOT NULL
GROUP BY gt.geo_type_id, l.location_id
ORDER BY avg_value DESC;


-- Show execution times for all queries run since SET profiling = 1
SHOW PROFILES;
