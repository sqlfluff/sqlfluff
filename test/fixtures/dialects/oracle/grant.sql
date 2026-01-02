GRANT CREATE SESSION
   TO hr;

GRANT CREATE SESSION
  TO hr, newuser IDENTIFIED BY password1, password2;

GRANT
     CREATE ANY MATERIALIZED VIEW
   , ALTER ANY MATERIALIZED VIEW
   , DROP ANY MATERIALIZED VIEW
   , QUERY REWRITE
   , GLOBAL QUERY REWRITE
   TO dw_manager
   WITH ADMIN OPTION;

GRANT dw_manager
   TO sh
   WITH ADMIN OPTION;

GRANT dw_manager
   TO sh
   WITH DELEGATE OPTION;

GRANT SELECT ON sh.sales TO warehouse_user;

GRANT warehouse_user TO dw_manager;

GRANT INHERIT PRIVILEGES ON USER sh TO hr;

GRANT READ ON DIRECTORY bfile_dir TO hr
   WITH GRANT OPTION;

GRANT ALL ON bonuses TO hr
   WITH GRANT OPTION;

GRANT SELECT, UPDATE
   ON emp_view TO PUBLIC;

GRANT SELECT
   ON oe.customers_seq TO hr;

GRANT REFERENCES (employee_id),
      UPDATE (employee_id, salary, commission_pct)
   ON hr.employees
   TO oe;
