-- simple assignment
SET VAR var1 = 5;

-- A complex expression assignment
SET VARIABLE var1 = (SELECT max(c1) FROM VALUES(1), (2) AS t(c1));

-- resetting the variable to DEFAULT (set in declare)
SET VAR var1 = DEFAULT;

-- A multi variable assignment
SET VAR (var1, var2) = (SELECT max(c1), CAST(min(c1) AS STRING) FROM VALUES(1), (2) AS t(c1));
