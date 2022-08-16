SELECT
    y AS woy
FROM
    UNNEST(GENERATE_ARRAY(1, 53)) AS y;

SELECT id, name
FROM
    UNNEST([1, 2, 3]) id WITH OFFSET pos1,
    UNNEST(['a', 'b', 'c']) name WITH OFFSET pos2
WHERE pos1 = pos2;
