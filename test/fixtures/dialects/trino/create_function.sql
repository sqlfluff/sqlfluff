CREATE FUNCTION f()
RETURNS bigint
RETURN 42;

CREATE FUNCTION double_it(x integer)
RETURNS integer
RETURN x * 2;

CREATE FUNCTION str_concat(a varchar, b varchar)
RETURNS varchar
RETURN concat(a, b);

CREATE FUNCTION calculate_tax(price double, tax_rate double)
RETURNS double
RETURN price * tax_rate;

CREATE FUNCTION custom_as()
RETURNS integer
AS 'SELECT 1';

CREATE FUNCTION custom_as_lang()
RETURNS integer
AS 'SELECT 1'
LANGUAGE sql;
