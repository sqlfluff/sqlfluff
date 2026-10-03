SELECT c1:price
FROM VALUES('{ "price": 5 }') AS T(c1);

SELECT c1:['price']::DECIMAL(5, 2)
FROM VALUES('{ "price": 5 }') AS T(c1);

-- JSON path expression accessors.
-- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-json-path-expression
SELECT raw:owner FROM t;

SELECT raw:['owner'] FROM t;

SELECT raw:store.fruit[0] FROM t;

SELECT raw:store.bicycle FROM t;

SELECT raw:['store']['bicycle'] FROM t;

SELECT raw:store.basket[0][2].b FROM t;

SELECT v:field FROM t;

SELECT raw:store.book[*] FROM t;

SELECT raw:[*] FROM t;

SELECT raw:`full name` FROM t;

SELECT raw:`fb:testid` FROM t;
