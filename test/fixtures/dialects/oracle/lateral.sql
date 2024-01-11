-- inner join with a lateral
SELECT
    t1.id,
    t2.id AS t2_id,
    t2.col1
FROM tbl1 t1
INNER JOIN
    LATERAL (SELECT
        id,
        col1
    FROM tbl2) t2
    ON t1.id = t2.id;

-- cross join with a lateral
SELECT
    t1.id,
    t2.id AS t2_id,
    t2.col1
FROM tbl1 t1
CROSS JOIN
    LATERAL (
        SELECT
            id,
            col1
        FROM tbl2
    ) t2;


-- comma cross join with a lateral
SELECT
    t1.id,
    t2.id AS t2_id,
    t2.col1
FROM tbl1 t1,
    LATERAL (SELECT
        id,
        col1
    FROM tbl2) t2;
