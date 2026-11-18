CREATE OR REPLACE TABLE my_db.my_schema.changes (
	id_col NUMBER(38,0) NOT NULL,
	flag_col BOOLEAN NOT NULL DEFAULT FALSE,
	ts_insert TIMESTAMP_NTZ(3) NOT NULL DEFAULT CAST(CURRENT_TIMESTAMP() AS TIMESTAMP_NTZ(3)),
	is_deleted BOOLEAN NOT NULL DEFAULT FALSE
)COMMENT='example';

SELECT *
FROM my_db.my_schema.changes
WHERE id_col = 1;

INSERT INTO my_db.my_schema.changes (id_col) VALUES (1);
