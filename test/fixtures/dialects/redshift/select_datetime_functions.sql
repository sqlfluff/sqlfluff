SELECT current_date;

SELECT sysdate;

SELECT current_timestamp;

SELECT TRUNC(sysdate);

-- As taken from: https://docs.aws.amazon.com/redshift/latest/dg/r_SYSDATE.html
SELECT salesid, pricepaid, TRUNC(saletime) AS saletime, TRUNC(sysdate) AS now
FROM sales
WHERE saletime BETWEEN TRUNC(sysdate)-120 AND TRUNC(sysdate)
ORDER BY saletime ASC;
