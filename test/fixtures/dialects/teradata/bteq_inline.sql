-- Edge cases: BTEQ commands mixed inline with SQL on same line.
-- These verify the lexer correctly splits BTEQ comment from SQL.
.IF errorcode > 0 then .quit 4; SELECT 1;
.RUN FILE=POSTING SELECT a FROM t;
.QUIT SELECT 1 + 2;
.LOGOFF SELECT * FROM t;

SELECT 1; .LOGOFF

-- BTEQ that looks like SQL — verifies regex keyword whitelist
-- prevents matching table.column syntax.
SELECT a.b, t.c FROM d.table_name;
.IF a.b > 10 then .GOTO end
