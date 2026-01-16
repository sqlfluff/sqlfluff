-- Simplified PIVOT
-- Examples from https://duckdb.org/docs/sql/statements/pivot
PIVOT Cities ON Year USING sum(Population);

PIVOT Cities ON Year USING first(Population);

PIVOT Cities ON Year USING sum(Population) GROUP BY Country;

PIVOT Cities ON Year IN (2000, 2010) USING sum(Population) GROUP BY Country;

PIVOT Cities ON Country, Name USING sum(Population);

PIVOT Cities ON Country || '_' || Name USING sum(Population);

PIVOT Cities ON Year USING sum(Population) AS total, max(Population) AS max GROUP BY Country;

PIVOT Cities ON Year USING sum(Population) GROUP BY Country, Name;

PIVOT Cities ON Year USING sum(Population) GROUP BY Country, Name ORDER BY Name;

PIVOT Cities ON Year USING sum(Population) GROUP BY Country, Name LIMIT 1;

PIVOT Cities ON Year USING sum(Population) GROUP BY Country, Name ORDER BY Name LIMIT 1;

-- Without ON
PIVOT Cities USING sum(Population) GROUP BY Country, Name;

-- Only ON
PIVOT Cities ON Year;

-- Only USING
PIVOT Cities USING sum(Population);

-- Only GROUP BY
PIVOT Cities GROUP BY Country, Name;

-- In a CTE
WITH pivot_alias AS (
    PIVOT Cities ON Year USING sum(Population) GROUP BY Country
)
SELECT * FROM pivot_alias;

-- In a subquery
SELECT *
FROM (
    PIVOT Cities ON Year USING sum(Population) GROUP BY Country
) pivot_alias;

-- Multiple pivots with a join
FROM (PIVOT Cities ON Year USING sum(Population) GROUP BY Country) year_pivot
JOIN (PIVOT Cities ON Name USING sum(Population) GROUP BY Country) name_pivot
USING (Country);

-- Test trailing comma
PIVOT Cities ON Year IN (2000, 2010,) USING sum(Population) GROUP BY Country;

PIVOT cities
ON country, name,
USING sum(population);

-- Multiple using expressions
PIVOT cities
ON year
USING sum(population) AS total, max(population) AS max,
GROUP BY country;

-- Standard PIVOT
FROM Cities
PIVOT (
    sum(Population)
    FOR
        Year IN (2000, 2010, 2020)
    GROUP BY Country
);

FROM Cities
PIVOT (
    sum(Population) AS total,
    count(Population) AS count
    FOR
        Year IN (2000, 2010)
        Country in ('NL', 'US')
);

FROM Cities
PIVOT (
    sum(Population) AS total,
    count(Population) AS count,
    FOR
        Year IN (2000, 2010,)
        Country in ('NL', 'US',)
);
