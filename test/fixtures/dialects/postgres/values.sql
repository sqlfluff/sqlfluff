values (1, 2);

VALUES (1+1, 2);

values (1+1, 2::TEXT);

values (1, 2), (3, 4);

values (1, 2), (3, 4), (greatest(5, 6), least(7, 8));

values (1, 2), (3, 4) limit 1;

values (1, 2), (3, 4) limit 1 offset 1;

values (1, 2), (3, 4) order by 1 desc;

values (1, 2), (3, 4) order by 1 desc limit 1;
