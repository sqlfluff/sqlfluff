-- Unfiltered list of all functions;
SHOW FUNCTIONS;

-- List a system function `trim` by searching both user defined and system
-- defined functions.
SHOW FUNCTIONS trim;

SHOW ALL FUNCTIONS trim;

-- List a system function `concat` by searching system defined functions.
SHOW SYSTEM FUNCTIONS concat;

-- List a user function `concat_user` by searching user defined functions.
SHOW USER FUNCTIONS concat_user;

-- List a qualified function `max` from database `salesdb`.
SHOW SYSTEM FUNCTIONS salesdb.max;

-- List all functions starting with `t`
SHOW FUNCTIONS LIKE 't*';

-- List all functions starting with `t` without LIKE keyword
SHOW FUNCTIONS 't*';

-- List all user functions starting with `t`
SHOW USER FUNCTIONS LIKE 't*';

-- List all user functions starting with `t` without LIKE keyword
SHOW USER FUNCTIONS 't*';

-- List all functions starting with `yea` or `windo`
SHOW FUNCTIONS LIKE 'yea*|windo*';

-- Use normal regex pattern to list function names that has 4 characters
-- with `t` as the starting character.
SHOW FUNCTIONS LIKE 't[a-z][a-z][a-z]';

-- List all functions from default schema
SHOW FUNCTIONS FROM default;

-- List all user functions from default schema
SHOW USER FUNCTIONS FROM default;

-- List all functions from default schema starting with `t`
SHOW FUNCTIONS FROM default LIKE 't*';

-- List all functions from default schema starting with `t` without LIKE keyword
SHOW FUNCTIONS FROM default 't*';

-- List all user functions from default schema starting with `t`
SHOW USER FUNCTIONS FROM default LIKE 't*';

-- List all user functions from default schema starting with `t` without LIKE keyword
SHOW USER FUNCTIONS FROM default 't*';
