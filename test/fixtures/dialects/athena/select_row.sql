SELECT ROW(1, 2.0);

SELECT CAST(ROW(1, 2.0) AS ROW(x BIGINT, y DOUBLE));

SELECT ARRAY[CAST(ROW(1) AS ROW(x INT))][1].x;

SELECT
    CAST(
        ROW(
            ARRAY[
                CAST(ROW('') AS ROW(id varchar))
            ],
            CAST(ROW('') AS ROW(id varchar)),
            'Approved'
        ) AS ROW(
            approvers ARRAY<ROW(id varchar)>,
            performer ROW(id varchar),
            approvalStatus varchar
        )
    ) as test;

