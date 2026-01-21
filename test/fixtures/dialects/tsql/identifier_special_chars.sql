-- Test special characters in T-SQL identifiers
-- According to Microsoft spec:
-- https://learn.microsoft.com/en-us/sql/relational-databases/databases/database-identifiers
--
-- First character: letter, underscore (@ and # have special meanings)
-- Subsequent characters: letters, numbers, underscore
-- Special characters like @, $, # REQUIRE brackets when used in regular identifiers

-- Variables with @ prefix can have $, #, _ in subsequent positions
DECLARE @variable INT = 1;
DECLARE @$variable INT = 2;
DECLARE @#variable INT = 3;
DECLARE @_variable INT = 4;
DECLARE @var$test INT = 5;
DECLARE @var#test INT = 6;
DECLARE @var_test INT = 7;

-- Temp tables with # prefix can have @, $, _ in subsequent positions
CREATE TABLE #temp (id INT);
CREATE TABLE #$temp (id INT);
CREATE TABLE #@temp (id INT);
CREATE TABLE #_temp (id INT);
CREATE TABLE ##global (id INT);

-- Regular identifiers with special characters MUST use brackets
CREATE TABLE [Table$name] ([Column@name] INT, [Column#test] INT, Column_test INT);

-- Using these identifiers in queries
SELECT @variable, @$variable, @#variable;
SELECT * FROM [Table$name];
SELECT [Column@name], [Column#test] FROM [Table$name];
