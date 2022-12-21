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
