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

SELECT * FROM
  (SELECT sales, quarter FROM Produce)
  PIVOT(SUM(sales), COUNT(sales) FOR quarter IN ('Q1', 'Q2', 'Q3'));

SELECT
  col1,
  col2
FROM
  table1
  PIVOT(SUM(`grand_total`) FOR REPLACE(LOWER(`media_type`), " ", "_") IN (
    "cinema", "digital", "direct_mail", "door_drops", "outdoor", "press", "radio", "tv"
  ));

SELECT
  col1,
  col2
FROM
  table1
  PIVOT(SUM(`grand_total`) FOR `media_type` IN (
    "cinema", "digital", "direct_mail", "door_drops", "outdoor", "press", "radio", "tv"
  ));

SELECT
  col1,
  col2
FROM
  table1
  PIVOT(SUM(`grand_total`) FOR '2' || '1' IN (
    "cinema", "digital", "direct_mail", "door_drops", "outdoor", "press", "radio", "tv"
  ));
