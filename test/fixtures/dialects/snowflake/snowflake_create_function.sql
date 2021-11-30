CREATE FUNCTION pi_udf()
  RETURNS FLOAT
  AS '3.141592654::FLOAT';
CREATE FUNCTION simple_table_function ()
  RETURNS TABLE (x INTEGER, y INTEGER)
  AS
  $$
    SELECT 1, 2
    UNION ALL
    SELECT 3, 4
  $$;
CREATE OR REPLACE FUNCTION get_countries_for_user ( id number )
  RETURNS TABLE (country_code char, country_name varchar)
  RETURNS NULL ON NULL INPUT
  AS 'select distinct c.country_code, c.country_name
      from user_addresses a, countries c
      where a.user_id = id
      and c.country_code = a.country_code';
CREATE SECURE FUNCTION js_factorial(d double)
  RETURNS double
  IMMUTABLE
  LANGUAGE JAVASCRIPT
  STRICT
  AS '
  if (D <= 0) {
    return 1;
  } else {
    var result = 1;
    for (var i = 2; i <= D; i++) {
      result = result * i;
    }
    return result;
  }
  ';
