DECLARE
  PROCEDURE p (
    sales  NUMBER,
    quota  NUMBER,
    emp_id NUMBER
  )
  IS
    bonus    NUMBER := 0;
    updated  VARCHAR2(3) := 'No';
  BEGIN
    IF sales > (quota + 200) THEN
      bonus := (sales - quota)/4;

      UPDATE employees
      SET salary = salary + bonus
      WHERE employee_id = emp_id;

      updated := 'Yes';
    END IF;

    DBMS_OUTPUT.PUT_LINE (
      'Table updated?  ' || updated || ', ' ||
      'bonus = ' || bonus || '.'
    );
  END p;
BEGIN
  p(10100, 10000, 120);
  p(10500, 10000, 121);
END;
/

DECLARE
  PROCEDURE p (
    sales  NUMBER,
    quota  NUMBER,
    emp_id NUMBER
  )
  IS
    bonus  NUMBER := 0;
  BEGIN
    IF sales > (quota + 200) THEN
      bonus := (sales - quota)/4;
    ELSE
      bonus := 50;
    END IF;

    DBMS_OUTPUT.PUT_LINE('bonus = ' || bonus);

    UPDATE employees
    SET salary = salary + bonus
    WHERE employee_id = emp_id;
  END p;
BEGIN
  p(10100, 10000, 120);
  p(10500, 10000, 121);
END;
/

DECLARE
  PROCEDURE p (
    sales  NUMBER,
    quota  NUMBER,
    emp_id NUMBER
  )
  IS
    bonus  NUMBER := 0;
  BEGIN
    IF sales > (quota + 200) THEN
      bonus := (sales - quota)/4;
    ELSE
      IF sales > quota THEN
        bonus := 50;
      ELSE
        bonus := 0;
      END IF;
    END IF;

    DBMS_OUTPUT.PUT_LINE('bonus = ' || bonus);

    UPDATE employees
    SET salary = salary + bonus
    WHERE employee_id = emp_id;
  END p;
BEGIN
  p(10100, 10000, 120);
  p(10500, 10000, 121);
  p(9500, 10000, 122);
END;
/

DECLARE
  PROCEDURE p (sales NUMBER)
  IS
    bonus  NUMBER := 0;
  BEGIN
    IF sales > 50000 THEN
      bonus := 1500;
    ELSIF sales > 35000 THEN
      bonus := 500;
    ELSE
      bonus := 100;
    END IF;

    DBMS_OUTPUT.PUT_LINE (
      'Sales = ' || sales || ', bonus = ' || bonus || '.'
    );
  END p;
BEGIN
  p(55000);
  p(40000);
  p(30000);
END;
/

-- IS [NOT] OF type predicate (Oracle OO PL/SQL)
DECLARE
  obj_ref SYS.ANYDATA;
BEGIN
  IF obj_ref IS OF (emp_t) THEN
    NULL;
  ELSIF obj_ref IS NOT OF (mgr_t, emp_t) THEN
    NULL;
  ELSIF obj_ref IS OF TYPE (worker_t) THEN
    NULL;
  ELSIF obj_ref IS NOT OF TYPE (mgr_t) THEN
    NULL;
  ELSIF obj_ref IS OF (ONLY emp_t) THEN
    NULL;
  ELSIF obj_ref IS NOT OF (ONLY mgr_t, ONLY emp_t) THEN
    NULL;
  END IF;
END;
/

-- Anonymous block with IF/ELSIF/ELSE
DECLARE
  AUDITINFO VARCHAR2(2000);
  EVENT VARCHAR2(10);
BEGIN
  IF 1 = 1 THEN
    AUDITINFO := 'Insert row into ';
    EVENT := 'INSERT';
  ELSIF 1 = 2 THEN
    AUDITINFO := 'Delete row from ';
    EVENT := 'DELETE';
  ELSIF 1 = 3 THEN
    AUDITINFO := 'Update row from ';
    EVENT := 'UPDATE';
  ELSE
    AUDITINFO := 'Unknow operation ';
    EVENT := 'UNKNOW';
  END IF;
END;
/
