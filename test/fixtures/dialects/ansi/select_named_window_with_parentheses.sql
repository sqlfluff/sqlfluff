SELECT
    NTH_VALUE(bar, 1) OVER(w1) AS baz,
    NTH_VALUE(bar, 1) OVER() AS foo
FROM t
WINDOW w1 AS (
    PARTITION BY
        x,
        y,
        z
    ORDER BY abc DESC
)
