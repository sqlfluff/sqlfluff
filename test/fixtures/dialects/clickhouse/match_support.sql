SELECT match('test', '^[0-9]+$')::bool;

WITH test as (SELECT '1' as id)
SELECT
    case when match(id, '^[0-9]*$')
        then id::Nullable(Float64)
    end as value_as_number
FROM test;

with toto as (SELECT '1' as id) SELECT * FROM toto WHERE match(id, '^[0-9]+$');
