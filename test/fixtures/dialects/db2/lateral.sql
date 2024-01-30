-- comma cross join with a lateral
SELECT
    X.NUM,
    D.MY_COL
FROM MY_SCHEMA.MY_TABLE AS D,
LATERAL (VALUES 0, 1) AS X (NUM);

SELECT X.NUM
FROM LATERAL (values (0), (1)) AS X (NUM);
