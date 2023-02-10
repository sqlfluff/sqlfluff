SELECT
    DATE(t), ROUND(b, 2),
    LEFT(right(s, 5), LEN(s + 6)) as compound
FROM tbl_b;

SELECT _custom_function(5) as test_column;
