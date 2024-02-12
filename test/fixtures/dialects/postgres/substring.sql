select * FROM substring('Thomas' from 2 for 3);
select * FROM substring('Thomas' from 3);
select * FROM substring('Thomas' for 2);
select * FROM substring('Thomas' similar '%#"o_a#"_' escape '#');
select * FROM substring('Thomas' from '...$');
