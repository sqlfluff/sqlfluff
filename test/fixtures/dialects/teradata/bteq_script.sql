-- An authentic BTEQ script: dot-commands are terminated by the end of the
-- line (no semicolon) and are freely interleaved with semicolon-terminated
-- SQL statements. See issue #1673.
.LOGON tdpid/username,password
.SET WIDTH 254
DATABASE mydb;
.IF ERRORCODE <> 0 THEN .QUIT 1
SELECT col1, col2 FROM my_table WHERE col1 > 10;
.EXPORT DATA FILE=out.dat
.LOGOFF
.QUIT
