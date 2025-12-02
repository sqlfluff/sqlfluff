SELECT
    region,
    city,
    grouping(region, city) AS grp_idx,
    count(DISTINCT id) AS num_total,
    count(DISTINCT id) FILTER (WHERE is_poi) AS num_poi,
    count(DISTINCT id) FILTER (WHERE is_gov) AS num_gov
FROM location_data
GROUP BY GROUPING SETS ( (region), (city), (region, city), () );

SELECT
    region,
    city,
    grouping(region, city) AS grp_idx,
    count(DISTINCT id) AS num_total,
    count(DISTINCT id) FILTER (WHERE is_poi) AS num_poi,
    count(DISTINCT id) FILTER (WHERE is_gov) AS num_gov
FROM location_data
GROUP BY ROLLUP ( (region), (city) );

SELECT
    region,
    city,
    grouping(region, city) AS grp_idx,
    count(DISTINCT id) AS num_total,
    count(DISTINCT id) FILTER (WHERE is_poi) AS num_poi,
    count(DISTINCT id) FILTER (WHERE is_gov) AS num_gov
FROM location_data
GROUP BY CUBE ( (region), (city) );
