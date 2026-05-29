import pandas as pd
from pymongo import MongoClient

# Load CSV
df = pd.read_csv("data/cleaned/air_quality_cleaned.csv")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

db = client["big_apple_air_quality"]

measurements_collection = db["measurements"]
indicators_collection = db["indicators"]

# Optional: clear old data
measurements_collection.delete_many({})
indicators_collection.delete_many({})

# -----------------------------
# CREATE MEASUREMENTS DOCUMENTS
# -----------------------------

measurement_docs = []

for _, row in df.iterrows():

    doc = {
        "unique_id": int(row["unique_id"]),

        "data_value": (
            float(row["data_value"])
            if pd.notna(row["data_value"])
            else None
        ),

        "message": (
            row["message"]
            if pd.notna(row["message"])
            else None
        ),

        "indicator": {
            "indicator_id": int(row["indicator_id"]),
            "name": row["name"],
            "measure": row["measure"],
            "measure_info": row["measure_info"]
        },

        "location": {
            "geo_type_name": row["geo_type_name"],
            "geo_join_id": row["geo_join_id"],
            "geo_place_name": row["geo_place_name"]
        },

        "time": {
            "time_period": row["time_period"],
            "start_date": row["start_date"]
        }
    }

    measurement_docs.append(doc)

# Insert into MongoDB
measurements_collection.insert_many(measurement_docs)

print(f"Inserted {len(measurement_docs)} measurement documents")

# -----------------------------
# CREATE INDICATORS COLLECTION
# -----------------------------

indicator_df = df[
    [
        "indicator_id",
        "name",
        "measure",
        "measure_info"
    ]
].drop_duplicates()

indicator_docs = []

for _, row in indicator_df.iterrows():

    doc = {
        "indicator_id": int(row["indicator_id"]),
        "name": row["name"],
        "measure": row["measure"],
        "measure_info": row["measure_info"]
    }

    indicator_docs.append(doc)

# Insert indicators
indicators_collection.insert_many(indicator_docs)

print(f"Inserted {len(indicator_docs)} indicator documents")

print("Done!")
