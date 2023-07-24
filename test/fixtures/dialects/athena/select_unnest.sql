SELECT
 field_1,
 field_2,
 column_value
FROM my_table
CROSS JOIN UNNEST(array_field) AS my_unnested_table(column_value);

SELECT numbers, n, a
FROM (
  VALUES
    (ARRAY[2, 5]),
    (ARRAY[7, 8, 9])
) AS x (numbers)
CROSS JOIN UNNEST(numbers) WITH ORDINALITY AS t (n, a);
