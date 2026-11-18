-- navigating into SUPER values with array accessors in the FROM clause
SELECT 1 FROM t AS a LEFT JOIN a.topic[0].extension AS x ON TRUE;

SELECT 1 FROM t AS a LEFT JOIN a.topic[0] AS x ON TRUE;

SELECT 1 FROM t AS a, a.arr[1].b[2].c AS y;

-- plain dotted paths still parse as before
SELECT 1 FROM t AS a LEFT JOIN a.topic.ext AS x ON TRUE;
