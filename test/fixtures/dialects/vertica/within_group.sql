WITH cd AS (SELECT DISTINCT (customer_city) city, customer_state, customer_region FROM customer_dimension)
SELECT customer_region Region, LISTAGG(city||', '||customer_state USING PARAMETERS separator=' | ')
   WITHIN GROUP (ORDER BY city) CityAndState FROM cd GROUP BY region ORDER BY region;
