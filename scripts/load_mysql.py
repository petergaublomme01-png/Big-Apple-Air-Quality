# scripts/load_mysql.py
# Placeholder: Load cleaned CSV data into MySQL.
# Complete this script after running mysql_schema.sql and mysql_normalize.sql.
#
# Usage:
#   1. Copy this note: create a .env file in the project root with the variables below.
#   2. Run:  python scripts/load_mysql.py
#
# Required .env variables:
#   DB_HOST      - MySQL host, e.g. localhost
#   DB_USER      - MySQL username, e.g. root
#   DB_PASSWORD  - MySQL password
#   DB_NAME      - Database name, e.g. big_apple_air_quality

import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME     = os.getenv("DB_NAME", "big_apple_air_quality")

# TODO: Implement loading logic here.
#
# Example approach using mysql-connector-python:
#
#   import mysql.connector
#   import pandas as pd
#
#   conn = mysql.connector.connect(
#       host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
#   )
#   cursor = conn.cursor()
#   df = pd.read_csv("data/cleaned/air_quality_cleaned.csv")
#
#   for _, row in df.iterrows():
#       cursor.execute(
#           "INSERT IGNORE INTO raw_air_quality VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
#           tuple(row)
#       )
#   conn.commit()
#   cursor.close()
#   conn.close()

print("load_mysql.py: placeholder — complete this script after the SQL setup files are run.")
print(f"Target: {DB_USER}@{DB_HOST}/{DB_NAME}")
