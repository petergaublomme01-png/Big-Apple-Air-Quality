# MySQL Database Design and SQL Query Explanation

For the relational database portion of the project, we used MySQL to organize the NYC Air Quality and Health Impacts dataset into a normalized schema. The original dataset was a flat CSV file, so we first loaded it into a raw staging table called `raw_air_quality`. From there, we separated the data into related tables for indicators, geography types, locations, time periods, and measurements.

The main fact table is `measurements`. Each row in this table stores one numeric data value and connects to the rest of the database through foreign keys. The `indicators` table stores the type of measurement, such as PM2.5, nitrogen dioxide, ozone, asthma emergency department visits, hospitalizations, or deaths. The `geo_types` table stores geography categories, such as borough, UHF, or community district. The `locations` table stores specific NYC places, and the `time_periods` table stores the time period, start date, and year value.

This relational design works well for the project because our analytical questions require combining measurement values with indicator names, locations, geography types, and time periods. For example, the SQL queries join `measurements` to `indicators` and `locations` to find the highest average pollution values by location. They also join `measurements` to `time_periods` to analyze how major air quality indicators changed over time.

The MySQL schema includes primary keys for each table, foreign keys connecting the measurement table to the dimension tables, unique constraints to prevent duplicate records, and a check constraint requiring `data_value` to be nonnegative or null. We also added indexes on major join fields, including indicator, location, time period, and geography type, to support filtering, joins, and aggregation performance.

The four SQL outputs answer the team’s four core analytical questions. Q1 ranks NYC locations by average pollutant levels for PM2.5, nitrogen dioxide, and ozone. Q2 shows how major pollutant averages changed over time. Q3 identifies locations with the highest pollution-related health impacts. Q4 compares locations that have both PM2.5 pollution measurements and PM2.5-related asthma impact values.

These SQL outputs give the MongoDB team a direct basis for comparison because MongoDB is answering the same four analytical questions using a document database model. This allows the team to compare SQL and MongoDB in terms of query structure, runtime, indexing, and overall usefulness for the dataset.
