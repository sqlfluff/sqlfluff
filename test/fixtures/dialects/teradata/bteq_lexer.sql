-- Test BTEQ meta-commands are consumed as comments by the lexer.
-- Mixed BTEQ + valid SQL in the same file.
.if errorcode > 0 then .quit 4;
.RUN FILE=POSTING
.QUIT
.LOGOFF

SELECT 1;

SELECT a, b FROM t WHERE a.b > 0;

.IF table.b > 10 then .GOTO cleanup
.IMPORT REPORT FILE=monthly.csv
.EXPORT REPORT FILE=output.txt

SELECT 1 + 2;

.LOGON tdpid/user, password
.LABEL cleanup
.DATABASE mydb;

SELECT * FROM mydb.schema.t;
