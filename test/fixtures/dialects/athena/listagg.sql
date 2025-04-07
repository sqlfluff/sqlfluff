SELECT
    composition.material_number AS material_number_composition,
    LISTAGG(
        composition.composition, ' || ' ON OVERFLOW ERROR
    ) WITHIN GROUP (
        ORDER BY composition ASC
    ) AS composition
FROM
    article_composition AS composition
GROUP BY composition.material_number;

SELECT
    country,
    LISTAGG(city, ',')
    WITHIN GROUP (
        ORDER BY population DESC
    )
    FILTER (WHERE population >= 10_000_000) AS megacities
FROM (
    VALUES
    ('India', 'Bangalore', 13_700_000),
    ('India', 'Chennai', 12_200_000),
    ('India', 'Ranchi', 1_547_000),
    ('Austria', 'Vienna', 1_897_000),
    ('Poland', 'Warsaw', 1_765_000)
) AS t (country, city, population)
GROUP BY country
ORDER BY country;

SELECT
    LISTAGG(value, ',' ON OVERFLOW TRUNCATE '.....' WITH COUNT) WITHIN GROUP (
        ORDER BY value
    )
FROM (VALUES 'a', 'b', 'c') AS t (value);

SELECT
    LISTAGG(
        value, ',' ON OVERFLOW TRUNCATE '.....' WITHOUT COUNT
    ) WITHIN GROUP (
        ORDER BY value
    )
FROM (VALUES 'a', 'b', 'c') AS t (value);
