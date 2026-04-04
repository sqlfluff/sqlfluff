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

-- USER: name of the current schema / session user (VARCHAR2).
SELECT USER FROM dual;

INSERT INTO audit_log (log_id, created_by)
VALUES (audit_seq.NEXTVAL, USER);

-- UID: numeric user identifier for the current session.
SELECT UID FROM dual;

INSERT INTO audit_log (log_id, user_id_num)
VALUES (audit_seq.NEXTVAL, UID);

-- SESSION_USER: ANSI / Oracle function returning the session user name.
-- Equivalent to USER in most contexts; differs under proxy authentication.
SELECT SESSION_USER FROM dual;

INSERT INTO audit_log (log_id, session_user_col)
VALUES (audit_seq.NEXTVAL, SESSION_USER);

-- ORA_ROWSCN: system change number pseudo-column for each row; read-only,
-- only valid in queries (SELECT / WHERE), not in INSERT VALUES.
SELECT ORA_ROWSCN, employee_id FROM employees;

SELECT employee_id FROM employees
WHERE ORA_ROWSCN > 12345678;
