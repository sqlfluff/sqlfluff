SELECT c1:price
FROM VALUES('{ "price": 5 }') AS T(c1);

SELECT c1:['price']::DECIMAL(5, 2)
FROM VALUES('{ "price": 5 }') AS T(c1);
