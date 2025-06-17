DECLARE
  TYPE EmpRec IS RECORD (
    last_name  employees.last_name%TYPE,
    salary     employees.salary%TYPE
  );
  emp_info    EmpRec;
  old_salary  employees.salary%TYPE;
BEGIN
  SELECT salary INTO old_salary
   FROM employees
   WHERE employee_id = 100;

  UPDATE employees
    SET salary = salary * 1.1
    WHERE employee_id = 100
    RETURNING last_name, salary INTO emp_info;

  DBMS_OUTPUT.PUT_LINE (
    'Salary of ' || emp_info.last_name || ' raised from ' ||
    old_salary || ' to ' || emp_info.salary
  );
END;
/

DECLARE
  emp_id          employees_temp.employee_id%TYPE := 299;
  emp_first_name  employees_temp.first_name%TYPE  := 'Bob';
  emp_last_name   employees_temp.last_name%TYPE   := 'Henry';
BEGIN
  INSERT INTO employees_temp (employee_id, first_name, last_name)
  VALUES (emp_id, emp_first_name, emp_last_name);

  UPDATE employees_temp
  SET first_name = 'Robert'
  WHERE employee_id = emp_id;

  DELETE FROM employees_temp
  WHERE employee_id = emp_id
  RETURNING first_name, last_name
  INTO emp_first_name, emp_last_name;

  COMMIT;
  DBMS_OUTPUT.PUT_LINE (emp_first_name || ' ' || emp_last_name);
END;
/

DECLARE
  TYPE NumList IS TABLE OF employees.employee_id%TYPE;
  enums  NumList;
  TYPE NameList IS TABLE OF employees.last_name%TYPE;
  names  NameList;
BEGIN
  DELETE FROM emp_temp
  WHERE department_id = 30
  RETURNING employee_id, last_name
  BULK COLLECT INTO enums, names;

  DBMS_OUTPUT.PUT_LINE ('Deleted ' || SQL%ROWCOUNT || ' rows:');
  FOR i IN enums.FIRST .. enums.LAST
  LOOP
    DBMS_OUTPUT.PUT_LINE ('Employee #' || enums(i) || ': ' || names(i));
  END LOOP;
END;
/

DECLARE
  TYPE SalList IS TABLE OF employees.salary%TYPE;
  old_sals SalList;
  new_sals SalList;
  TYPE NameList IS TABLE OF employees.last_name%TYPE;
  names NameList;
BEGIN
  UPDATE emp_temp SET salary = salary * 1.15
  WHERE salary < 2500
  RETURNING OLD salary, NEW salary, last_name
  BULK COLLECT INTO old_sals, new_sals, names;

  DBMS_OUTPUT.PUT_LINE('Updated ' || SQL%ROWCOUNT || ' rows: ');
  FOR i IN old_sals.FIRST .. old_sals.LAST
  LOOP
    DBMS_OUTPUT.PUT_LINE(names(i) || ': Old Salary $' || old_sals(i) ||
            ', New Salary $' || new_sals(i));
  END LOOP;
END;
/

DECLARE
  TYPE NumList IS TABLE OF NUMBER;
  depts  NumList := NumList(10,20,30);

  TYPE enum_t IS TABLE OF employees.employee_id%TYPE;
  e_ids  enum_t;

  TYPE dept_t IS TABLE OF employees.department_id%TYPE;
  d_ids  dept_t;

BEGIN
  FORALL j IN depts.FIRST..depts.LAST
    DELETE FROM emp_temp
    WHERE department_id = depts(j)
    RETURNING employee_id, department_id
    BULK COLLECT INTO e_ids, d_ids;

  DBMS_OUTPUT.PUT_LINE ('Deleted ' || SQL%ROWCOUNT || ' rows:');

  FOR i IN e_ids.FIRST .. e_ids.LAST
  LOOP
    DBMS_OUTPUT.PUT_LINE (
      'Employee #' || e_ids(i) || ' from dept #' || d_ids(i)
    );
  END LOOP;
END;
/

DECLARE
  TYPE t_desc_tab IS TABLE OF t1.description%TYPE;
  TYPE t_id_tab   IS TABLE OF t1.id%TYPE;
  TYPE t_desc_out_tab IS TABLE OF t1.description%TYPE;

  l_desc_tab t_desc_tab := t_desc_tab('FIVE', 'SIX', 'SEVEN');
  l_id_tab   t_id_tab;
  l_desc_out_tab t_desc_out_tab;
BEGIN
  FORALL i IN l_desc_tab.FIRST .. l_desc_tab.LAST
    INSERT INTO t1 VALUES (t1_seq.NEXTVAL, l_desc_tab(i))
    RETURNING id, description BULK COLLECT INTO l_id_tab, l_desc_out_tab;

  FOR i IN l_id_tab.FIRST .. l_id_tab.LAST LOOP
    DBMS_OUTPUT.put_line('INSERT ID=' || l_id_tab(i) ||
                         ' DESC=' || l_desc_out_tab(i));
  END LOOP;

  COMMIT;
END;
/

DECLARE
TYPE t_sal_tab IS TABLE OF emp.sal%TYPE;
TYPE t_empno_tab IS TABLE OF emp.empno%TYPE;
l_empno t_empno_tab;
l_salo t_sal_tab;
l_saln t_sal_tab;
BEGIN
    MERGE INTO emp t
    USING  emp_sal_increase  q
    ON    (t.deptno = q.deptno)
    WHEN MATCHED THEN UPDATE SET t.sal=t.sal*(1+q.increase_pct/100)
    RETURNING empno, OLD sal, NEW sal BULK COLLECT INTO l_empno, l_salo, l_saln;

    FOR i IN l_salo.first .. l_salo.last LOOP
      DBMS_OUTPUT.put_line('EMPNO=' || l_empno(i)|| ', SAL changed from '||l_salo(i) ||' to ' ||l_saln(i));
    END LOOP;
END;
/
