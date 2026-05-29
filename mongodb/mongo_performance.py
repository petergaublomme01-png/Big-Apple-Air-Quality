import time
import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["big_apple_air_quality"]
measurements = db["measurements"]

print("Connected to MongoDB")
print("Measurement documents:", measurements.count_documents({}))

# ============================================================
# SECTION 1: Create indexes
# ============================================================

measurements.create_index("indicator.indicator_id")
measurements.create_index("location.geo_place_name")
measurements.create_index("time.start_date")
measurements.create_index([("indicator.name", 1), ("location.geo_type_name", 1)])

print("\nCurrent indexes:")
for index in measurements.list_indexes():
    print(index)

# ============================================================
# SECTION 2: Runtime comparison for 3 queries
# ============================================================

pipeline1 = [
    {"$match": {
        "indicator.name": "Fine particles (PM 2.5)",
        "location.geo_type_name": "UHF42"
    }},
    {"$group": {
        "_id": "$location.geo_place_name",
        "average_pollution": {"$avg": "$data_value"},
        "count": {"$sum": 1}
    }},
    {"$sort": {"average_pollution": -1}},
    {"$limit": 10}
]

pipeline2 = [
    {"$match": {
        "indicator.name": {
            "$regex": "PM 2.5|Ozone|NO2",
            "$options": "i"
        }
    }},
    {"$group": {
        "_id": {
            "indicator": "$indicator.name",
            "time_period": "$time.time_period"
        },
        "average_value": {"$avg": "$data_value"}
    }},
    {"$sort": {
        "_id.time_period": 1,
        "_id.indicator": 1
    }},
    {"$project": {
        "_id": 0,
        "indicator": "$_id.indicator",
        "time_period": "$_id.time_period",
        "average_value": 1
    }}
]

pipeline3 = [
    {"$match": {
        "indicator.name": {
            "$regex": "asthma|hospitalization|death",
            "$options": "i"
        },
        "location.geo_type_name": "UHF42"
    }},
    {"$group": {
        "_id": "$location.geo_place_name",
        "average_health_impact": {"$avg": "$data_value"},
        "count": {"$sum": 1}
    }},
    {"$sort": {"average_health_impact": -1}},
    {"$limit": 10}
]

def time_query(label, pipeline):
    start = time.time()
    results = list(measurements.aggregate(pipeline))
    end = time.time()

    runtime = end - start
    print(f"\n{label} runtime: {runtime:.6f} seconds")
    print(pd.DataFrame(results).head(10))

    return runtime

runtime1 = time_query("Query 1: Top PM2.5 neighborhoods", pipeline1)
runtime2 = time_query("Query 2: Air quality indicators over time", pipeline2)
runtime3 = time_query("Query 3: Health impact neighborhoods", pipeline3)

# ============================================================
# SECTION 3: MongoDB explain output
# ============================================================

print("\nMongoDB explain output for Query 1:")

explain_output = db.command(
    "explain",
    {
        "aggregate": "measurements",
        "pipeline": pipeline1,
        "cursor": {}
    },
    verbosity="executionStats"
)

print(explain_output)

# ============================================================
# SECTION 4: Summary table
# ============================================================

summary = pd.DataFrame({
    "Query": [
        "Top PM2.5 neighborhoods",
        "Air quality indicators over time",
        "Health impact neighborhoods"
    ],
    "MongoDB Runtime Seconds": [
        runtime1,
        runtime2,
        runtime3
    ]
})

print("\nRuntime summary:")
print(summary)