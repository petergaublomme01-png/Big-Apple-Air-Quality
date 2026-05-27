-- =============================================================================
-- mysql_schema.sql
-- Big Apple Air Quality — MySQL Database Schema
--
-- Run this file in MySQL Workbench BEFORE importing any data.
-- It will drop and recreate the database and all tables from scratch.
-- =============================================================================

DROP DATABASE IF EXISTS big_apple_air_quality;

CREATE DATABASE big_apple_air_quality
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE big_apple_air_quality;


-- -----------------------------------------------------------------------------
-- STAGING TABLE
-- All columns are VARCHAR/TEXT so MySQL Workbench can import the CSV without
-- any type errors. Normalization happens in mysql_normalize.sql.
-- -----------------------------------------------------------------------------
CREATE TABLE raw_air_quality (
    unique_id_raw     VARCHAR(50),
    indicator_id_raw  VARCHAR(50),
    name              VARCHAR(255),
    measure           VARCHAR(255),
    measure_info      VARCHAR(100),
    geo_type_name     VARCHAR(100),
    geo_join_id       VARCHAR(50),
    geo_place_name    VARCHAR(255),
    time_period       VARCHAR(100),
    start_date_raw    VARCHAR(100),
    data_value_raw    VARCHAR(50),
    message           TEXT
);


-- -----------------------------------------------------------------------------
-- NORMALIZED TABLES
-- -----------------------------------------------------------------------------

-- Unique indicator types (e.g., "Fine particles (PM 2.5) | Mean | mcg/m3")
CREATE TABLE indicators (
    indicator_key  INT          NOT NULL AUTO_INCREMENT,
    indicator_id   INT          NOT NULL,
    name           VARCHAR(255) NOT NULL,
    measure        VARCHAR(255) NOT NULL,
    measure_info   VARCHAR(100) NOT NULL DEFAULT '',
    PRIMARY KEY (indicator_key),
    UNIQUE KEY uq_indicator (indicator_id, name, measure, measure_info)
);

-- Geography classification types (e.g., Borough, UHF42, CD)
CREATE TABLE geo_types (
    geo_type_id   INT          NOT NULL AUTO_INCREMENT,
    geo_type_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (geo_type_id),
    UNIQUE KEY uq_geo_type (geo_type_name)
);

-- Named geographic places, linked to a geography type
CREATE TABLE locations (
    location_id    INT          NOT NULL AUTO_INCREMENT,
    geo_join_id    VARCHAR(50)  NOT NULL,
    geo_place_name VARCHAR(255) NOT NULL,
    geo_type_id    INT          NOT NULL,
    PRIMARY KEY (location_id),
    UNIQUE KEY uq_location (geo_join_id, geo_place_name, geo_type_id),
    CONSTRAINT fk_location_geo_type
        FOREIGN KEY (geo_type_id) REFERENCES geo_types (geo_type_id)
);

-- Distinct time periods with parsed dates
CREATE TABLE time_periods (
    time_period_id INT          NOT NULL AUTO_INCREMENT,
    time_period    VARCHAR(100) NOT NULL,
    start_date     DATE,
    year_value     INT,
    PRIMARY KEY (time_period_id),
    UNIQUE KEY uq_time_period (time_period, start_date)
);

-- One row per measurement; links all four dimension tables
CREATE TABLE measurements (
    unique_id      INT             NOT NULL,
    indicator_key  INT             NOT NULL,
    location_id    INT             NOT NULL,
    time_period_id INT             NOT NULL,
    data_value     DECIMAL(12, 4),
    message        TEXT,
    PRIMARY KEY (unique_id),
    CONSTRAINT fk_meas_indicator
        FOREIGN KEY (indicator_key)  REFERENCES indicators  (indicator_key),
    CONSTRAINT fk_meas_location
        FOREIGN KEY (location_id)    REFERENCES locations   (location_id),
    CONSTRAINT fk_meas_time
        FOREIGN KEY (time_period_id) REFERENCES time_periods (time_period_id),
    CONSTRAINT chk_data_value
        CHECK (data_value IS NULL OR data_value >= 0)
);


-- -----------------------------------------------------------------------------
-- INDEXES
-- These speed up the most common join and filter patterns.
-- -----------------------------------------------------------------------------
CREATE INDEX idx_measurements_indicator ON measurements (indicator_key);
CREATE INDEX idx_measurements_location  ON measurements (location_id);
CREATE INDEX idx_measurements_time      ON measurements (time_period_id);
CREATE INDEX idx_locations_geo_type     ON locations    (geo_type_id);
