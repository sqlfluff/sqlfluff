CREATE OR REPLACE LUA SCRIPT aschema.hello AS
    return 'HELLO'
/
-- and a second one
CREATE OR REPLACE LUA SCRIPT aschema.world AS
    return 'WORLD'
/
