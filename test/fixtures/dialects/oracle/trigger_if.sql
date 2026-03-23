CREATE OR REPLACE TRIGGER test.trigger_if
AFTER INSERT OR UPDATE OR DELETE ON test.table_ref
REFERENCING NEW AS New OLD AS Old
FOR EACH ROW
DECLARE
  AUDITINFO VARCHAR2(2000);
  EVENT VARCHAR2(10);
BEGIN
  IF INSERTING THEN
    AUDITINFO := 'Insert row into ';
    EVENT := 'INSERT';
  ELSIF DELETING THEN
    AUDITINFO := 'Delete row from ';
    EVENT := 'DELETE';
  ELSIF UPDATING THEN
    AUDITINFO := 'Update row from ';
    EVENT := 'UPDATE';
  ELSE
    AUDITINFO := 'Unknow operation ';
    EVENT := 'UNKNOW';
  END IF;
END;
/

-- OR-combined trigger predicates in IF / ELSIF
CREATE OR REPLACE TRIGGER test.trigger_if_or_combined
AFTER INSERT OR UPDATE OR DELETE ON test.table_ref
FOR EACH ROW
DECLARE
  EVENT VARCHAR2(10);
BEGIN
  IF UPDATING('Institution_id') OR INSERTING OR DELETING THEN
    EVENT := 'MULTI';
  ELSIF UPDATING('col1') OR UPDATING('col2') THEN
    EVENT := 'COL_UPDATE';
  END IF;
END;
/

-- UPDATING with a specific column name (single predicate)
CREATE OR REPLACE TRIGGER test.trigger_if_updating_col
AFTER UPDATE ON test.table_ref
FOR EACH ROW
BEGIN
  IF UPDATING('salary') THEN
    NULL;
  END IF;
END;
/

-- NOT before single trigger predicates
CREATE OR REPLACE TRIGGER test.trigger_if_not_predicate
AFTER INSERT OR UPDATE OR DELETE ON test.table_ref
FOR EACH ROW
BEGIN
  IF NOT INSERTING THEN
    NULL;
  ELSIF NOT DELETING THEN
    NULL;
  ELSIF NOT UPDATING THEN
    NULL;
  END IF;
END;
/

-- AND-combined trigger predicates
CREATE OR REPLACE TRIGGER test.trigger_if_and_combined
AFTER INSERT OR UPDATE OR DELETE ON test.table_ref
FOR EACH ROW
BEGIN
  IF UPDATING('col1') AND NOT UPDATING('col2') THEN
    NULL;
  ELSIF INSERTING AND NOT DELETING THEN
    NULL;
  END IF;
END;
/

-- Mixed OR and AND with NOT
CREATE OR REPLACE TRIGGER test.trigger_if_or_and_not
AFTER INSERT OR UPDATE OR DELETE ON test.table_ref
FOR EACH ROW
BEGIN
  IF NOT UPDATING('salary') OR INSERTING AND NOT DELETING THEN
    NULL;
  END IF;
END;
/

-- CASE WHEN with multiple predicates (OR/AND/NOT)
CREATE OR REPLACE TRIGGER test.trigger_case_predicates
AFTER INSERT OR UPDATE OR DELETE ON test.table_ref
FOR EACH ROW
BEGIN
  CASE
    WHEN UPDATING('col') OR INSERTING THEN
      NULL;
    WHEN NOT DELETING AND UPDATING('other_col') THEN
      NULL;
    ELSE
      NULL;
  END CASE;
END;
/
