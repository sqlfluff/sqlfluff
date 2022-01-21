VALUES ROW ('a', 1), ROW ('b', 2);

VALUES ROW ('a', 1), ROW (upper('b'), 2+1);

VALUES ROW (CURRENT_DATE, '2020-06-04' + interval -5 day);
