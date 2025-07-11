CREATE FUNCTION mleast(VARIADIC arr numeric[]) RETURNS numeric AS $$
    SELECT min($1[i]) FROM generate_subscripts($1, 1) g(i);
$$ LANGUAGE SQL;

SELECT mleast(VARIADIC ARRAY[10, -1, 5, 4.4]);

SELECT mleast(VARIADIC ARRAY[]::numeric[]);

SELECT mleast(VARIADIC arr := ARRAY[10, -1, 5, 4.4]);

CREATE FUNCTION anyleast (VARIADIC anyarray) RETURNS anyelement AS $$
    SELECT min($1[i]) FROM generate_subscripts($1, 1) g(i);
$$ LANGUAGE SQL;

CREATE FUNCTION concat_values(text, VARIADIC anyarray) RETURNS text AS $$
    SELECT array_to_string($2, $1);
$$ LANGUAGE SQL;

SELECT my_function(other_function(
    VARIADIC ARRAY_REMOVE(ARRAY[
        a.value1,
        b.value2,
        c.value3
    ], NULL)
))
FROM a
FULL OUTER JOIN b USING (id)
FULL OUTER JOIN c USING (id);

SELECT json_extract_path_text(t.col::json, VARIADIC ARRAY['foo'::text])
FROM t;

SELECT my_function(VARIADIC ARRAY[
    CASE WHEN x > 0 THEN x ELSE 0 END,
    y + z,
    'literal'
]);

SELECT my_function(VARIADIC ARRAY(SELECT value FROM table1));
