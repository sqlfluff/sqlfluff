SELECT CAST(:start_time AS DATE) AS d;

SELECT *
FROM t
WHERE a = :a AND b > :min_b
LIMIT :max_rows;

SELECT j:name, j:address:city, :param_value
FROM t
WHERE j:id > :min_id;
