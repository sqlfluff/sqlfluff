SELECT id FROM mytable qualify count(*) over (partition by id) > 1;
