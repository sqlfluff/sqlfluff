-- simple assignment
SET VAR var1 = 5;

-- A complex expression assignment
SET VARIABLE var1 = (SELECT max(c1) FROM VALUES(1), (2) AS t(c1));

-- resetting the variable to DEFAULT (set in declare)
SET VAR var1 = DEFAULT;

-- A multi variable assignment
SET VAR (var1, var2, var3) = (VALUES(100,'x123',DEFAULT));

-- escpaed function name
SET VARIABLE `foo` = select 'bar';

-- function call
set var tz = current_timezone();

-- set multiple vars in one statement
set var x1 = 12, x2 = 'helloworld';
