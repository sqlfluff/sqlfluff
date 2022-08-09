SELECT
 field_1,
 field_2,
 column_value
FROM my_table
CROSS JOIN UNNEST(array_field) AS my_unnested_table(column_value);
