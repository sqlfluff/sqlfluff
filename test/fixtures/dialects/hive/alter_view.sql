ALTER VIEW db.foo AS SELECT col1 FROM db.bar;

ALTER VIEW foo SET TBLPROPERTIES ('bar' = '1', 'baz' = '2');
