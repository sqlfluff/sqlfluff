SELECT
    status
FROM
    orders
GROUP BY
    status
FETCH FIRST 3 ROWS ONLY
