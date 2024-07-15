REPLACE tbl_name VALUES (1, 2);

REPLACE tbl_name VALUES (DEFAULT, DEFAULT);

REPLACE tbl_name VALUES (1, 2), (11, 22);

REPLACE tbl_name VALUE (1, 2), (11, 22);

REPLACE tbl_name (col1, col2) VALUES (1, 2);

REPLACE tbl_name (col1, col2) VALUES ROW(1, 2), ROW(11, 22);

REPLACE LOW_PRIORITY tbl_name VALUES (1, 2);

REPLACE DELAYED tbl_name VALUES (1, 2);

REPLACE LOW_PRIORITY INTO tbl_name VALUES (1, 2);

REPLACE tbl_name PARTITION (partition_name) VALUES (1, 2);

REPLACE tbl_name SET col1 = 1, col2 = 2;

REPLACE LOW_PRIORITY tbl_name SET col1 = 1, col2 = 2;

REPLACE DELAYED tbl_name SET col1 = 1, col2 = 2;

REPLACE LOW_PRIORITY INTO tbl_name SET col1 = 1, col2 = 2;

REPLACE tbl_name PARTITION (partition_name) SET col1 = 1, col2 = 2;

REPLACE tbl_name SELECT * FROM table_name;
