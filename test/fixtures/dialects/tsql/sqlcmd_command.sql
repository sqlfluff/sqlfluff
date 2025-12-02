/*
https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver16#sqlcmd-commands
*/

-- reference / execute other SQL files
:r script.sql
:r script#01_a-b.sql
:r ...\folder\script.SQL
:r .\folder_1\folder_2\folder_3\folder_4\script.sql

-- define *sqlcmd* scripting variable
:setvar variable_name variable_value
:setvar variable_name "variable_value"
