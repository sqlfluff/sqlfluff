SELECT
    a,
    b
FROM person where a IS DISTINCT FROM b;

SELECT
    a,
    b
FROM person where a IS NOT DISTINCT FROM b;
