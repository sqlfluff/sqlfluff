-- redshift_unpivot.sql
/* Examples of SELECT statements that include UNPIVOT expressions. */

-- Below examples come from
-- https://docs.aws.amazon.com/redshift/latest/dg/r_FROM_clause-pivot-unpivot-examples.html
SELECT *
FROM (SELECT
    red,
    green,
    blue
    FROM count_by_color) UNPIVOT (
    cnt FOR color IN (red, green, blue)
);

SELECT *
FROM (
    SELECT
        red,
        green,
        blue
    FROM count_by_color
) UNPIVOT INCLUDE NULLS (
cnt FOR color IN (red, green, blue)
);


SELECT *
FROM count_by_color UNPIVOT (
    cnt FOR color IN (red, green, blue)
);

SELECT *
FROM count_by_color UNPIVOT (
    cnt FOR color IN (red AS r, green AS g, blue AS b)
);
-- Examples provided by AWS end here

-- Can do EXCLUDE NULLS as well
SELECT *
FROM (
    SELECT
        red,
        green,
        blue
    FROM count_by_color
) UNPIVOT EXCLUDE NULLS (
cnt FOR color IN (red, green, blue)
);

-- Can do this on CTEs
WITH subset_color_counts AS (
    SELECT
        red,
        green,
        blue
    FROM count_by_color
)

SELECT *
FROM subset_color_counts UNPIVOT (
    cnt FOR color IN (red, green, blue)
);

-- Can do this on tables
SELECT *
FROM count_by_color UNPIVOT (
    cnt FOR color IN (red, green, blue)
);

-- Can alias output of unpivot statement
SELECT *
FROM count_of_bears UNPIVOT (
    cnt FOR species IN (giant_panda, moon_bear)
) AS floofy_bears;
