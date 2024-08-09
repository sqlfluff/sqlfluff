LOAD DATA INFILE '/var/lib/mysql-files/libaccess.csv' INTO TABLE libaccess FIELDS TERMINATED BY '\t' OPTIONALLY ENCLOSED BY '"' IGNORE 1 LINES;
LOAD DATA INFILE 'data.txt' INTO TABLE db2.my_table;
LOAD DATA INFILE 'data.txt' INTO TABLE db2.my_table PARTITION (partition_name);
LOAD DATA INFILE '/tmp/test.txt' INTO TABLE test
  FIELDS TERMINATED BY ','  LINES STARTING BY 'xxx';
LOAD DATA INFILE '/tmp/test.txt' INTO TABLE test IGNORE 1 LINES;
LOAD DATA INFILE 'data.txt' INTO TABLE table2
  FIELDS TERMINATED BY ',';
LOAD DATA INFILE 'data.txt' INTO TABLE table2
  FIELDS TERMINATED BY '\t';
LOAD DATA INFILE 'data.txt' INTO TABLE tbl_name
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\r\n'
  IGNORE 1 LINES;
LOAD DATA INFILE '/tmp/jokes.txt' INTO TABLE jokes
  FIELDS TERMINATED BY ''
  LINES TERMINATED BY '\n%%\n' (joke);
LOAD DATA INFILE 'persondata.txt' INTO TABLE persondata;
LOAD DATA INFILE 'file.txt'
  INTO TABLE t1
  (column1, @var1)
  SET column2 = @var1/100;
LOAD DATA INFILE 'file.txt'
  INTO TABLE t1
  (column1, column2)
  SET column3 = CURRENT_TIMESTAMP;
LOAD DATA INFILE 'file.txt'
  INTO TABLE t1
  (column1, @dummy, column2, @dummy, column3);
LOAD DATA INFILE '/local/access_log' INTO TABLE tbl_name
  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\'
