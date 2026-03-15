select 10 // 5;

SELECT * FROM capitals UNION BY NAME SELECT * FROM weather;

SELECT * FROM capitals UNION ALL BY NAME SELECT * FROM weather;

-- Verify that single underscores are parsed as numeric literals
SELECT 1_000;
SELECT 1_000_000;
SELECT 1.0_000;
SELECT 1_000_000.0_000_000;

SELECT *,
FROM (VALUES ('Amsterdam', 1),
('London', 2),
) cities(name, id);
