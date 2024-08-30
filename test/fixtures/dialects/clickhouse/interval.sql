SELECT INTERVAL 1 DAY;
SELECT INTERVAL '1' DAY;
SELECT INTERVAL '1 DAY';
SELECT INTERVAL '1 days' + interval '3 hours' + interval 2 minutes;

SELECT date_add(today(), INTERVAL -30 DAY);

SELECT subDate(toDate('2008-01-02'), INTERVAL 31 DAY);

SELECT addDate(today(), INTERVAL -30 day);

SELECT date_sub(toDate('2018-01-01'), INTERVAL 3 YEAR);

SELECT date_add(toDate('2018-01-01'), INTERVAL 3 YYYY);

SELECT date_add(today(), interval 7 * 4 days);

SELECT
    addDate(today(), INTERVAL col1 DAY)
FROM
    tbl1
;

SELECT
    subDate(today(), INTERVAL col1 + col2 DAY)
FROM
    tbl1
;

SELECT
    formatDateTime(db1.tbl1.col1 + INTERVAL db1.tbl1.col2 + db2_tbl2.col2 DAY, '%F %T')
FROM
    db1.tbl1 left join db2.tbl2 as db2_tbl2 on db1.tbl1.id = db2_tbl2.id
;
