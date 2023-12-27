SELECT pageid, adid
FROM pageAds
LATERAL VIEW explode(adid_list) adTable AS adid;

SELECT adid, count(1)
FROM pageAds LATERAL VIEW explode(adid_list) adTable AS adid
GROUP BY adid;

SELECT * FROM exampleTable
LATERAL VIEW explode(col1) myTable1 AS myCol1
LATERAL VIEW explode(myCol1) myTable2 AS myCol2;

SELECT myCol1, myCol2 FROM baseTable
LATERAL VIEW explode(col1) myTable1 AS myCol1
LATERAL VIEW explode(col2) myTable2 AS myCol2;

SELECT * FROM src LATERAL VIEW explode(array()) C AS a limit 10;

SELECT * FROM src LATERAL VIEW OUTER explode(array()) C AS a limit 10;

-- besides as a part of LATERAL VIEW, UDTF can also be used in the SELECT expression
SELECT explode(map('A', 10, 'B', 20, 'C', 30)) AS (key,value);

SELECT posexplode(array('A', 'B', 'C')) AS (pos,val);

SELECT inline(array(struct('A', 10, DATE '2015-01-01'), struct('B', 20, DATE '2016-02-02'))) AS (col1,col2,col3);

SELECT stack(2, 'A', 10, DATE '2015-01-01', 'B', 20, DATE '2016-01-01') AS (col0,col1,col2);
