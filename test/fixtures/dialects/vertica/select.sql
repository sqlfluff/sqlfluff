-- https://docs.vertica.com/latest/en/sql-reference/statements/select/
-- Some functionality isn't covered yet, so I commented it

SELECT * FROM T1
   WHERE T1.x IN
      (SELECT MAX(c1) FROM T2
       EXCEPT
          SELECT MAX(cc1) FROM T3
       EXCEPT
          SELECT MAX(d1) FROM T4);

SELECT user_id.id, user_name.name FROM user_name
     JOIN user_id ON user_name.id = user_id.id;

SELECT employee_last_name, SUM(vacation_days)
   FROM employee_dimension
   WHERE employee_last_name ILIKE 'S%'
   GROUP BY employee_last_name;

SELECT employee_last_name, MAX(annual_salary) as highest_salary FROM employee_dimension
     GROUP BY employee_last_name HAVING MAX(annual_salary) > 800000 ORDER BY highest_salary DESC;

SELECT * FROM T1
   WHERE T1.x IN
      (SELECT MAX(c1) FROM T2
       INTERSECT
          SELECT MAX(cc1) FROM T3
       INTERSECT
          SELECT MAX(d1) FROM T4);

-- SELECT * INTO TABLE newTable FROM customer_dimension;

SELECT store_region, store_city||', '||store_state location, store_name, number_of_employees FROM store.store_dimension
     LIMIT 2 OVER (PARTITION BY store_region ORDER BY number_of_employees ASC);

-- SELECT uid,
--        sid,
--        ts,
--        refurl,
--        pageurl,
--        action,
--        event_name(),
--        pattern_id(),
--        match_id()
-- FROM clickstream_log
-- MATCH
--   (PARTITION BY uid, sid ORDER BY ts
--    DEFINE
--      Entry    AS RefURL  NOT ILIKE '%website2.com%' AND PageURL ILIKE '%website2.com%',
--      Onsite   AS PageURL ILIKE     '%website2.com%' AND Action='V',
--      Purchase AS PageURL ILIKE     '%website2.com%' AND Action = 'P'
--    PATTERN
--      P AS (Entry Onsite* Purchase)
--    ROWS MATCH FIRST EVENT);


-- Can't generate yml with this query for some reason
-- SELECT customer_name, customer_gender FROM customer_dimension
--    WHERE occupation='Dancer' AND customer_city = 'San Francisco' ORDER BY customer_name OFFSET 8;

SELECT PolygonPoint(geom) OVER(PARTITION BY geom)
   AS SEL_0 FROM t ORDER BY geog;

SELECT symbol, AVG(first_bid) as avg_bid FROM (
        SELECT symbol, slice_time, TS_FIRST_VALUE(bid1) AS first_bid
        FROM Tickstore
        WHERE symbol IN ('MSFT', 'IBM')
        TIMESERIES slice_time AS '5 seconds' OVER (PARTITION BY symbol ORDER BY ts)
        ) AS resultOfGFI
GROUP BY symbol;

(SELECT id, emp_name FROM company_a ORDER BY emp_name LIMIT 2)
   UNION ALL
   (SELECT id, emp_name FROM company_b ORDER BY emp_name LIMIT 2);

SELECT DISTINCT customer_key, customer_name FROM public.customer_dimension
   WHERE customer_key IN
     (SELECT customer_key FROM store.store_sales_fact WHERE sales_dollar_amount > 500
      UNION ALL
      SELECT customer_key FROM online_sales.online_sales_fact WHERE sales_dollar_amount > 500)
   AND customer_state = 'CT';

SELECT DISTINCT customer_name
   FROM customer_dimension
   WHERE customer_region = 'East'
   AND customer_name ILIKE 'Amer%';
