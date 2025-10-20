select * from table1 PARTITION(part1) left join table2 PARTITION(part2) on table1.id = table2.id;
