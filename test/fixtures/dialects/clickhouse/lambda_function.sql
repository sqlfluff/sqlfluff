SELECT arrayFirst(x -> x = 2, [1, 1, 2, 2]);

SELECT arrayFirst(x, y -> x != y, [1, 1, 2, 2], [1, 2, 2, 3]);
