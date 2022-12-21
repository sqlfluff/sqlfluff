-- ansi_cast_with_whitespaces.sql
/* Several valid queries where there is whitespace surrounding the ANSI
cast operator (::) */

-- query from https://github.com/sqlfluff/sqlfluff/issues/2720
SELECT amount_of_honey :: FLOAT
FROM bear_inventory;


-- should be able to support an arbitrary amount of whitespace
SELECT amount_of_honey        ::        FLOAT
FROM bear_inventory;

SELECT amount_of_honey::    FLOAT
FROM bear_inventory;

SELECT amount_of_honey        ::FLOAT
FROM bear_inventory;

-- should support a wide variety of typecasts
SELECT amount_of_honey :: time
FROM bear_inventory;

SELECT amount_of_honey :: text
FROM bear_inventory;

SELECT amount_of_honey     :: VARCHAR( 512 )
FROM bear_inventory;

SELECT amount_of_honey ::        TIMESTAMPTZ
FROM bear_inventory;

SELECT amount_of_honey    ::        TIMESTAMP WITHOUT TIME ZONE
FROM bear_inventory;

-- should support casts with arbitrary amount of whitespace in join statements
SELECT
    bi.amount_of_honey
FROM bear_inventory bi
LEFT JOIN favorite_cola fc
    ON fc.bear_id ::   VARCHAR(512) = bi.bear_id    ::VARCHAR(512)
WHERE fc.favorite_cola = 'RC Cola';
