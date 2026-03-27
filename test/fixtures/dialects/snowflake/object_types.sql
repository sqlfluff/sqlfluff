SELECT cast({ 'foo': 'bar' } AS OBJECT (foo VARCHAR)) AS baz;

SELECT CAST(NULL AS OBJECT) AS bare_obj;
