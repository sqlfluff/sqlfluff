VALUES ROW ('a', 1), ROW ('b', 2);

VALUES ROW ('a', 1), ROW (upper('b'), 2+1);

VALUES ROW (CURRENT_DATE, 1), ROW (INTERVAL 10 MINUTE, 2+1);
