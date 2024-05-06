CREATE TEMPORARY TABLE tbl_name (
    id INT PRIMARY KEY AUTO_INCREMENT,
    col VARCHAR(255) DEFAULT '' NOT NULL,
    INDEX(col)
) AS SELECT id, col FROM table_name;

-- CREATE TEMPORARY TABLE tbl_name (
--     id INT PRIMARY KEY AUTO_INCREMENT,
--     col VARCHAR(255) DEFAULT '' NOT NULL,
--     INDEX(col)
-- ) SELECT id, col FROM table_name;

-- CREATE TEMPORARY TABLE tbl_name (INDEX(col)) AS
--     SELECT id, col FROM table_name;
--
-- CREATE TEMPORARY TABLE tbl_name (INDEX(col))
--     SELECT id, col FROM table_name;
