with toto as (SELECT 1 as id, 'test' as name) SELECT * FROM toto LIMIT 1;

with toto as (SELECT 1 as id, 'test' as name) SELECT * FROM toto LIMIT 1 OFFSET 1;

with toto as (SELECT 1 as id, 'test' as name) SELECT * FROM toto LIMIT 1, 2;

with toto as (SELECT 1 as id, 'test' as name) SELECT * FROM toto LIMIT (1), (2);
