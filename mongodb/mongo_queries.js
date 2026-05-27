// QUESTION 1: Which NYC locations have the highest average air pollution values?
    // Basic filtering: Show all where indicator is "Fine particles (PM 2.5)"
db.measurements.find(
  {
    "indicator.name": "Fine particles (PM 2.5)"
  }
)
    // Aggregation: Group by UHF area (United Hospital Fund) and calculate average PM 2.5
db.measurements.aggregate([

  {
    $match: {
      "indicator.name": "Fine particles (PM 2.5)",
      "location.geo_type_name": "UHF42"
    }
  },

  {
    $group: {
      _id: "$location.geo_place_name",

      average_pollution: {
        $avg: "$data_value"
      }
    }
  },

  {
    $sort: {
      average_pollution: -1
    }
  },

  {
    $limit: 10
  }

])
