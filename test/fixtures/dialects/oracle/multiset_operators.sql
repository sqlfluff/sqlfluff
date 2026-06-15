-- MULTISET EXCEPT: elements in first table but not in second
SELECT
  customer_id,
  cust_address_ntab
  MULTISET EXCEPT cust_address2_ntab AS multiset_except
FROM customers_demo
ORDER BY customer_id;

-- MULTISET EXCEPT ALL (default)
SELECT
  customer_id,
  cust_address_ntab
  MULTISET EXCEPT ALL cust_address2_ntab AS multiset_except_all
FROM customers_demo
ORDER BY customer_id;

-- MULTISET EXCEPT DISTINCT
SELECT
  customer_id,
  cust_address_ntab
  MULTISET EXCEPT DISTINCT cust_address2_ntab AS multiset_except_distinct
FROM customers_demo
ORDER BY customer_id;

-- MULTISET INTERSECT: elements common to both tables
SELECT
  customer_id,
  cust_address_ntab
  MULTISET INTERSECT cust_address2_ntab AS multiset_intersect
FROM customers_demo
ORDER BY customer_id;

-- MULTISET INTERSECT DISTINCT
SELECT
  customer_id,
  cust_address_ntab
  MULTISET INTERSECT DISTINCT cust_address2_ntab
    AS multiset_intersect_distinct
FROM customers_demo
ORDER BY customer_id;

-- MULTISET UNION: all elements from both tables
SELECT
  customer_id,
  cust_address_ntab
  MULTISET UNION cust_address2_ntab AS multiset_union
FROM customers_demo
ORDER BY customer_id;

-- MULTISET UNION DISTINCT
SELECT
  customer_id,
  cust_address_ntab
  MULTISET UNION DISTINCT cust_address2_ntab AS multiset_union_distinct
FROM customers_demo
ORDER BY customer_id;

-- MULTISET UNION ALL (explicit ALL modifier)
SELECT
  customer_id,
  cust_address_ntab
  MULTISET UNION ALL cust_address2_ntab AS multiset_union_all
FROM customers_demo
ORDER BY customer_id;

-- MULTISET INTERSECT ALL (explicit ALL modifier)
SELECT
  customer_id,
  cust_address_ntab
  MULTISET INTERSECT ALL cust_address2_ntab AS multiset_intersect_all
FROM customers_demo
ORDER BY customer_id;

-- CAST(MULTISET(...) AS type): convert subquery to nested table
UPDATE customers_demo cd
SET cust_address_ntab = CAST(
  MULTISET(
    SELECT c.cust_address
    FROM customers c
    WHERE c.customer_id = cd.customer_id
  ) AS cust_address_tab_typ
);

-- MULTISET EXCEPT in PL/SQL assignment
DECLARE
  TYPE list_of_names_t IS TABLE OF varchar2(100);
  happyfamily list_of_names_t := LIST_OF_NAMES_T();
  children list_of_names_t := LIST_OF_NAMES_T();
  parents list_of_names_t := LIST_OF_NAMES_T();
BEGIN
  parents := happyfamily MULTISET EXCEPT children;
END;
/

-- MULTISET in WHERE clause with IS EMPTY condition
SELECT customer_id
FROM customers_demo
WHERE (cust_address_ntab MULTISET EXCEPT cust_address2_ntab) IS EMPTY;

-- MULTISET in HAVING clause with IS NOT EMPTY
SELECT department_id
FROM order_items_demo
GROUP BY department_id
HAVING (col1_ntab MULTISET INTERSECT col2_ntab) IS NOT EMPTY;

-- MULTISET in UPDATE SET clause
UPDATE order_items_demo
SET col1_ntab = col1_ntab MULTISET UNION col2_ntab
WHERE order_id = 1;

-- MULTISET in PL/SQL IF condition with IS EMPTY
DECLARE
  TYPE list_of_names_t IS TABLE OF varchar2(100);
  a list_of_names_t := LIST_OF_NAMES_T();
  b list_of_names_t := LIST_OF_NAMES_T();
  c list_of_names_t := LIST_OF_NAMES_T();
BEGIN
  IF (a MULTISET EXCEPT b) IS EMPTY THEN
    c := a;
  END IF;
END;
/
