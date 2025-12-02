(
    WITH mycte2 AS (
        WITH mycte1 AS (
            SELECT
                foo,
                bar,
                baz
            FROM mytable
        )
        SELECT
            foo,
            bar,
            baz
        FROM mycte1
    )
    SELECT
        foo,
        bar,
        baz
    FROM mycte2
);
