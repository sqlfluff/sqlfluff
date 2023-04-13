SELECT map();

WITH dataset AS (
    SELECT map(
        ARRAY['first', 'last', 'age'],
        ARRAY['Bob', 'Smith', '35']
    ) AS a_map
)

SELECT a_map FROM dataset;

SELECT map_filter(map(ARRAY[], ARRAY[]), (k, v) -> true);
-- -- {}

SELECT map_filter(
    map(
        ARRAY[10, 20, 30],
        ARRAY['a', null, 'c']
    ),
    (k, v) -> v IS NOT NULL
);
-- -- {10 -> a, 30 -> c}

SELECT map_filter(
    map(
        ARRAY['k1', 'k2', 'k3'],
        ARRAY[20, 3, 15]
    ),
    (k, v) -> v > 10
);
