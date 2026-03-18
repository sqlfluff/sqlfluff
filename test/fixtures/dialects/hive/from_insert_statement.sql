-- Multi-insert using a shared source clause
FROM tab1
INSERT INTO TABLE tab2 SELECT * WHERE flag = 2
INSERT INTO TABLE tab3 SELECT * WHERE flag = 3;

-- Repro from issue with full SELECT statements in each insert clause
FROM tab1
INSERT INTO TABLE tab2 SELECT * FROM tab1 WHERE flag = 2
INSERT INTO TABLE tab3 SELECT * FROM tab1 WHERE flag = 3;

-- INSERT targets may include target column lists
FROM tab1
INSERT INTO TABLE tab2 (col1, col2) SELECT * FROM tab1 WHERE flag = 2
INSERT INTO TABLE tab3 (col1, col2) SELECT * FROM tab1 WHERE flag = 3;

-- Shared sources may include joins
FROM src1
JOIN src2 ON src1.id = src2.id
INSERT INTO TABLE tab2 SELECT src1.id WHERE src2.flag = 2
INSERT INTO TABLE tab3 SELECT src2.id WHERE src1.flag = 3;

-- Shared sources may include subqueries
FROM (
	SELECT id, flag
	FROM tab1
) src
INSERT INTO TABLE tab2 SELECT id WHERE flag = 2
INSERT INTO TABLE tab3 SELECT id WHERE flag = 3;
