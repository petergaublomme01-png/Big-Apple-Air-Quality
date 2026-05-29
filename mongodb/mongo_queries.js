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

// QUESTION 2: How have major air quality indicators changed over time?
    // Custom Analytical Query: Filter to major pollutants, group by pollutant and year, sorted and reshaped.
    db.air_quality.aggregate([

  // STEP 1: Filter to major pollutants
  {
    $match: {
      name: /PM 2.5|Ozone|NO2/i
    }
  },

  // STEP 2: Group by pollutant and year
  {
    $group: {
      _id: {
        pollutant: "$name",
        period: "$time_period"
      },
      avg_value: {
        $avg: "$data_value"
      }
    }
  },

  // STEP 3: Sort chronologically
  {
    $sort: {
      "_id.period": 1
    }
  },

  // STEP 4: Reshape output
  {
    $project: {
      pollutant: "$_id.pollutant",
      year: "$_id.period",
      avg_value: 1,
      _id: 0
    }
  }

])

// QUESTION 3: Which neighborhoods have the highest pollution-related health impacts?

    // Basic Filter + Aggregation: 
    // Find health impacts (asthma, hospitalizations,etc)
    //  Group by neighborhood and calculate average health impact and sort

    db.air_quality.aggregate([
  {
    $match: {
      name: /asthma|hospitalization|death/i,
      geo_type_name: "UHF42"
    }
  },
  {
    $group: {
      _id: "$geo_place_name",
      avg_health_impact: { $avg: "$data_value" }
    }
  },
  {
    $sort: {
      avg_health_impact: -1
    }
  }
])

// QUESTION 4: Which areas appear to have both high pollutant levels and high health-impact rates?
    // Complex Aggregation: Self-join equivalent, combining pollution and health data

    // STEP 1: Create pollution-only collection using UHF42 neighborhoods

db.air_quality.aggregate([

  {
    $match: {
      geo_type_name: "UHF42",
      name: /PM 2.5|Ozone|NO2/i
    }
  },

  {
    $out: "pollution_data"
  }

])


// STEP 2: Create health-only collection using UHF42 neighborhoods

db.air_quality.aggregate([

  {
    $match: {
      geo_type_name: "UHF42",
      name: /asthma|hospitalization|death/i
    }
  },

  {
    $out: "health_data"
  }

])


// STEP 3: Join pollution and health collections together
// using UHF42 neighborhood IDs

db.pollution_data.aggregate([

  {
    $lookup: {
      from: "health_data",
      localField: "geo_join_id",
      foreignField: "geo_join_id",
      as: "health_stats"
    }
  }

])


// STEP 4: Better analytical version
// Average pollution + related health data by UHF42 area

db.pollution_data.aggregate([

  // Group pollution values by UHF42 neighborhood
  {
    $group: {
      _id: {
        uhf42_id: "$geo_join_id",
        neighborhood: "$geo_place_name"
      },

      avg_pollution: {
        $avg: "$data_value"
      }
    }
  },

  // Join matching health records
  {
    $lookup: {
      from: "health_data",
      localField: "_id.uhf42_id",
      foreignField: "geo_join_id",
      as: "health_stats"
    }
  },

  // Calculate average health impact
  {
    $addFields: {

      avg_health_impact: {
        $avg: "$health_stats.data_value"
      }

    }
  },

  // Sort areas with highest pollution and health impacts
  {
    $sort: {
      avg_pollution: -1,
      avg_health_impact: -1
    }
  },

  // Clean up output
  {
    $project: {
      _id: 0,
      neighborhood: "$_id.neighborhood",
      uhf42_id: "$_id.uhf42_id",
      avg_pollution: 1,
      avg_health_impact: 1
    }
  }

])