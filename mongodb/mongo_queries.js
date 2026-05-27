// mongodb/mongo_queries.js
// Placeholder: MongoDB analytical queries for Big Apple Air Quality.
// Complete this file during the MongoDB portion of the project.
//
// Planned queries (mirroring the MySQL queries for performance comparison):
//
// 1. Basic filter: highest PM2.5 values by location and time period
//    db.air_quality.find({ name: /PM2\.5/i }).sort({ data_value: -1 }).limit(20)
//
// 2. Aggregation: avg / min / max by indicator name
//    db.air_quality.aggregate([
//      { $match: { data_value: { $ne: null } } },
//      { $group: {
//          _id: { name: "$name", measure: "$measure" },
//          avg_value: { $avg: "$data_value" },
//          min_value: { $min: "$data_value" },
//          max_value: { $max: "$data_value" },
//          count:     { $sum: 1 }
//      }},
//      { $sort: { avg_value: -1 } }
//    ])
//
// 3. Location + geography type lookup
//    db.air_quality.aggregate([
//      { $group: {
//          _id: { geo_type: "$geo_type_name", location: "$geo_place_name", name: "$name" },
//          avg_value: { $avg: "$data_value" }
//      }},
//      { $sort: { avg_value: -1 } }
//    ])
//
// 4. Year-over-year PM2.5 trend
//    db.air_quality.aggregate([
//      { $match: { name: /PM2\.5/i, data_value: { $ne: null } } },
//      { $project: { year: { $year: "$start_date" }, data_value: 1 } },
//      { $group: { _id: "$year", avg_pm25: { $avg: "$data_value" } } },
//      { $sort: { _id: 1 } }
//    ])
//
// 5. Locations with both high pollution and asthma-related health impacts
//    (Requires $facet or a two-pass aggregation — to be designed during MongoDB phase)
