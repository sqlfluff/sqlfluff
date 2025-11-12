-- Postgres should work with Unicode identifiers in various places

SELECT größe, länge FROM measurements;

SELECT
    width AS größe,
    height AS höhe
FROM dimensions;

SELECT 'Não' reativação FROM table1;

SELECT αλφα, βητα, γαμμα FROM greek_letters;

SELECT москва, санкт_петербург FROM cities;

SELECT field1 AS 名前 FROM users;

SELECT
    id,
    größe,
    description
FROM products;

WITH größen AS (
    SELECT * FROM base_table
)
SELECT * FROM größen;

CREATE TABLE größen (
    länge INTEGER,
    breite INTEGER
);
