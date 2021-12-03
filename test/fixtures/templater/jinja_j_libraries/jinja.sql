SELECT 56
FROM {{ foo.schema }}.{{ foo.table("xyz") }}
WHERE {{ bar.equals("x", 23) }} and {{ root_equals("y", 42) }}
