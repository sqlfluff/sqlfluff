select lag(test) over (ORDER BY test);

select lag(test) over (PARTITION BY test ORDER BY test);