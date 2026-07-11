-- Edge cases: BTEQ with mixed-case keywords.
-- Verifies the (?i:...) regex flag works correctly.
.If errorcode > 0 then .QUIT 4;
.RUN FILE=POSTING
.quit
.logoff

SELECT 1;
