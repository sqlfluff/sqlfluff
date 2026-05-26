.if errorcode > 0 then .quit 4;
.RUN FILE=POSTING;
.RUN FILE=POSTING.SQL;
.RUN FILE=../posting-file.sql;
.RUN FILE="reports/out summary.txt";
.RUN FILE=C:\reports\out-summary.txt;
.EXPORT REPORT FILE=reports/out,summary.txt
