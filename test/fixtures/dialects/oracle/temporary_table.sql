--https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/CREATE-TABLE.html#GUID-F9CE0CC3-13AE-4744-A43C-EAC7A71AAAB6
--https://oracle-base.com/articles/misc/temporary-tables
--https://oracle-base.com/articles/18c/private-temporary-tables-18c

CREATE GLOBAL TEMPORARY TABLE today_sales
   ON COMMIT PRESERVE ROWS
   AS SELECT * FROM orders WHERE order_date = SYSDATE;

CREATE GLOBAL TEMPORARY TABLE HT_AFFAIRES (ID CHAR (36 CHAR)) ON COMMIT DELETE ROWS;

CREATE GLOBAL TEMPORARY TABLE my_temp_table (
  id           NUMBER,
  description  VARCHAR2(20)
)
ON COMMIT DELETE ROWS;

CREATE GLOBAL TEMPORARY TABLE my_temp_table (
  id           NUMBER,
  description  VARCHAR2(20)
)
ON COMMIT PRESERVE ROWS;

CREATE PRIVATE TEMPORARY TABLE ora$ptt_my_temp_table (
  id           NUMBER,
  description  VARCHAR2(20)
)
ON COMMIT DROP DEFINITION;

CREATE PRIVATE TEMPORARY TABLE ora$ptt_my_temp_table (
  id           NUMBER,
  description  VARCHAR2(20)
)
ON COMMIT PRESERVE DEFINITION;

CREATE PRIVATE TEMPORARY TABLE ora$ptt_emp AS
SELECT * FROM emp;
