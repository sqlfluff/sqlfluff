DELETE a FROM a JOIN b USING (id) WHERE b.name = 'example';

DELETE FROM somelog WHERE user = 'jcole'
ORDER BY timestamp_column LIMIT 1;

DELETE LOW_PRIORITY QUICK IGNORE a FROM a JOIN b USING (id) WHERE b.name = 'example';

DELETE FROM a PARTITION (p) WHERE b.name = 'example';

-- Multiple-Table Syntax 1
DELETE t1, t2 FROM t1 INNER JOIN t2 INNER JOIN t3
WHERE t1.id=t2.id AND t2.id=t3.id;

DELETE LOW_PRIORITY QUICK IGNORE t1, t2 FROM t1 INNER JOIN t2 INNER JOIN t3
WHERE t1.id=t2.id AND t2.id=t3.id;

-- Multiple-Table Syntax 2
DELETE FROM t1, t2 USING t1 INNER JOIN t2 INNER JOIN t3
WHERE t1.id=t2.id AND t2.id=t3.id;

DELETE LOW_PRIORITY QUICK IGNORE FROM t1, t2 USING t1 INNER JOIN t2 INNER JOIN t3
WHERE t1.id=t2.id AND t2.id=t3.id;

DELETE a1, a2 FROM t1 AS a1 INNER JOIN t2 AS a2
WHERE a1.id=a2.id;

-- .* after table name
DELETE t1.*, t2.* FROM t1 INNER JOIN t2 INNER JOIN t3
WHERE t1.id=t2.id AND t2.id=t3.id;

DELETE FROM t1.*, t2.* USING t1 INNER JOIN t2 INNER JOIN t3
WHERE t1.id=t2.id AND t2.id=t3.id;
