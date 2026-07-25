-- DuckDB `USING SAMPLE` / `TABLESAMPLE` table sampling.
-- https://duckdb.org/docs/stable/sql/samples

-- Percentage samples.
SELECT * FROM addresses USING SAMPLE 10%;
SELECT * FROM addresses USING SAMPLE 10 PERCENT;

-- Fixed-size (row count) sample.
SELECT * FROM addresses USING SAMPLE 100 ROWS;

-- Sampling method applied to a size.
SELECT * FROM addresses USING SAMPLE reservoir(20%);
SELECT * FROM addresses USING SAMPLE bernoulli(10%);
SELECT * FROM addresses USING SAMPLE reservoir(500 ROWS) REPEATABLE (100);

-- Size with an explicit method and seed.
SELECT * FROM addresses USING SAMPLE 10% (system, 377);
SELECT * FROM addresses USING SAMPLE 10 ROWS (reservoir, 354);

-- `TABLESAMPLE` is an accepted synonym.
SELECT * FROM addresses TABLESAMPLE 10%;
SELECT * FROM addresses TABLESAMPLE bernoulli(10);

-- Sampling combined with a join (the sample applies to the sampled table).
SELECT *
FROM addresses USING SAMPLE 10%
JOIN cities USING (city_id);
