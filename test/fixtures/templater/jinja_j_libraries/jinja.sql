SELECT 56
FROM {{ foo.schema }}.{{ table_proxy("xyz") }}
WHERE {{ bar.equals("x", 23) }}
