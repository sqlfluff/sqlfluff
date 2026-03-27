SELECT cast({ 'foo': 'bar' } AS OBJECT (foo VARCHAR)) AS baz;

SELECT CAST(NULL AS OBJECT(foo VARCHAR, bar NUMBER(10,2))) AS multi_field_obj;

SELECT CAST(NULL AS OBJECT(foo VARCHAR NOT NULL)) AS not_null_obj;

SELECT CAST(NULL AS OBJECT(foo OBJECT(bar VARCHAR))) AS nested_obj;

SELECT {'foo': 'bar'}::OBJECT(foo VARCHAR) AS shorthand_obj;

SELECT CAST(NULL AS OBJECT) AS bare_obj;
