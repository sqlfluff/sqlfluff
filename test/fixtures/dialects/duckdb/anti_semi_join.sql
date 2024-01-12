SELECT cars.name, cars.manufacturer
FROM cars SEMI JOIN region
ON cars.region = region.id;

SELECT cars.name, cars.manufacturer
FROM cars ANTI JOIN safety_data
ON cars.safety_report_id = safety_data.report_id;

SELECT cars.name, cars.manufacturer
FROM cars SEMI JOIN region
USING (region_id);

SELECT cars.name, cars.manufacturer
FROM cars ANTI JOIN region
USING (region_id);
