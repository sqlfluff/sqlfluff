-- BTEQ dot-commands are confined to a single line and are accepted without
-- producing an unparsable section. See issue #1673.
.LOGON tdpid/username,password;
.SET WIDTH 254;
.SET SEPARATOR '|';
.EXPORT DATA FILE=out.dat;
.EXPORT RESET;
.IMPORT DATA FILE=in.dat;
.RUN FILE=POSTING;
.LABEL start;
.GOTO start;
.REMARK 'load complete';
.OS ls -l;
.SHOW CONTROLS;
.IF ACTIVITYCOUNT = 0 THEN .QUIT 8;
.LOGOFF;
.QUIT;
