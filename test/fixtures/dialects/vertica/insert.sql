INSERT INTO t1 VALUES (101, 102, 103, 104);
INSERT INTO customer VALUES (10, 'male', 'DPR', 'MA', 35);
INSERT INTO start_time VALUES (12, 'film','05:10:00:01');
INSERT INTO retail.t1 (C0, C1) VALUES (1, 1001);
INSERT INTO films SELECT * FROM tmp_films WHERE date_prod < '2004-05-07';
INSERT INTO t1 (col1, col2) (SELECT 'abc', mycolumn FROM mytable);
