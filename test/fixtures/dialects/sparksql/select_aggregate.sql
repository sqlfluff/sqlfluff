SELECT aggregate(array(1, 2, 3), 0, (acc, x) -> acc + x); -- 6
SELECT aggregate(array(1, 2, 3), 0, (acc, x) -> acc + x, acc -> acc * 10); -- 60
