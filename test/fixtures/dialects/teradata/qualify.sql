SELECT id FROM mytable qualify x = 1;

SELECT id FROM mytable qualify x = 1
UNION ALL
SELECT id FROM mytable qualify x = 1;

SELECT id FROM mytable qualify count(*) over (partition by id) > 1;
