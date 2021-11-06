SELECT * FROM
  (SELECT * FROM Produce)
  PIVOT(SUM(sales) FOR quarter IN ('Q1', 'Q2', 'Q3', 'Q4'));

SELECT * FROM
  (SELECT sales, quarter FROM Produce)
  PIVOT(SUM(sales) FOR quarter IN ('Q1', 'Q2', 'Q3', 'Q4'));

SELECT * FROM
  (SELECT * FROM Produce)
  PIVOT(SUM(sales) FOR quarter IN ('Q1', 'Q2', 'Q3'));

SELECT * FROM
  (SELECT sales, quarter FROM Produce)
  PIVOT(SUM(sales) FOR quarter IN ('Q1', 'Q2', 'Q3'));
