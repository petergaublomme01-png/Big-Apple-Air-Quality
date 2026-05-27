-- =============================================================================
-- mysql_queries.sql
-- Big Apple Air Quality — Analytical Queries
--
-- Run each query individually in MySQL Workbench after mysql_normalize.sql
-- has been executed successfully.
-- =============================================================================

USE big_apple_air_quality;


-- =============================================================================
-- QUERY 1: Basic Filter
-- Question: Which locations recorded the highest PM2.5 values, and when?
-- Shows the top 20 PM2.5 measurements ranked by data value.
-- =============================================================================
SELECT
    l.geo_place_name                     AS location,
    gt.geo_type_name                     AS geography_type,
    tp.time_period,
    tp.start_date,
    i.name                               AS indicator,
    i.measure,
    i.measure_info                       AS unit,
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
-- QUERY 2: Aggregation
-- Question: What are the average, minimum, maximum, and record count for each
--           air quality indicator?
-- Useful for understanding the scale and spread of every indicator type.
-- =============================================================================
SELECT
    i.name                               AS indicator,
    i.measure,
    i.measure_info                       AS unit,
    COUNT(m.unique_id)                   AS record_count,
    ROUND(AVG(m.data_value), 4)          AS avg_value,
    ROUND(MIN(m.data_value), 4)          AS min_value,
    ROUND(MAX(m.data_value), 4)          AS max_value
FROM measurements m
JOIN indicators i ON i.indicator_key = m.indicator_key
WHERE m.data_value IS NOT NULL
GROUP BY i.indicator_key, i.name, i.measure, i.measure_info
ORDER BY avg_value DESC;


-- =============================================================================
-- QUERY 3: Join Query
-- Question: How do average pollution values compare across geography types,
--           locations, and indicators?
-- Joins all five normalized tables to produce a cross-referenced summary.
-- =============================================================================
SELECT
    gt.geo_type_name                     AS geography_type,
    l.geo_place_name                     AS location,
    i.name                               AS indicator,
    i.measure,
    COUNT(m.unique_id)                   AS record_count,
    ROUND(AVG(m.data_value), 4)          AS avg_value
FROM measurements  m
JOIN indicators    i  ON i.indicator_key  = m.indicator_key
JOIN locations     l  ON l.location_id    = m.location_id
JOIN geo_types     gt ON gt.geo_type_id   = l.geo_type_id
WHERE m.data_value IS NOT NULL
GROUP BY gt.geo_type_id, l.location_id, i.indicator_key
ORDER BY gt.geo_type_name, avg_value DESC;


-- =============================================================================
-- QUERY 4: Time-Based Analysis
-- Question: How have average PM2.5 levels changed year over year across NYC?
-- Groups all PM2.5 measurements by year and shows the trend over time.
-- =============================================================================
SELECT
    tp.year_value                        AS year,
    i.name                               AS indicator,
    i.measure,
    COUNT(m.unique_id)                   AS record_count,
    ROUND(AVG(m.data_value), 4)          AS avg_value,
    ROUND(MIN(m.data_value), 4)          AS min_value,
    ROUND(MAX(m.data_value), 4)          AS max_value
FROM measurements  m
JOIN indicators    i  ON i.indicator_key   = m.indicator_key
JOIN time_periods  tp ON tp.time_period_id = m.time_period_id
WHERE i.name LIKE '%PM2.5%'
  AND m.data_value IS NOT NULL
  AND tp.year_value IS NOT NULL
GROUP BY tp.year_value, i.indicator_key
ORDER BY tp.year_value ASC, i.name;


-- =============================================================================
-- QUERY 5: Custom Analytical Query
-- Question: Which NYC locations appear in BOTH the high-pollution list AND the
--           high-asthma-health-impact list?
-- Identifies neighborhoods where residents face a compounded environmental and
-- health burden. Uses two CTEs to rank each group separately, then joins them.
-- =============================================================================
WITH pollution_by_location AS (
    SELECT
        l.location_id,
        l.geo_place_name,
        ROUND(AVG(m.data_value), 4)  AS avg_pollution
    FROM measurements  m
    JOIN indicators    i ON i.indicator_key = m.indicator_key
    JOIN locations     l ON l.location_id   = m.location_id
    WHERE (i.name LIKE '%PM2.5%' OR i.name LIKE '%NO2%' OR i.name LIKE '%Ozone%')
      AND m.data_value IS NOT NULL
    GROUP BY l.location_id, l.geo_place_name
),
asthma_by_location AS (
    SELECT
        l.location_id,
        l.geo_place_name,
        ROUND(AVG(m.data_value), 4)  AS avg_health_impact
    FROM measurements  m
    JOIN indicators    i ON i.indicator_key = m.indicator_key
    JOIN locations     l ON l.location_id   = m.location_id
    WHERE i.name LIKE '%Asthma%'
      AND m.data_value IS NOT NULL
    GROUP BY l.location_id, l.geo_place_name
)
SELECT
    p.geo_place_name                     AS location,
    p.avg_pollution,
    a.avg_health_impact
FROM pollution_by_location  p
JOIN asthma_by_location     a ON a.location_id = p.location_id
ORDER BY p.avg_pollution DESC, a.avg_health_impact DESC;
