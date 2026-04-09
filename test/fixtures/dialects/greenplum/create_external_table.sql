CREATE EXTERNAL TABLE ext_expenses
( name text,
  category text,
  desc1 text )
LOCATION ('gpfdist://etlhost-1:8081/*')
FORMAT 'TEXT' (DELIMITER '|');

CREATE EXTERNAL TABLE ext_expenses
( name text,
  category text,
  amount float4 )
LOCATION ('gpfdist://etlhost-1:8081/*.txt', 'gpfdist://etlhost-2:8082/*.txt')
FORMAT 'TEXT' (DELIMITER '|');

CREATE EXTERNAL TABLE ext_csv
( id int,
  name text )
LOCATION ('gpfdist://etlhost-1:8081/data.csv')
FORMAT 'CSV' (DELIMITER ',');

CREATE READABLE EXTERNAL TABLE ext_read
( id int,
  val text )
LOCATION ('gpfdist://etlhost-1:8081/data.txt')
FORMAT 'TEXT' (DELIMITER '|');

CREATE WRITABLE EXTERNAL TABLE ext_write
( id int,
  val text )
LOCATION ('gpfdist://etlhost-1:8081/output/')
FORMAT 'TEXT' (DELIMITER '|')
DISTRIBUTED BY (id);

CREATE EXTERNAL WEB TABLE log_output
( linenum int,
  message text )
EXECUTE '/var/load_scripts/get_log_data.sh' ON HOST
FORMAT 'TEXT' (DELIMITER '|');

CREATE EXTERNAL TABLE ext_encoded
( id int,
  name text )
LOCATION ('gpfdist://etlhost-1:8081/data.txt')
FORMAT 'TEXT' (DELIMITER '|')
ENCODING 'UTF8';

CREATE EXTERNAL TABLE ext_with_errors
( id int,
  name text )
LOCATION ('gpfdist://etlhost-1:8081/data.txt')
FORMAT 'TEXT' (DELIMITER '|')
LOG ERRORS
SEGMENT REJECT LIMIT 5 ROWS;

CREATE WRITABLE EXTERNAL TABLE ext_write_random
( id int,
  val text )
LOCATION ('gpfdist://etlhost-1:8081/output/')
FORMAT 'TEXT' (DELIMITER '|')
DISTRIBUTED RANDOMLY;

CREATE EXTERNAL WEB TABLE cmd_output
( id int,
  val text )
EXECUTE '/usr/local/bin/mycommand' ON COORDINATOR
FORMAT 'TEXT' (DELIMITER '|');

CREATE EXTERNAL TABLE ext_custom_fmt
( id int,
  data bytea )
LOCATION ('gpfdist://etlhost-1:8081/data.bin')
FORMAT 'CUSTOM' (FORMATTER='fixedwidth_in');

CREATE EXTERNAL TABLE ext_with_options
( id int,
  name text )
LOCATION ('pxf://tmp/data?PROFILE=HdfsTextSimple')
FORMAT 'TEXT' (DELIMITER ',')
OPTIONS (mpp_execute 'all segments');

CREATE EXTERNAL TABLE ext_like
LIKE other_table
LOCATION ('gpfdist://etlhost-1:8081/data.txt')
FORMAT 'CSV';

CREATE EXTERNAL TABLE ext_log_errors
( id int,
  name text )
LOCATION ('gpfdist://etlhost-1:8081/data.txt')
FORMAT 'TEXT' (DELIMITER '|')
LOG ERRORS
SEGMENT REJECT LIMIT 10 PERCENT;
