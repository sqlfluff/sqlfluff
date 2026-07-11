-- Edge cases: BTEQ commands without semicolons at end of file.
-- Verifies the lexer consumes BTEQ without requiring statement terminators.
.IF errorcode > 0 then .quit 4
.RUN FILE=POSTING
.QUIT
.LOGOFF

SELECT 1
