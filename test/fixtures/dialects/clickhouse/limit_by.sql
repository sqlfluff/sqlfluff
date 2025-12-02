with toto as (SELECT 1 as id, 'test' as name) SELECT * FROM toto LIMIT 1, 2 by id;

with toto as (SELECT 1 as id, 'test' as name) SELECT * FROM toto LIMIT 1 by id;

with toto as (SELECT 1 as id, 'test' as name) SELECT * FROM toto LIMIT 2 OFFSET 1 by id;

with toto as (SELECT 1 as id, 'test' as name) SELECT * FROM toto LIMIT 2, 1 by (id, name);
