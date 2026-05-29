import time
import json
import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["big_apple_air_quality"]
measurements = db["measurements"]

print("Connected to MongoDB")
print("Measurement documents:", measurements.count_documents({}))

# ------------------------------------------------------------
# Drop existing indexes so we can test BEFORE indexing
# ------------------------------------------------------------

measurements.drop_indexes()
print("\nDropped non-_id indexes for before-index test.")

# ------------------------------------------------------------
# Define MongoDB aggregation queries
# ------------------------------------------------------------

pipeline1 = [
    {
        "$match": {
            "indicator.name": "Fine particles (PM 2.5)",
            "location.geo_type_name": "UHF42"
        }
    },
    {
        "$group": {
            "_id": "$location.geo_place_name",
            "average_pollution": {"$avg": "$data_value"},
            "count": {"$sum": 1}
        }
    },
    {"$sort": {"average_pollution": -1}},
    {"$limit": 10}
]

pipeline2 = [
    {
        "$match": {
            "indicator.name": {
                "$regex": "PM 2.5|Ozone|NO2",
                "$options": "i"
            }
        }
    },
    {
        "$group": {
            "_id": {
                "indicator": "$indicator.name",
                "time_period": "$time.time_period"
            },
            "average_value": {"$avg": "$data_value"}
        }
    },
    {
        "$sort": {
            "_id.time_period": 1,
            "_id.indicator": 1
        }
    },
    {
        "$project": {
            "_id": 0,
            "indicator": "$_id.indicator",
            "time_period": "$_id.time_period",
            "average_value": 1
        }
    }
]

pipeline3 = [
    {
        "$match": {
            "indicator.name": {
                "$regex": "asthma|hospitalization|death",
                "$options": "i"
            },
            "location.geo_type_name": "UHF42"
        }
    },
    {
        "$group": {
            "_id": "$location.geo_place_name",
            "average_health_impact": {"$avg": "$data_value"},
            "count": {"$sum": 1}
        }
    },
    {"$sort": {"average_health_impact": -1}},
    {"$limit": 10}
]

queries = {
    "Top PM2.5 neighborhoods": pipeline1,
    "Air quality indicators over time": pipeline2,
    "Health impact neighborhoods": pipeline3
}

# ------------------------------------------------------------
# Function to time queries
# ------------------------------------------------------------

def time_query(query_name, pipeline):
    start = time.time()
    results = list(measurements.aggregate(pipeline))
    end = time.time()

    runtime = end - start

    print(f"\n{query_name}")
    print(f"Runtime: {runtime:.6f} seconds")
    print(pd.DataFrame(results).head(10))

    return runtime

# ------------------------------------------------------------
# BEFORE INDEX RUNTIME TEST
# ------------------------------------------------------------

before_results = []

print("\n==============================")
print("BEFORE INDEX RUNTIME RESULTS")
print("==============================")

for query_name, pipeline in queries.items():
    runtime = time_query(query_name, pipeline)

    before_results.append({
        "Query": query_name,
        "Runtime_Before_Index": runtime
    })

before_runtime_df = pd.DataFrame(before_results)

before_runtime_df.to_csv(
    "mongo_runtime_before_index.csv",
    index=False
)

print("\nSaved:mongo_runtime_before_index.csv")
print(before_runtime_df)

# ------------------------------------------------------------
# CREATE INDEXES
# ------------------------------------------------------------

print("\n==============================")
print("CREATING INDEXES")
print("==============================")

measurements.create_index("indicator.indicator_id")
measurements.create_index("location.geo_place_name")
measurements.create_index("time.start_date")
measurements.create_index([
    ("indicator.name", 1),
    ("location.geo_type_name", 1)
])

print("\nCurrent indexes:")
for index in measurements.list_indexes():
    print(index)

# ------------------------------------------------------------
# AFTER INDEX RUNTIME TEST
# ------------------------------------------------------------

after_results = []

print("\n==============================")
print("AFTER INDEX RUNTIME RESULTS")
print("==============================")

for query_name, pipeline in queries.items():
    runtime = time_query(query_name, pipeline)

    after_results.append({
        "Query": query_name,
        "Runtime_After_Index": runtime
    })

after_runtime_df = pd.DataFrame(after_results)

after_runtime_df.to_csv(
    "mongo_runtime_after_index.csv",
    index=False
)

print("\nSaved: mongodb/mongo_runtime_after_index.csv")
print(after_runtime_df)

# ------------------------------------------------------------
# BEFORE VS AFTER INDEX COMPARISON
# ------------------------------------------------------------

comparison = before_runtime_df.merge(
    after_runtime_df,
    on="Query"
)

comparison["Improvement_Seconds"] = (
    comparison["Runtime_Before_Index"]
    - comparison["Runtime_After_Index"]
)

comparison["Percent_Improvement"] = (
    comparison["Improvement_Seconds"]
    / comparison["Runtime_Before_Index"]
) * 100

comparison.to_csv(
    "mongo_index_comparison.csv",
    index=False
)

print("\n==============================")
print("INDEX COMPARISON SUMMARY")
print("==============================")
print(comparison)
print("\nSaved: mongo_index_comparison.csv")

# ------------------------------------------------------------
# MONGODB EXPLAIN OUTPUT FOR QUERY 1
# ------------------------------------------------------------

print("\n==============================")
print("MONGODB EXPLAIN OUTPUT FOR QUERY 1")
print("==============================")

explain_output = db.command(
    "explain",
    {
        "aggregate": "measurements",
        "pipeline": pipeline1,
        "cursor": {}
    },
    verbosity="executionStats"
)

with open("mongo_explain_query1.json", "w") as f:
    json.dump(explain_output, f, indent=4, default=str)

print("Saved: mongo_explain_query1.json")



