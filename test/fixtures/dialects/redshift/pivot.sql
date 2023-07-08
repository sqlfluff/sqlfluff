-- redshift_pivot.sql
/* Examples of SELECT statements that include PIVOT expressions. */

-- Below examples come from
-- https://docs.aws.amazon.com/redshift/latest/dg/r_FROM_clause-pivot-unpivot-examples.html
SELECT *
FROM (SELECT
    partname,
    price
    FROM part) PIVOT (
    AVG(price) FOR partname IN ('P1', 'P2', 'P3')
);

SELECT *
FROM (SELECT
    quality,
    manufacturer
    FROM part) PIVOT (
    COUNT(*) FOR quality IN (1, 2, NULL)
);

SELECT *
FROM (SELECT
    quality,
    manufacturer
    FROM part) PIVOT (
    COUNT(*) AS count FOR quality IN (1 AS high, 2 AS low, NULL AS na)
);
-- End of AWS-provided examples

-- Can do PIVOTs for CTEs
WITH bear_diet AS (
    SELECT
        bear_id,
        bear_species,
        food_eaten
    FROM bear_facts
)

SELECT *
FROM bear_diet
PIVOT ( COUNT(*) AS num_ate_food
    FOR bear_species IN (
        'polar bear',
        'brown bear',
        'american black bear',
        'asian black bear',
        'giant panda',
        'spectacled bear',
        'sloth bear',
        'sun bear'
    )
);

-- Can do Pivots for tables
SELECT *
FROM orders PIVOT (COUNT(*) FOR color IN ('red', 'blue'));

-- Can also alias the pivoted table
SELECT *
FROM (SELECT
    quality,
    manufacturer
    FROM part) PIVOT (
    COUNT(*) FOR quality IN (1, 2, NULL)
) AS quality_matrix;
