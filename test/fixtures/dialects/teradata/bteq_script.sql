-- An authentic BTEQ script: dot-commands are terminated by the end of the
-- line (no semicolon) and are freely interleaved with semicolon-terminated
-- SQL statements. See issue #1673.
.LOGON tdpid/username,password
.SET WIDTH 254
DATABASE mydb;
-- A command whose arguments could otherwise keep matching onto the next
-- line, directly followed by another dot-command.
.IF ERRORCODE <> 0 THEN .QUIT 1
.LABEL LOADSTEP
SELECT col1, col2 FROM my_table WHERE col1 > 10;
.IF ACTIVITYCOUNT = 0 THEN .QUIT 2
.EXPORT DATA FILE=out.dat
.RUN FILE=POSTING
.LOGOFF
.QUIT
