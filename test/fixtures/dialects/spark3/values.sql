values (1, 2);
values (1, 2), (3, 4);
values (1, 2), (3, 4), (greatest(5, 6), least(7, 8));
values 1, 2;
values 1;

-- TODO: A VALUES clause can include LIMIT, ORDER BY specifiers just like a SELECT.
-- These are not yet implemented,
-- see https://github.com/sqlfluff/sqlfluff/issues/2475
-- values 1 , 2 , 3 limit 1;
-- values 3 , 2 , 1 order by 2;
