WITH mycte AS (
    SELECT
        foo,
        bar
    FROM mytable1
)

UPDATE sometable
SET
    sometable.baz = mycte.bar
FROM
    mycte;
