DECLARE
constraint_name VARCHAR2(255);
result_var NUMBER;
BEGIN
  SELECT constraint_name
  INTO constraint_name
  FROM user_constraints
  WHERE table_name = 'MY_TABLE' AND constraint_type = 'C' AND search_condition_vc LIKE 'MY_CONDITION%';

  EXECUTE IMMEDIATE 'ALTER TABLE ' || table_name || ' DROP CONSTRAINT ' || constraint_name;
  EXECUTE IMMEDIATE 'ALTER TABLE MY_TABLE2 DROP CONSTRAINT ' || constraint_name;
  EXECUTE IMMEDIATE 'SELECT COUNT(*) FROM ' || table_name INTO result_var;
  EXECUTE IMMEDIATE 'INSERT INTO MY_TABLE3 VALUES (:1, :2)' USING constraint_name, result_var;
  EXECUTE IMMEDIATE 'DROP TABLE MY_TABLE';
END;
/
