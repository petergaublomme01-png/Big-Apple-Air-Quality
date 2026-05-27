// mongodb/mongo_setup.js
// Placeholder: MongoDB collection setup for Big Apple Air Quality.
// Complete this file during the MongoDB portion of the project.
//
// Planned steps:
//   1. Connect to MongoDB (local or Atlas)
//   2. Create database: big_apple_air_quality
//   3. Create collection: air_quality
//   4. Insert documents from the cleaned CSV (via mongoimport or a Python script)
//   5. Add indexes on indicator_id, geo_place_name, and start_date
//
// Example document structure:
// {
//   unique_id:      101,
//   indicator_id:   365,
//   name:           "Fine particles (PM 2.5)",
//   measure:        "Mean",
//   measure_info:   "mcg/m3",
//   geo_type_name:  "UHF42",
//   geo_join_id:    "101",
//   geo_place_name: "Kingsbridge - Riverdale",
//   time_period:    "Annual Average 2009",
//   start_date:     ISODate("2009-01-01"),
//   data_value:     8.6,
//   message:        null
// }
