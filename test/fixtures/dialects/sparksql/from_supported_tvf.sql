--TVFs that are supported in a `FROM` clause
--
-- range call with end
SELECT id FROM range(6 + cos(3));
SELECT id FROM range(5);

-- range call with start and end
SELECT id FROM range(5, 10);

-- range call with start, end and step
SELECT id FROM range(5, 10, 2);

-- range call with start, end, step, and numPartitions
SELECT id FROM range(0, 10, 2, 200);

-- range call with a table alias
SELECT test.id FROM range(5, 8) AS test;

SELECT test.id FROM range(5, 8) test;
