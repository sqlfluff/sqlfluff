set v1 = 10;

set v2 = 'example';

set (v1, v2) = (10, 'example');

set id_threshold = (select count(*) from table1) / 2;

set (min, max) = (40, 70);

set (min, max) = (50, 2 * $min);

SET THIS_ROLE=CURRENT_ROLE();
