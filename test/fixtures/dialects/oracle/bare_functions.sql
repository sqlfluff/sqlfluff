SELECT
  a.foo,
  b.bar,
  current_date,
  current_timestamp,
  dbtimezone,
  localtimestamp,
  sessiontimestamp,
  sysdate,
  systimestamp
FROM first_table a
INNER JOIN second_table b
ON a.baz = b.baz
;

-- Sequence pseudo-columns: CURRVAL and NEXTVAL via dotted reference
SELECT some_seq.CURRVAL FROM dual;
SELECT some_seq.NEXTVAL FROM dual;
INSERT INTO t (id) VALUES (some_seq.CURRVAL);

-- 3-part schema-qualified sequence pseudo-columns
SELECT myschema.some_seq.CURRVAL FROM dual;
SELECT myschema.some_seq.NEXTVAL FROM dual;
INSERT INTO t (id) VALUES (myschema.some_seq.NEXTVAL);
