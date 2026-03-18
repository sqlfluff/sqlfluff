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
