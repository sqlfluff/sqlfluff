SELECT store_region, store_city||', '||store_state location, store_name, number_of_employees
     FROM store.store_dimension WHERE number_of_employees <= 12 ORDER BY store_region, number_of_employees LIMIT 10;

SELECT store_region, store_city||', '||store_state location, store_name, number_of_employees FROM store.store_dimension
     LIMIT 2 OVER (PARTITION BY store_region ORDER BY number_of_employees ASC);
