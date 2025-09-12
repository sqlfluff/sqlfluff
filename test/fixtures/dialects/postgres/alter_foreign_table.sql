ALTER FOREIGN TABLE distributors ALTER COLUMN street SET NOT NULL;

ALTER FOREIGN TABLE t_user ADD COLUMN my_column text;

ALTER TABLE bar_fdw.foo ADD test varchar NULL;

ALTER FOREIGN TABLE myschema.distributors OPTIONS (ADD opt1 'value', SET opt2 'value2', DROP opt3);

ALTER FOREIGN TABLE test OPTIONS (SET table $$(select my_column from my_table)$$);

ALTER FOREIGN TABLE test ADD COLUMN new_column int8, OPTIONS (SET table $$(select my_column from my_table)$$);

ALTER FOREIGN TABLE test RENAME TO test_renamed;
