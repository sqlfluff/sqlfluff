-- Variable substitution with `spark.sql.variable.substitute` enabled.
-- https://spark.apache.org/docs/latest/configuration.html
SET foo=(1, 3);

SELECT *
FROM t
WHERE bar IN ${foo};

SELECT *
FROM t
WHERE bar NOT IN ${hivevar:foo};

SELECT
    a,
    ${col_name},
    b + ${spark.sql.shuffle.partitions} AS c
FROM ${db}.t
WHERE d = ${env:USER_NAME};
