-- lambda functions
SELECT list_transform([4, 5, 6], x -> x + 1);

SELECT list_filter([4, 5, 6], x -> x > 4);

-- nested lambda functions
SELECT list_transform(
    list_filter([0, 1, 2, 3, 4, 5], x -> x % 2 = 0),
    y -> y * y
);

-- lambda with index
SELECT list_filter([1, 3, 1, 5], (x, i) -> x > i);

-- new lambda syntax, introduced in v1.3
SELECT list_transform([4, 5, 6], lambda x: x + 1);
