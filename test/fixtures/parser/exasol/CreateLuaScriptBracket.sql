CREATE OR REPLACE LUA SCRIPT BRACKET.SCRIPT_EXAMPLE RETURNS ROWCOUNT AS
    local _stmt = [[SOME ASSIGNMENT WITH OPEN BRACKET ( ]]
    x = 1
    local _stmt = _stmt .. [[ ) ]]
return 1
/
