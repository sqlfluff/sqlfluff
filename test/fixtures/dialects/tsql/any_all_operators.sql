-- Test ANY operator with equals
SELECT ProductName
FROM Products
WHERE ProductID = ANY
  (SELECT ProductID
  FROM OrderDetails
  WHERE Quantity > 99);

-- Test ALL operator with equals
SELECT ProductName
FROM Products
WHERE ProductID = ALL
  (SELECT ProductID
  FROM OrderDetails
  WHERE Quantity = 10);

-- Test SOME operator (synonym for ANY) with greater than
SELECT ProductName
FROM Products
WHERE ProductID > SOME
  (SELECT ProductID
  FROM OrderDetails
  WHERE Quantity = 10);

-- Test ALL with less than
SELECT ProductName
FROM Products
WHERE ProductID < ALL
  (SELECT ProductID
  FROM OrderDetails
  WHERE Quantity = 10);

-- Test ANY with greater than or equal
SELECT ProductName
FROM Products
WHERE ProductID >= ANY
  (SELECT ProductID
  FROM OrderDetails
  WHERE Quantity = 10);

-- Test ALL with not equal
SELECT ProductName
FROM Products
WHERE ProductID <> ALL
  (SELECT ProductID
  FROM OrderDetails
  WHERE Quantity = 10);

-- Test SOME with less than or equal
SELECT ProductName
FROM Products
WHERE ProductID <= SOME
  (SELECT ProductID
  FROM OrderDetails);

-- Test in WHERE clause with complex expressions
SELECT *
FROM Orders
WHERE Quantity > ALL (SELECT AVG(Quantity) FROM OrderDetails);

-- Test with multiple ANY/ALL in same query
SELECT ProductName
FROM Products
WHERE ProductID = ANY (SELECT ProductID FROM OrderDetails WHERE Quantity > 10)
  AND Price < ALL (SELECT Price FROM Products WHERE CategoryID = 1);
