SELECT
    FILTER(ident, i -> i:value > 0) as sample_filter,
    TRANSFORM(ident, j -> j:value) as sample_transform
FROM ref;

SELECT
    FILTER("ident", (i INT, j VARIANT) -> (i:value is not null and j:value = 'some_literal')) as sample_filter,
    TRANSFORM("ident", j -> j) as sample_transform,
    some_other_function('unusual arguments', x -> 'still a lambda expression', true) as sample_other
FROM ref;
